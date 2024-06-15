from uuid import uuid4

from typing import Iterator

from example.stream_server.service.base import BaseStreamService
from example.stream_server.service.models import StreamRequest, StreamResponse


class StreamService(BaseStreamService):
    async def stream_in_request(self, requests: Iterator[StreamRequest]) -> StreamResponse:
        return StreamResponse(id=uuid4(), text=f'Hello, {', '.join([request.name for request in requests])}')

    async def stream_in_response(self, request: StreamRequest) -> Iterator[StreamResponse]:
        for i in range(10):
            yield StreamResponse(id=request.id, text=f'Hello, {request.name} | {i}')

    async def stream_in_request_and_response(self, requests: Iterator[StreamRequest]) -> Iterator[StreamResponse]:
        for request in requests:
            yield StreamResponse(id=request.id, text=f'Hello, {request.name}')
