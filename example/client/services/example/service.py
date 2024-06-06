from abc import abstractmethod

from py_grpcio import BaseService

from example.client.services.example.models import PingRequest, PingResponse, ComplexRequest, ComplexResponse


class ExampleService(BaseService):
    @abstractmethod
    async def ping(self: 'ExampleService', request: PingRequest) -> PingResponse:
        ...

    @abstractmethod
    async def complex(self: 'ExampleService', request: ComplexRequest) -> ComplexResponse:
        ...
