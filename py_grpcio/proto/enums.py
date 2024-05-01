from enum import StrEnum


class ProtoBufTypes(StrEnum):
    DOUBLE: str = 'double'
    FLOAT: str = 'float'
    INT32: str = 'int32'
    INT64: str = 'int64'
    UINT32: str = 'uint32'
    UINT64: str = 'uint64'
    SINT32: str = 'sint32'
    SINT64: str = 'sint64'
    FIXED32: str = 'fixed32'
    FIXED64: str = 'fixed64'
    SFIXED32: str = 'sfixed32'
    SFIXED64: str = 'sfixed64'
    BOOL: str = 'bool'
    STRING: str = 'string'
    BYTES: str = 'bytes'
    MAP: str = 'map'
