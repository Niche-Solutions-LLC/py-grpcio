from py_grpcio import BaseServer

from service import ExampleService


def main() -> None:
    server: BaseServer = BaseServer()
    server.add_service(service=ExampleService)
    server.run()


if __name__ == '__main__':
    main()
