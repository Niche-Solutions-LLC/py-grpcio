from inspect import isclass
from functools import partial
from typing_extensions import Annotated
from types import FunctionType, ModuleType, GenericAlias
from typing import Type, Any, TypeVar, Iterable, get_origin, assert_never

from pydantic import BaseModel, ConfigDict, Field as PyField, create_model
from pydantic.fields import FieldInfo  # noqa: FieldInfo
from pydantic_core.core_schema import CoreSchema, no_info_wrap_validator_function, str_schema, to_string_ser_schema

from google.protobuf.message import Message as ProtoMessage

from py_grpcio.enums import ServiceModes
from py_grpcio.exceptions import MethodSignatureException
from py_grpcio.proto import ProtoBufTypes, parse_field_type

Target: 'Target' = TypeVar('Target', bound=partial)


class Field(BaseModel):
    name: str
    type: ProtoBufTypes | str
    repeated: bool = False
    map_key: str | None = None
    map_value: str | None = None

    @classmethod
    def from_field_info(cls: Type['Field'], field_name: str, field_info: FieldInfo) -> 'Field':
        return cls(**parse_field_type(field_name=field_name, field_type=field_info.annotation))


class Message(BaseModel):
    @classmethod
    def fields(cls: Type['Message']) -> list[Field]:
        return [
            Field.from_field_info(field_name=field_name, field_info=field_info)
            for field_name, field_info in cls.model_fields.items()
        ]

    @classmethod
    def get_additional_messages(
        cls, model_fields: dict[str, FieldInfo] | None = None
    ) -> dict[str, Type['Message']]:
        messages: dict[str, Type[Message]] = {}
        for field_name, field_info in (cls.model_fields if model_fields is None else model_fields).items():
            field_type: type | None = field_info.annotation
            if isclass(field_type) and issubclass(field_type, Message):
                messages[field_type.__name__]: Type[Message] = field_type
                if additional_messages := cls.get_additional_messages(model_fields=field_type.model_fields):
                    messages.update(**additional_messages)
            elif isinstance(field_type, GenericAlias) and (origin := get_origin(tp=field_type)) is not None:
                if issubclass(origin, Iterable):
                    if len(args := field_type.__args__) != 1:
                        raise TypeError(
                            f'Field `{field_name}`: type `{field_type}` must have only one subtype, not {len(args)}.'
                        )
                    if isclass(sub_field_type := args[0]) and issubclass(sub_field_type, Message):
                        messages[sub_field_type.__name__]: Type[Message] = sub_field_type
                        if additional_messages := cls.get_additional_messages(model_fields=sub_field_type.model_fields):
                            messages.update(**additional_messages)
        return messages


BytesMessage: Type['BytesMessage'] = create_model('BytesMessage', bytes=(bytes, ...), __base__=Message)


class ModuleTypePydanticAnnotation:
    @classmethod
    def validate_object_id(cls: Type['ModuleTypePydanticAnnotation'], value: Any, _) -> ModuleType:
        if isinstance(value, ModuleType):
            return value

    @classmethod
    def __get_pydantic_core_schema__(cls: Type['ModuleTypePydanticAnnotation'], source_type: type, _) -> CoreSchema:
        assert source_type is ModuleType
        return no_info_wrap_validator_function(
            cls.validate_object_id,
            str_schema(),
            serialization=to_string_ser_schema(),
        )


class Method(BaseModel):
    mode: ServiceModes
    request: Type[Message]
    response: Type[Message]
    validation_request: Type[Message]
    validation_response: Type[Message]
    target: Target
    protos: Annotated[ModuleType, ModuleTypePydanticAnnotation] | None = None
    services: Annotated[ModuleType, ModuleTypePydanticAnnotation] | None = None
    additional_messages: dict[str, Type[Message]] = PyField(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_target(cls, target: FunctionType, mode: ServiceModes = ServiceModes.DEFAULT) -> 'Method':
        annotations: dict[str, Any] = target.__annotations__
        if not (requst_message := annotations.get('request')) or not issubclass(requst_message, Message):
            raise MethodSignatureException(
                text=f'Method `{target.__qualname__}` must receive a request parameter of type subclass `Message`'
            )
        if not (response_message := annotations.get('return')) or not issubclass(response_message, Message):
            raise MethodSignatureException(
                text=f'The `{target.__qualname__}` method should return an object of type subclass `Message`'
            )
        return cls(
            mode=mode,
            target=partial(target, self=target.__class__),
            request=BytesMessage if mode is ServiceModes.BYTES else requst_message,
            response=BytesMessage if mode is ServiceModes.BYTES else response_message,
            validation_request=requst_message,
            validation_response=response_message
        )

    @property
    def default_messages(self: 'Method') -> dict[str, Type[Message]]:
        self.additional_messages.update(self.request.get_additional_messages())
        self.additional_messages.update(self.response.get_additional_messages())
        return {
            **self.additional_messages,
            self.request.__name__: self.request,
            self.response.__name__: self.response,
        }

    @property
    def bytes_messages(self: 'Method') -> dict[str, Type[Message]]:
        return {'BytesMessage': BytesMessage}

    @property
    def messages(self: 'Method') -> dict[str, Type[Message]]:
        match self.mode:
            case ServiceModes.DEFAULT:
                return self.default_messages
            case ServiceModes.BYTES:
                return self.bytes_messages
            case _:
                return assert_never(self.mode)

    @property
    def proto_request(self: 'Method') -> Type[ProtoMessage] | None:
        return getattr(self.protos, self.request.__name__)

    @property
    def proto_response(self: 'Method') -> Type[ProtoMessage] | None:
        return getattr(self.protos, self.response.__name__)

    def get_additional_proto(self: 'Method', proto_name: str) -> Type[ProtoMessage] | None:
        return getattr(self.protos, proto_name)

    def get_additional_message(self: 'Method', message_name: str) -> Type[Message] | None:
        return self.additional_messages.get(message_name)
