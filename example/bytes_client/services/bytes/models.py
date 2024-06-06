from typing import Any
from uuid import UUID, uuid4

from pydantic import Field

from py_grpcio import Message


class BytesRequest(Message):
    id: UUID = Field(default_factory=uuid4)
    data: list[dict[str, Any]]


class BytesResponse(Message):
    id: UUID
    data: list[dict[str, Any]]
