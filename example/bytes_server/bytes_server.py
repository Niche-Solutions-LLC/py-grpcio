from py_grpcio import BaseServer

from example.bytes_server.service import BytesService

if __name__ == '__main__':
    server: BaseServer = BaseServer()
    server.add_service(service=BytesService)
    server.run()
