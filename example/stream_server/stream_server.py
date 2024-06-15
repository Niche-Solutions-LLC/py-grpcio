from py_grpcio import BaseServer

from example.stream_server.service import StreamService

if __name__ == '__main__':
    server: BaseServer = BaseServer()
    server.add_service(service=StreamService)
    server.run()
