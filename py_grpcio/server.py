from typing import Type
from pathlib import Path
from types import ModuleType

from asyncio import AbstractEventLoop, get_event_loop

from grpc.aio import server
from grpc.aio._server import Server  # noqa: _server

from grpc_interceptor.server import AsyncServerInterceptor

from py_grpcio.service import BaseService
from py_grpcio.interceptor import ServerInterceptor


class BaseServer:
    def __init__(
        self: 'BaseServer',
        port: int = 50051,
        interceptors: list[AsyncServerInterceptor] | None = None,
        proto_dir: Path = Path('proto')
    ):
        self.port: int = port
        self.interceptors: list = interceptors or []
        self.proto_dir: Path = proto_dir
        self.proto_dir.mkdir(exist_ok=True)

        self.loop: AbstractEventLoop = get_event_loop()

        self.server: Server = server(interceptors=[ServerInterceptor(), *self.interceptors])
        self.server._loop = self.loop

        self.services: dict[str, Type[BaseService]] = {}

        self.__protos: dict[str, ModuleType] = {}
        self.__services: dict[str, ModuleType] = {}

    def add_service(self: 'BaseServer', service: Type[BaseService]):
        self.services[service.name]: Type[BaseService] = service
        service.init_protos_and_services(proto_dir=self.proto_dir)
        self.__protos[service.name], self.__services[service.name] = service.protos, service.services
        getattr(service.services, f'add_{service.name}Servicer_to_server')(servicer=service, server=self.server)

    async def start_server(self: 'BaseServer') -> None:
        await self.server.start()
        await self.server.wait_for_termination()

    def run(self: 'BaseServer') -> None:
        self.server.add_insecure_port(f'[::]:{self.port}')
        try:
            self.loop.run_until_complete(self.start_server())
        finally:
            self.loop.stop()
