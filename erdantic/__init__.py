import erdantic._logging  # noqa: F401
from erdantic._version import __version__
from erdantic.convenience import create, draw, to_dot
from erdantic.core import EntityRelationshipDiagram
from erdantic.diff import compare_diagrams
from erdantic.plugins import list_plugins
from erdantic.plugins import load_plugins as _load_plugins

__version__

__all__ = [
    "EntityRelationshipDiagram",
    "compare_diagrams",
    "create",
    "draw",
    "list_plugins",
    "to_dot",
]

_load_plugins()
