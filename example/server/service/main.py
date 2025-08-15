from example.server.service.base import BaseExampleService
from example.server.service.models import PingRequest, PingResponse, ComplexRequest, ComplexResponse


class ExampleService(BaseExampleService):
    async def ping(self, request: PingRequest) -> PingResponse:
        return PingResponse(id=request.id)

    async def complex(self, request: ComplexRequest) -> ComplexResponse:
        return ComplexResponse(**request.model_dump())
