from asyncio import run

from loguru import logger

from example.bytes_client.services.bytes import BytesService, BytesRequest, BytesResponse


async def test() -> None:
    service: BytesService = BytesService()
    response: BytesResponse = await service.test(
        request=BytesRequest(
            data=[
                {'a': 1, 'b': {1, 2, 3}, 'c': [1, 2, 3]},
                {'x': 2, 'y': 3, 'z': 4}
            ]
        )
    )
    logger.info(response)


if __name__ == '__main__':
    run(test())
