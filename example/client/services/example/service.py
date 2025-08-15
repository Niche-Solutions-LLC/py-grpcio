from abc import ABC, abstractmethod

from py_grpcio import BaseService

from example.client.services.example.models import PingRequest, PingResponse, ComplexRequest, ComplexResponse


class ExampleService(BaseService, ABC):
    @abstractmethod
    async def ping(self, request: PingRequest) -> PingResponse:
        ...

    @abstractmethod
    async def complex(self, request: ComplexRequest) -> ComplexResponse:
        ...
