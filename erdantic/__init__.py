# from erdantic.refactor.convenience import create, draw, to_dot
import erdantic._logging  # noqa: F401
from erdantic._version import __version__
from erdantic.convenience import create, draw, to_dot
from erdantic.core import EntityRelationshipDiagram
from erdantic.plugins import load_plugins

__version__

__all__ = [
    "create",
    "draw",
    "EntityRelationshipDiagram",
    "to_dot",
]

load_plugins()
