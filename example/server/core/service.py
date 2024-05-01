from abc import abstractmethod

from py_grpcio import BaseService

from example.server.core.models import PingRequest, PingResponse


class BaseExampleService(BaseService):
    @abstractmethod
    async def ping(self: 'BaseExampleService', request: PingRequest) -> PingResponse:
        ...
