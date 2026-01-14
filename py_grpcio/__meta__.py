from typing import Final
from pathlib import Path
from importlib.metadata import version

__package_name__: Final[str] = __package__
__version__: Final[str] = version(__package_name__)
__module_path__: Final[Path] = Path(__file__).parent
