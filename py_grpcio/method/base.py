from typing import Any, Type, Callable, Iterator

from google.protobuf.message import Message as ProtoMessage

from py_grpcio.models import Method, Message

from py_grpcio.proto.enums import ProtoBufTypes

type Delay = float
type ServiceType = type
type MethodType = Callable[[ProtoMessage, str, bool], ProtoMessage]
type StreamMethodType = Callable[[Iterator[ProtoMessage], str, bool], ProtoMessage]


class BaseMethodGRPC:
    def __init__(self: 'BaseMethodGRPC', method: Method):
        self.method: Method = method

    def __getattr__(self: 'BaseMethodGRPC', attr_name: str) -> Any:
        return getattr(self.method.target.func, attr_name)

    @classmethod
    def proto_to_pydantic(
        cls: Type['BaseMethodGRPC'],
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
        cls: Type['BaseMethodGRPC'],
        message: Message,
        model: Type[ProtoMessage],
        method: Method,
        warnings: bool = False,
        exclude_types: set[ProtoBufTypes | str] | None = None
    ) -> ProtoMessage:
        exclude_types: set[ProtoBufTypes | str] = exclude_types or {ProtoBufTypes.BYTES}
        exclude: set[str] = {field.name for field in message.fields() if field.type in exclude_types}
        dump: dict[str, Any] = message.model_dump(mode='json', warnings=warnings, exclude=exclude)
        params: dict[str, Any] = {}
        for field_name, field_info in message.model_fields.items():
            if field_info.annotation.__name__ in method.additional_messages:
                value: ProtoMessage = cls.pydantic_to_proto(
                    message=getattr(message, field_name),
                    model=method.get_additional_proto(proto_name=field_info.annotation.__name__),
                    method=method,
                    warnings=warnings,
                    exclude_types=exclude_types
                )
            elif field_info.annotation is bytes:
                value: bytes = getattr(message, field_name)
            else:
                value: Any = dump[field_name]
            params[field_name] = value
        return model(**params)  # noqa: args, kwargs

    @classmethod
    def pydantic_to_bytes(cls: Type['BaseMethodGRPC'], message: Message, method: Method) -> ProtoMessage:
        message_type: Type[ProtoMessage] = method.get_additional_proto(proto_name='BytesMessage')
        return message_type(bytes=message.model_dump_json().encode())  # noqa: bytes

    @classmethod
    def bytes_to_pydantic(cls: Type['BaseMethodGRPC'], message: ProtoMessage, model: Type[Message]) -> Message:
        return model.model_validate_json(json_data=getattr(message, 'bytes').decode())
