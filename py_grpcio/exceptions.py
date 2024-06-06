from typing import Any

from grpc import StatusCode


class PyGrpcIOException(Exception):
    def __init__(self, text: str):
        self.text: str = text

    def __str__(self) -> str:
        return f'{self.__class__.__name__} | {self.text}'

    __repr__ = __str__


class MethodSignatureException(PyGrpcIOException):
    ...


class SendEmpty(PyGrpcIOException):
    ...


class RunTimeServerError(PyGrpcIOException):
    def __init__(self, status_code: StatusCode = StatusCode.INTERNAL, details: Any = 'Internal Server Error'):
        self.status_code: StatusCode = status_code
        self.details: Any = details
        super().__init__(text=f'status_code: {status_code} | details: {details}')
