from typing import Any
from inspect import get_annotations
from abc import ABC, abstractmethod

from grpc.aio import ServicerContext

from py_grpcio.models import Message, Target

type MiddlewareType = BaseMiddleware


class BaseMiddleware(ABC):
    def __init__(self, target: MiddlewareType | Target):
        self.target: MiddlewareType | Target = target

    def get_kwargs(self, request: Message, context: ServicerContext) -> dict[str, Any]:
        if isinstance(self.target, BaseMiddleware):
            return {'request': request, 'context': context}
        kwargs: dict[str, Any] = {}
        if 'request' in get_annotations(self.target.func):
            kwargs['request']: Message = request
        if 'context' in get_annotations(self.target.func):
            kwargs['context']: ServicerContext = context
        return kwargs

    async def call_target(self, request: Message, context: ServicerContext) -> Message:
        return await self.target(**self.get_kwargs(request=request, context=context))

    @abstractmethod
    async def __call__(self, request: Message, context: ServicerContext) -> Message:
        return await self.call_target(request=request, context=context)

    func = __call__
