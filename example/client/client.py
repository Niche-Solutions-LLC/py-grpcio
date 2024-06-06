from uuid import uuid4
from asyncio import run

from loguru import logger

from example.client.services.example import (
    ExampleService, Names,
    PingRequest, PingResponse,
    ComplexModel, ComplexRequest, ComplexResponse
)

service: ExampleService = ExampleService(host='127.0.0.1')


async def main() -> None:
    response: PingResponse = await service.ping(request=PingRequest())
    logger.info(f'ping response: {response}')

    response: ComplexResponse = await service.complex(
        request=ComplexRequest(id=uuid4(), model=ComplexModel(name=Names.NAME_1))
    )
    logger.info(f'complex response: {response}')


if __name__ == '__main__':
    run(main())
