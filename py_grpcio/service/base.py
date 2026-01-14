from typing import Any
from pathlib import Path

from py_grpcio.models import Method
from py_grpcio.method import ClientMethodGRPC
from py_grpcio.service.meta import BaseServiceMeta

try:
    from __meta__ import __src_path__
except ImportError:
    __src_path__: Path = Path()

DEFAULT_PROTO_DIR: Path = __src_path__ / 'proto'

type Delay = float
type ServiceType = BaseService


class BaseService(metaclass=BaseServiceMeta):
    def __init__(
        self: ServiceType,
        host: str = 'localhost',
        port: int = 50051,
        proto_dir: Path = DEFAULT_PROTO_DIR,
        timeout_delay: Delay = 1
    ):
        self.host: str = host
        self.port: int = port
        self.proto_dir: Path = proto_dir
        self.proto_dir.mkdir(exist_ok=True)
        self.timeout_delay: Delay = timeout_delay
        self.__class__.init_protos_and_services(proto_dir=self.proto_dir)

    def __getattribute__(self: ServiceType, attr_name: str) -> ClientMethodGRPC | Any:
        methods: dict[str, Method] = super().__getattribute__('methods')
        if method := methods.get(attr_name):
            return ClientMethodGRPC(
                method=method,
                service_name=self.name,
                host=self.host,
                port=self.port,
                timeout_delay=self.timeout_delay
            )
        return super().__getattribute__(attr_name)
