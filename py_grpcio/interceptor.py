from loguru import logger

from pydantic import ValidationError

from grpc import StatusCode
from grpc.aio import ServicerContext
from grpc_interceptor.exceptions import GrpcException
from grpc_interceptor.server import AsyncServerInterceptor

from google.protobuf.message import Message

from py_grpcio.method import ServerMethodGRPC
from py_grpcio.exceptions import RunTimeServerError


class ServerInterceptor(AsyncServerInterceptor):
    async def intercept(
        self: 'ServerInterceptor',
        route: ServerMethodGRPC,
        message: Message,
        context: ServicerContext,
        method_name: str,
    ) -> Message | None:
        try:
            response: Message | None = await route(message=message)
            logger.info(f'{context.peer()} - {route.__qualname__}')
            return response
        except GrpcException as grpc_exc:
            logger.error(
                f'{context.peer()} - {route.__qualname__} | '
                f'{grpc_exc.__class__.__name__} | {grpc_exc.status_code} | {grpc_exc.details}'
            )
            context.set_code(grpc_exc.status_code)
            context.set_details(grpc_exc.details)
        except RunTimeServerError as py_grpc_io_exc:
            logger.error(py_grpc_io_exc)
            context.set_code(py_grpc_io_exc.status_code)
            context.set_details(
                'Internal Server Error'
                if py_grpc_io_exc.status_code == StatusCode.INTERNAL else py_grpc_io_exc.details
            )
        except ValidationError as exc:
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details(exc.json())
        except Exception as exc:
            logger.exception(exc)
            context.set_code(StatusCode.INTERNAL)
            context.set_details('Internal Server Error')
