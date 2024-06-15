from uuid import UUID, uuid4

from pydantic import Field

from py_grpcio import Message


class StreamRequest(Message):
    id: UUID = Field(default_factory=uuid4)
    name: str


class StreamResponse(Message):
    id: UUID
    text: str
