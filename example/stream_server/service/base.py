from typing import Iterator
from abc import abstractmethod

from py_grpcio import BaseService

from example.stream_server.service.models import StreamRequest, StreamResponse


class BaseStreamService(BaseService):
    @abstractmethod
    async def stream_in_request(self, requests: Iterator[StreamRequest]) -> StreamResponse:
        ...

    @abstractmethod
    async def stream_in_response(self, request: StreamRequest) -> Iterator[StreamResponse]:
        ...

    @abstractmethod
    async def stream_in_request_and_response(self, requests: Iterator[StreamRequest]) -> Iterator[StreamResponse]:
        ...
