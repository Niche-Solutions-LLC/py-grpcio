from typing import Type

from loguru import logger

from pydantic import ValidationError

from grpc import StatusCode
from grpc.aio import ServicerContext
from grpc_interceptor.exceptions import GrpcException
from grpc_interceptor.server import AsyncServerInterceptor
from grpc._cython.cygrpc import _MessageReceiver as MessageReceiver  # noqa: _MessageReceiver

from google.protobuf.message import Message

from py_grpcio.method import ServerMethodGRPC
from py_grpcio.exceptions import SendEmpty, RunTimeServerError


class ServerInterceptor(AsyncServerInterceptor):
    @classmethod
    async def intercept_message(
        cls: Type['ServerInterceptor'],
        route: ServerMethodGRPC,
        message: Message,
        context: ServicerContext
    ) -> Message | None:
        response: Message | None = await route(message=message, context=context)
        logger.info(f'{context.peer()} - {route.__qualname__}')
        return response

    @classmethod
    async def intercept_receiver(
        cls: Type['ServerInterceptor'],
        route: ServerMethodGRPC,
        receiver: MessageReceiver,
        context: ServicerContext
    ) -> Message | None:
        async for message in receiver._async_message_receiver():
            print(message)
        return

    async def intercept(
        self: 'ServerInterceptor',
        route: ServerMethodGRPC,
        message_or_receiver: Message | MessageReceiver,
        context: ServicerContext,
        method_name: str,
    ) -> Message | None:
        try:
            match message_or_receiver:
                case Message():
                    return await self.intercept_message(route=route, message=message_or_receiver, context=context)
                case MessageReceiver():
                    return await self.intercept_receiver(route=route, receiver=message_or_receiver, context=context)
                case _:
                    raise 'Aboba'
        except GrpcException as grpc_exc:
            logger.error(
                f'{context.peer()} - {route.__qualname__} | '
                f'{grpc_exc.__class__.__name__} | {grpc_exc.status_code} | {grpc_exc.details}'
            )
            context.set_code(grpc_exc.status_code)
            context.set_details(grpc_exc.details)
        except SendEmpty as exc:
            context.set_code(StatusCode.ABORTED)
            context.set_details(exc.text)
        except RunTimeServerError as exc:
            logger.error(exc)
            context.set_code(exc.status_code)
            context.set_details('Internal Server Error' if exc.status_code == StatusCode.INTERNAL else exc.details)
        except ValidationError as exc:
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details(exc.json())
        except Exception as exc:
            logger.exception(exc)
            context.set_code(StatusCode.INTERNAL)
            context.set_details('Internal Server Error')
