from typing import Type, Callable, Iterator, assert_never

from asyncio import to_thread
from warnings import catch_warnings

from grpc import experimental

from google.protobuf.message import Message as ProtoMessage

from py_grpcio.enums import ServiceModes
from py_grpcio.utils import snake_to_camel
from py_grpcio.models import Method, Message

from py_grpcio.method.base import BaseMethodGRPC, Delay, ServiceType, MethodType, StreamMethodType


class ClientMethodGRPC(BaseMethodGRPC):
    def __init__(
        self: 'ClientMethodGRPC',
        method: Method,
        service_name: str,
        host: str,
        port: int = 50051,
        timeout_delay: Delay = 1
    ):
        super().__init__(method=method)
        self.method: Method = method
        self.service_name: str = service_name
        self.host: str = host
        self.port: int = port
        self.timeout_delay: Delay = timeout_delay

    @property
    def service(self: 'ClientMethodGRPC') -> ServiceType:
        return getattr(self.method.services, f'{self.service_name}')

    @classmethod
    async def call_grpc_method(cls: Type['ClientMethodGRPC'], method: MethodType, **kwargs) -> ProtoMessage:
        with catch_warnings(action='ignore', category=experimental.ExperimentalApiWarning):
            return await to_thread(method, **kwargs)

    async def default_call(self: 'ClientMethodGRPC', grpc_method: MethodType, request: Message) -> Message | None:
        proto_request: ProtoMessage = self.pydantic_to_proto(
            message=request,
            model=self.method.proto_request,
            method=self.method
        )
        proto_response: ProtoMessage = await self.call_grpc_method(
            method=grpc_method,
            request=proto_request,
            target=f'{self.host}:{self.port}',
            insecure=True,
            timeout=self.timeout_delay
        )
        return self.proto_to_pydantic(message=proto_response, model=self.method.response, method=self.method)

    async def bytes_call(self: 'ClientMethodGRPC', grpc_method: MethodType, request: Message) -> Message | None:
        proto_request: ProtoMessage = self.pydantic_to_bytes(message=request, method=self.method)
        proto_response: ProtoMessage = await self.call_grpc_method(
            method=grpc_method,
            request=proto_request,
            target=f'{self.host}:{self.port}',
            insecure=True,
            timeout=self.timeout_delay
        )
        return self.bytes_to_pydantic(message=proto_response, model=self.method.validation_response)

    async def streamig_call(self: 'ClientMethodGRPC', grpc_method: StreamMethodType, requests: Iterator[Message]):
        proto_requests: Iterator[ProtoMessage] = iter(
            [
                self.pydantic_to_proto(
                    message=request,
                    model=self.method.proto_request,
                    method=self.method
                )
                for request in requests
            ]
        )
        # response = grpc_method(request_iterator=proto_requests, target=f'{self.host}:{self.port}', insecure=True)
        # print(response)

    async def __streaming_call__(self: 'ClientMethodGRPC', requests: Iterator[Message]) -> Message | None:
        print(requests, isinstance(requests, Iterator))
        grpc_method: StreamMethodType = getattr(self.service, snake_to_camel(self.method.target.func.__name__))
        from inspect import signature
        print(signature(grpc_method).parameters)
        await self.streamig_call(grpc_method=grpc_method, requests=requests)
        return

    async def __call__(self: 'ClientMethodGRPC', request: Message) -> Message | None:
        grpc_method: MethodType = getattr(self.service, snake_to_camel(self.method.target.func.__name__))
        match self.method.mode:
            case ServiceModes.DEFAULT:
                return await self.default_call(grpc_method=grpc_method, request=request)
            case ServiceModes.BYTES:
                return await self.bytes_call(grpc_method=grpc_method, request=request)
            case _:
                return assert_never(self.method.mode)
