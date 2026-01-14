from abc import ABC, abstractmethod

from py_grpcio import BaseService

from example.bytes_server.service.models import BytesRequest, BytesResponse


class BaseBytesService(BaseService, ABC, mode='bytes'):
    @abstractmethod
    async def test(self, request: BytesRequest) -> BytesResponse:
        ...
