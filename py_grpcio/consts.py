from sys import path
from pathlib import Path

try:
    from __meta__ import __src_path__
except ImportError:
    __src_path__: Path = Path()

DEFAULT_PROTO_DIR: Path = __src_path__.relative_to(path[0]) / 'proto'
