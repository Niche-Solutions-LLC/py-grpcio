from py_grpcio import BaseServer

from example.server.service import ExampleService


if __name__ == '__main__':
    server: BaseServer = BaseServer()
    server.add_service(service=ExampleService)
    server.run()
