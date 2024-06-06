from example.bytes_server.service.base import BaseBytesService
from example.bytes_server.service.models import BytesRequest, BytesResponse


class BytesService(BaseBytesService):
    async def test(self, request: BytesRequest) -> BytesResponse:
        return BytesResponse(id=request.id, data=request.data)
