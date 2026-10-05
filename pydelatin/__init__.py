"""Top-level package for pydelatin."""

from importlib.metadata import PackageNotFoundError, version

from . import util
from .delatin import Delatin

try:
    __version__ = version("pydelatin")
except PackageNotFoundError:
    __version__ = "uninstalled"

__all__ = ["Delatin", "__version__", "util"]
