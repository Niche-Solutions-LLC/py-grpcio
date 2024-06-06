# <p align="center">Pydantic & gRPC</p>

[**py-grpcio**](https://pypi.org/project/py-grpcio/) is a microframework and high-level wrapper of 
[**grpcio**](https://pypi.org/project/grpcio/) to simplify work with the original library using abstractions, 
useful python objects and [**pydantic**](https://pypi.org/project/pydantic/) models.

Examples of use are given below and also duplicated in the 
[**example**](https://github.com/Niche-Solutions-LLC/py-grpcio/tree/main/example) directory.

---

## Install latest

```shell
pip install py-grpcio
```


---

## Example

### Models

**Pydantic** models that describe messages for client-server interaction.

```python
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import Field

from py_grpcio import Message

from example.server.service.enums import Names


class PingRequest(Message):
    id: UUID = Field(default_factory=uuid4)


class PingResponse(Message):
    id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)


class ComplexModel(Message):
    name: Names


class ComplexRequest(Message):
    id: UUID
    model: ComplexModel


class ComplexResponse(Message):
    id: UUID
    model: ComplexModel

```

---

### Server

Basic implementation of **gRPC** services on the server side.

You need to describe the service abstractly and duplicate this service on the client side.

```python
from abc import abstractmethod

from py_grpcio import BaseService

from example.server.service.models import PingRequest, PingResponse, ComplexRequest, ComplexResponse


class BaseExampleService(BaseService):
    @abstractmethod
    async def ping(self: 'BaseExampleService', request: PingRequest) -> PingResponse:
        ...

    @abstractmethod
    async def complex(self: 'BaseExampleService', request: ComplexRequest) -> ComplexResponse:
        ...

```

---

Full implementation of the **gRPC** service with methods.

```python
from example.server.service.base import BaseExampleService
from example.server.service.models import PingRequest, PingResponse, ComplexRequest, ComplexResponse


class ExampleService(BaseExampleService):
    async def ping(self: 'ExampleService', request: PingRequest) -> PingResponse:
        return PingResponse(id=request.id)

    async def complex(self: 'BaseExampleService', request: ComplexRequest) -> ComplexResponse:
        return ComplexResponse(**request.model_dump())

```

---

Run the ExampleService on Server.

```python
from py_grpcio import BaseServer

from example.server.service import ExampleService


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

from example.server.service.models import PingRequest, PingResponse, ComplexRequest, ComplexResponse


class ExampleService(BaseService):
    @abstractmethod
    async def ping(self: 'ExampleService', request: PingRequest) -> PingResponse:
        ...

    @abstractmethod
    async def complex(self: 'ExampleService', request: ComplexRequest) -> ComplexResponse:
        ...

```

---

Calling the ExampleService endpoints by Client.

```python
from uuid import uuid4
from asyncio import run

from loguru import logger

from example.client.services.example import (
    ExampleService, PingRequest, PingResponse, ComplexModel, ComplexRequest, ComplexResponse, Names
)

service: ExampleService = ExampleService(host='127.0.0.1')


async def main() -> None:
    response: PingResponse = await service.ping(request=PingRequest())
    logger.info(f'ping response: {response}')

    response: ComplexResponse = await service.complex(
        request=ComplexRequest(id=uuid4(), model=ComplexModel(name=Names.NAME_1))
    )
    logger.info(f'complex response: {response}')


if __name__ == '__main__':
    run(main())

```

---

### Notes

* You can use the library on the client side even if the server is implemented differently 
by simply describing it as an abstract service

* The client can also be implemented using other libraries, the server that uses `py-grpcio` 
will still be able to accept such requests