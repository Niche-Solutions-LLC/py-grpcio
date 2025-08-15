from pathlib import Path

from types import ModuleType
from typing import Callable, Awaitable

from asyncio import AbstractEventLoop, set_event_loop, new_event_loop

from loguru import logger

from grpc.aio import server
from grpc.aio._server import Server  # noqa: _server

from py_grpcio.service import BaseService
from py_grpcio.middleware import BaseMiddleware
from py_grpcio.interceptor import ServerInterceptor

type ServerType = BaseServer

type LifespanFunc = Callable[[ServerType], Awaitable[None]]


class BaseServer:
    def __init__(
        self,
        port: int = 50051,
        proto_dir: Path = Path('proto'),
        middlewares: set[type[BaseMiddleware]] | None = None,
        on_startup: LifespanFunc | None = None,
        on_shutdown: LifespanFunc | None = None,
        loop: AbstractEventLoop | None = None,
        loop_factory: Callable[..., AbstractEventLoop] = new_event_loop,
    ):
        self.port: int = port
        self.proto_dir: Path = proto_dir
        self.proto_dir.mkdir(exist_ok=True)

        self.loop: AbstractEventLoop = loop or loop_factory()
        set_event_loop(self.loop)

        self.server: Server = server(interceptors=[ServerInterceptor()])
        self.server._loop = self.loop

        self.services: dict[str, type[BaseService]] = {}

        self.__protos: dict[str, ModuleType] = {}
        self.__services: dict[str, ModuleType] = {}
        self.middlewares: set[type[BaseMiddleware]] = middlewares or set()

        self.on_startup: LifespanFunc | None = on_startup
        self.on_shutdown: LifespanFunc | None = on_shutdown

    def add_service(self, service: type[BaseService]) -> None:
        self.services[service.name]: type[BaseService] = service
        service.set_middlewares(middlewares=self.middlewares)
        service.init_protos_and_services(proto_dir=self.proto_dir)
        self.__protos[service.name], self.__services[service.name] = service.protos, service.services
        getattr(service.services, f'add_{service.name}Servicer_to_server')(servicer=service, server=self.server)

    async def start_server(self) -> None:
        await self.server.start()
        logger.info('Server has been launched!')
        await self.server.wait_for_termination()

    def run(self) -> None:
        self.server.add_insecure_port(address=f'[::]:{self.port}')
        try:
            logger.info('Server starts up...')
            if self.on_startup:
                self.loop.run_until_complete(future=self.on_startup(self))
            self.loop.run_until_complete(future=self.start_server())
        except KeyboardInterrupt:
            ...
        finally:
            if self.on_shutdown:
                self.loop.run_until_complete(future=self.on_shutdown(self))
            logger.info('Server is stopped!')
            self.loop.stop()
