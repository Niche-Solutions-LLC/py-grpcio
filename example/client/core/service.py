from abc import abstractmethod

from py_grpcio import BaseService

from example.client.core.models import PingRequest, PingResponse


class ExampleService(BaseService):
    @abstractmethod
    async def ping(self: 'ExampleService', request: PingRequest) -> PingResponse:
        ...
