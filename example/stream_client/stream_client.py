from asyncio import run
from typing import Iterator

from loguru import logger

from example.stream_client.services.stream import StreamService, StreamRequest, StreamResponse


async def test_stream() -> None:
    service: StreamService = StreamService()
    requests: Iterator[StreamRequest] = iter(
        [
            StreamRequest(name='A'),
            StreamRequest(name='B'),
            StreamRequest(name='C'),
            StreamRequest(name='D'),
            StreamRequest(name='E'),
        ]
    )
    await service.stream_in_request(requests=requests)
    logger.info(service)


if __name__ == '__main__':
    run(test_stream())
