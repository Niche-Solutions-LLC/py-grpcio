from pathlib import Path

from types import ModuleType
from typing import Any, Type

from jinja2 import Environment, FileSystemLoader, Template

from grpc import protos_and_services

from py_grpcio.models import Message, Method
from py_grpcio.method import ServerMethodGRPC
from py_grpcio.utils import is_method, camel_to_snake, snake_to_camel

environment: Environment = Environment(
    loader=FileSystemLoader(searchpath=Path(__file__).parent / 'proto/templates'),
    trim_blocks=True
)


class BaseServiceMeta(type):
    def __init__(cls: 'BaseServiceMeta', name: str, *args):
        super().__init__(name, *args)
        cls.name: str = name
        cls.methods: dict[str, Method] = {}
        cls.messages: dict[str, Type[Message]] = {}
        cls.protos: ModuleType | None = None
        cls.services: ModuleType | None = None

    def __getattr__(cls: 'BaseServiceMeta', attr_name: str) -> ServerMethodGRPC | Any:
        if method := cls.methods.get(camel_to_snake(string=attr_name)):
            return ServerMethodGRPC(method=method)
        return getattr(cls, attr_name)

    def methods_and_messages(cls: 'BaseServiceMeta') -> None:
        for method_name, target in cls.__dict__.items():
            if is_method(method=target):
                method: Method = Method.from_target(target=target)
                cls.methods[method_name]: Method = method
                cls.messages.update(method.messages)

    def get_proto(cls: 'BaseServiceMeta') -> str:
        cls.methods_and_messages()
        template: Template = environment.get_template(name='service.proto.template')
        return template.render(
            service=cls,
            camel_to_snake=camel_to_snake,
            snake_to_camel=snake_to_camel
        )

    def gen_proto(cls: 'BaseServiceMeta', proto_dir: Path) -> Path:
        path: Path = proto_dir / f'{camel_to_snake(string=cls.name)}.proto'
        path.write_text(data=cls.get_proto())
        return path

    def get_method(cls: 'BaseServiceMeta', method_name: str) -> ServerMethodGRPC:
        return ServerMethodGRPC(method=getattr(cls, method_name))

    def init_protos_and_services(cls: 'BaseServiceMeta', proto_dir: Path) -> None:
        cls.protos, cls.services = protos_and_services(protobuf_path=str(cls.gen_proto(proto_dir=proto_dir)))
        for method in cls.methods.values():
            method.protos, method.services = cls.protos, cls.services
