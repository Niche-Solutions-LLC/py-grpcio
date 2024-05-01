from asyncio import run

from loguru import logger

from example.client.core import ExampleService, PingRequest, PingResponse

service: ExampleService = ExampleService(host='127.0.0.1')


async def call_ping() -> None:
    response: PingResponse = await service.ping(request=PingRequest())
    logger.info(f'response: {response}')


if __name__ == '__main__':
    run(call_ping())
