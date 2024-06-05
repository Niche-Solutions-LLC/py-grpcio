from abc import abstractmethod

from py_grpcio import BaseService

from service.models import PingRequest, PingResponse, ComplexRequest, ComplexResponse


class BaseExampleService(BaseService):
    @abstractmethod
    async def ping(self: 'BaseExampleService', request: PingRequest) -> PingResponse:
        ...

    @abstractmethod
    async def complex(self: 'BaseExampleService', request: ComplexRequest) -> ComplexResponse:
        ...
