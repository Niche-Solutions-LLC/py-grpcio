from pathlib import Path

from types import ModuleType
from typing import Any, Type, TypedDict, Unpack, NotRequired

from jinja2 import Environment, FileSystemLoader, Template

from grpc import protos_and_services

from py_grpcio.__meta__ import __module_path__

from py_grpcio.enums import ServiceModes
from py_grpcio.models import Message, Method
from py_grpcio.method import ServerMethodGRPC
from py_grpcio.middleware import BaseMiddleware

from py_grpcio.utils import is_method, camel_to_snake, snake_to_camel

environment: Environment = Environment(
    loader=FileSystemLoader(searchpath=__module_path__ / 'proto/templates'),
    trim_blocks=True
)


class ExtraKwargs(TypedDict):
    mode: NotRequired[ServiceModes]


class BaseServiceMeta(type):
    def __new__(
        cls: Type['BaseServiceMeta'],
        name: str,
        bases: tuple[Type['BaseServiceMeta'], ...],
        class_dict: dict[str, Any],
        **extra: Unpack[ExtraKwargs]
    ) -> 'BaseServiceMeta':
        class_dict.update(extra)
        class_dict['__extra__']: ExtraKwargs = extra
        for base in bases:
            class_dict.update(base.__extra__)
        return super().__new__(cls, name, bases, class_dict)

    def __init__(
        cls: 'BaseServiceMeta',
        name: str,
        bases: tuple,
        class_dict: dict[str, Any],
        **extra: Unpack[ExtraKwargs],
    ):
        super().__init__(name, bases, class_dict)
        cls.name: str = name
        cls.mode: ServiceModes = extra.get('mode') or class_dict.get('mode', ServiceModes.DEFAULT)
        cls.methods: dict[str, Method] = {}
        cls.messages: dict[str, Type[Message]] = {}
        cls.protos: ModuleType | None = None
        cls.services: ModuleType | None = None
        cls.middlewares: set[Type[BaseMiddleware]] = set()

    def __getattr__(self: 'BaseServiceMeta', attr_name: str) -> ServerMethodGRPC | Any:
        if method := self.methods.get(camel_to_snake(string=attr_name)):
            server_method_grpc: ServerMethodGRPC = ServerMethodGRPC(method=method, middlewares=self.middlewares)
            if method.request_streaming:
                return server_method_grpc.__streaming_call__
            return server_method_grpc
        return getattr(self, attr_name)

    def set_middlewares(self: 'BaseServiceMeta', middlewares: set[Type[BaseMiddleware]]) -> None:
        self.middlewares: set[Type[BaseMiddleware]] = middlewares

    def methods_and_messages(self: 'BaseServiceMeta') -> None:
        for method_name, target in self.__dict__.items():
            if is_method(method=target):
                method: Method = Method.from_target(target=target, mode=self.mode)
                self.methods[method_name]: Method = method
                self.messages.update(method.messages)

    def get_proto(self: 'BaseServiceMeta') -> str:
        self.methods_and_messages()
        template: Template = environment.get_template(name='service.proto.template')
        return template.render(
            service=self,
            camel_to_snake=camel_to_snake,
            snake_to_camel=snake_to_camel
        )

    def gen_proto(self: 'BaseServiceMeta', proto_dir: Path) -> Path:
        path: Path = proto_dir / f'{camel_to_snake(string=self.name)}.proto'
        path.write_text(data=self.get_proto())
        return path

    def init_protos_and_services(self: 'BaseServiceMeta', proto_dir: Path) -> None:
        self.protos, self.services = protos_and_services(protobuf_path=str(self.gen_proto(proto_dir=proto_dir)))
        for method in self.methods.values():
            method.protos, method.services = self.protos, self.services
