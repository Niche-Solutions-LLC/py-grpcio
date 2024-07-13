from typing import Type, assert_never

from pydantic import ValidationError

from grpc.aio import ServicerContext

from google.protobuf.message import Message as ProtoMessage

from py_grpcio.enums import ServiceModes
from py_grpcio.models import Target, Method, Message
from py_grpcio.exceptions import SendEmpty, RunTimeServerError

from py_grpcio.middleware import BaseMiddleware
from py_grpcio.method.base import BaseMethodGRPC


class ServerMethodGRPC(BaseMethodGRPC):
    def __init__(self, method: Method, middlewares: set[Type[BaseMiddleware]]):
        super().__init__(method=method)
        self.middlewares: set[Type[BaseMiddleware]] = middlewares

        self.target: Target = self.method.target
        self.wrapped_target: BaseMiddleware | None = None
        self.wrap_target()

    def wrap_target(self) -> None:
        for middleware in self.middlewares:
            self.wrapped_target = middleware(target=self.wrapped_target or self.target)

    async def call_target(self, request: Message, context: ServicerContext) -> Message:
        if self.wrapped_target:
            response: Message | None = await self.wrapped_target(request=request, context=context)
        else:
            response: Message | None = await self.target(request=request)
        if not response:
            raise SendEmpty(text='Method did not return anything')
        return response

    async def default_call(
        self: 'ServerMethodGRPC',
        message: ProtoMessage,
        context: ServicerContext
    ) -> ProtoMessage | None:
        request: Message = self.proto_to_pydantic(
            message=message,
            model=self.method.validation_request,
            method=self.method
        )
        try:
            response: Message = await self.call_target(request=request, context=context)
            return self.pydantic_to_proto(message=response, model=self.method.proto_response, method=self.method)
        except ValidationError as exc:
            raise RunTimeServerError(details={'validation_error': exc.json()})

    async def bytes_call(
        self: 'ServerMethodGRPC',
        message: ProtoMessage,
        context: ServicerContext
    ) -> ProtoMessage | None:
        request: Message = self.bytes_to_pydantic(message=message, model=self.method.validation_request)
        try:
            response: Message = await self.call_target(request=request, context=context)
            return self.pydantic_to_bytes(message=response, method=self.method)
        except ValidationError as exc:
            raise RunTimeServerError(details={'validation_error': exc.json()})

    async def __call__(
        self: 'ServerMethodGRPC',
        message: ProtoMessage,
        context: ServicerContext
    ) -> ProtoMessage | None:
        match self.method.mode:
            case ServiceModes.DEFAULT:
                return await self.default_call(message=message, context=context)
            case ServiceModes.BYTES:
                return await self.bytes_call(message=message, context=context)
            case _:
                return assert_never(self.method.mode)
