import erdantic.dataclasses  # noqa: F401
from erdantic.erd import EntityRelationshipDiagram, create, draw, to_dot
import erdantic.pydantic  # noqa: F401
import erdantic.pydantic1  # noqa: F401
from erdantic.version import __version__

__version__

__all__ = [
    "create",
    "draw",
    "EntityRelationshipDiagram",
    "to_dot",
]
