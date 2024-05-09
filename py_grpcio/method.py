from asyncio import to_thread
from warnings import catch_warnings
from typing import Any, Type, Callable

from pydantic import ValidationError

from grpc import experimental

from google.protobuf.message import Message as ProtoMessage

from py_grpcio.utils import snake_to_camel
from py_grpcio.models import Method, Message
from py_grpcio.exceptions import RunTimeServerError

type Service = type
type MethodType = Callable[[ProtoMessage, str, bool], ProtoMessage]


class MethodGRPC:
    def __init__(self: 'MethodGRPC', method: Method):
        self.method: Method = method

    def __getattr__(self: 'MethodGRPC', attr_name: str) -> Any:
        return getattr(self.method.target, attr_name)

    @classmethod
    def proto_to_pydantic(
        cls: Type['MethodGRPC'],
        message: ProtoMessage,
        model: Type[Message],
        method: Method
    ) -> Message:
        params: dict[str, Any] = {}
        for descriptor, value in message.ListFields():
            if isinstance(value, ProtoMessage):
                value: Message = cls.proto_to_pydantic(
                    message=value,
                    model=method.get_additional_message(message_name=descriptor.message_type.name),
                    method=method
                )
            params[descriptor.name]: Any = value
        return model(**params)

    @classmethod
    def pydantic_to_proto(
        cls: Type['MethodGRPC'],
        message: Message,
        model: Type[ProtoMessage],
        method: Method
    ) -> ProtoMessage:
        dump: dict[str, Any] = message.model_dump(mode='json')
        params: dict[str, Any] = {}
        for field_name, field_info in message.model_fields.items():
            if field_info.annotation.__name__ in method.additional_messages:
                value: ProtoMessage = cls.pydantic_to_proto(
                    message=getattr(message, field_name),
                    model=method.get_additional_proto(proto_name=field_info.annotation.__name__),
                    method=method
                )
            else:
                value: Any = dump[field_name]
            params[field_name] = value
        return model(**params)  # noqa: args, kwargs


class ServerMethodGRPC(MethodGRPC):
    async def __call__(self: 'ServerMethodGRPC', message: ProtoMessage) -> ProtoMessage | None:
        request: Message = self.proto_to_pydantic(message=message, model=self.method.request, method=self.method)
        try:
            response: Message = await self.method.target(self=self, request=request)
            return self.pydantic_to_proto(message=response, model=self.method.proto_response, method=self.method)
        except ValidationError as exc:
            raise RunTimeServerError(details={'validation_error': exc.json()})


class ClientMethodGRPC(MethodGRPC):
    def __init__(self: 'ClientMethodGRPC', method: Method, service_name: str, host: str, port: int = 50051):
        super().__init__(method=method)
        self.method: Method = method
        self.service_name: str = service_name
        self.host: str = host
        self.port: int = port

    @property
    def service(self: 'ClientMethodGRPC') -> Service:
        return getattr(self.method.services, f'{self.service_name}')

    @classmethod
    async def call_grpc_method(cls: Type['ClientMethodGRPC'], method: MethodType, **kwargs) -> ProtoMessage:
        with catch_warnings(action='ignore', category=experimental.ExperimentalApiWarning):
            return await to_thread(method, **kwargs)

    async def __call__(self: 'ClientMethodGRPC', request: Message) -> Message | None:
        proto_request: ProtoMessage = self.pydantic_to_proto(
            message=request,
            model=self.method.proto_request,
            method=self.method
        )
        method: Callable = getattr(self.service, snake_to_camel(self.method.target.__name__))
        proto_response: ProtoMessage = await self.call_grpc_method(
            method=method,
            request=proto_request,
            target=f'{self.host}:{self.port}',
            insecure=True
        )
        return self.proto_to_pydantic(message=proto_response, model=self.method.response, method=self.method)
