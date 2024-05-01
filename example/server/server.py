from example.server.core import BaseExampleService, PingRequest, PingResponse

from py_grpcio import BaseServer


class ExampleService(BaseExampleService):
    async def ping(self: 'ExampleService', request: PingRequest) -> PingResponse:
        return PingResponse(id=request.id)


if __name__ == '__main__':
    server: BaseServer = BaseServer()
    server.add_service(service=ExampleService)
    server.run()
