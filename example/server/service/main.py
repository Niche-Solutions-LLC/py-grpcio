from example.server.service.base import BaseExampleService
from example.server.service.models import PingRequest, PingResponse, ComplexRequest, ComplexResponse


class ExampleService(BaseExampleService):
    async def ping(self: 'ExampleService', request: PingRequest) -> PingResponse:
        return PingResponse(id=request.id)

    async def complex(self: 'BaseExampleService', request: ComplexRequest) -> ComplexResponse:
        return ComplexResponse(**request.model_dump())
