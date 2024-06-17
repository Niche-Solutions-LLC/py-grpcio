from pathlib import Path
from typing import Any, Callable

from py_grpcio import Message
from py_grpcio.models import Method
from py_grpcio.method import ClientMethodGRPC
from py_grpcio.service.meta import BaseServiceMeta

type Delay = float


class BaseService(metaclass=BaseServiceMeta):
    def __init__(
        self: 'BaseService',
        host='localhost',
        port: int = 50051,
        proto_dir: Path = Path('proto'),
        timeout_delay: Delay = 1
    ):
        self.host: str = host
        self.port: int = port
        self.proto_dir: Path = proto_dir
        self.proto_dir.mkdir(exist_ok=True)
        self.timeout_delay: Delay = timeout_delay
        self.__class__.init_protos_and_services(proto_dir=self.proto_dir)

    def __getattribute__(
        self: 'BaseService', attr_name: str
    ) -> ClientMethodGRPC | Callable[[Message], Message | None] | Any:
        methods: dict[str, Method] = super().__getattribute__('methods')
        if method := methods.get(attr_name):
            client_method_grpc: ClientMethodGRPC = ClientMethodGRPC(
                method=method,
                service_name=self.name,
                host=self.host,
                port=self.port,
                timeout_delay=self.timeout_delay
            )
            if method.request_streaming:
                return client_method_grpc.__streaming_call__
            return client_method_grpc
        return super().__getattribute__(attr_name)
