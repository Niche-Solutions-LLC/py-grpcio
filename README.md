# <p align="center">Pydantic & gRPC</p>

`py-grpcio` is a microframework and high-level wrapper of [**grpcio**](https://pypi.org/project/grpcio/) to simplify 
work with the original library using abstractions, 
useful python objects and [**pydantic**](https://pypi.org/project/pydantic/) models.

Examples of use are given below and also duplicated in the [**example**](example) directory.

---

## Example

### Models

**Pydantic** models that describe messages for client-server interaction.

```python
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import Field

from py_grpcio import Message


class PingRequest(Message):
    id: UUID = Field(default_factory=uuid4)


class PingResponse(Message):
    id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
```

---

### Server

Basic implementation of **gRPC** services on the server side.

You need to describe the service abstractly and duplicate this service on the client side.


```python
from abc import abstractmethod

from py_grpcio import BaseService

from example.server.core.models import PingRequest, PingResponse


class BaseExampleService(BaseService):
    @abstractmethod
    async def ping(self, request: PingRequest) -> PingResponse:
        ...
```

---

Full implementation of the **gRPC** service with methods.

```python
from example.server.core import BaseExampleService, PingRequest, PingResponse

from py_grpcio import BaseServer


class ExampleService(BaseExampleService):
    async def ping(self, request: PingRequest) -> PingResponse:
        return PingResponse(id=request.id)


if __name__ == '__main__':
    server: BaseServer = BaseServer()
    server.add_service(service=ExampleService)
    server.run()
```

---

Note that on the client side, this class must be named the same as it is named in the full server-side implementation.

That is, if on the server we call the base class as `BaseExampleService` and the class with the implementation of 
methods as `ExampleService`, then on the client side the abstract service should be called `ExampleService`.


### Client

```python
from abc import abstractmethod

from py_grpcio import BaseService

from example.client.core.models import PingRequest, PingResponse


class ExampleService(BaseService):
    @abstractmethod
    async def ping(self, request: PingRequest) -> PingResponse:
        ...

```

---

### Notes

* You can use the library on the client side even if the server is implemented differently 
by simply describing it as an abstract service

* The client can also be implemented using other libraries, the server that uses `py-grpcio` 
will still be able to accept such requests