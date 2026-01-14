from enum import StrEnum
from typing import Literal

type ServiceModesType = Literal[ServiceModes.BYTES, ServiceModes.DEFAULT]


class ServiceModes(StrEnum):
    DEFAULT = 'default'
    BYTES = 'bytes'
