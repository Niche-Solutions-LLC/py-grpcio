from uuid import UUID, uuid4
from datetime import datetime

from pydantic import Field

from py_grpcio import Message


class PingRequest(Message):
    id: UUID = Field(default_factory=uuid4)


class PingResponse(Message):
    id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
