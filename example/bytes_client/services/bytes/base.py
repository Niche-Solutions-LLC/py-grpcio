from abc import ABC, abstractmethod

from py_grpcio import BaseService, ServiceModes

from example.bytes_client.services.bytes.models import BytesRequest, BytesResponse


class BytesService(BaseService, ABC, mode=ServiceModes.BYTES):
    @abstractmethod
    async def test(self, request: BytesRequest) -> BytesResponse:
        ...
