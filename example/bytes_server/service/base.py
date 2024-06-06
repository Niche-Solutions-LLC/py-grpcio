from abc import abstractmethod

from py_grpcio import BaseService, ServiceModes

from example.bytes_server.service.models import BytesRequest, BytesResponse


class BaseBytesService(BaseService, mode=ServiceModes.BYTES):
    @abstractmethod
    async def test(self, request: BytesRequest) -> BytesResponse:
        ...
