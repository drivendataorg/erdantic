from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, TYPE_CHECKING

from erdantic.typing import repr_type

if TYPE_CHECKING:
    from erdantic.erd import EntityRelationshipDiagram  # pragma: no cover


_row_template = """<tr><td>{name}</td><td port="{name}">{type_name}</td></tr>"""


class Field(ABC):
    """Abstract base class that holds a field of a data model. Concrete implementations should
    subclass and implement methods.
    """

    @property
    @abstractmethod
    def name(self) -> str:  # pragma: no cover
        """str: Name of this field on the parent data model."""

    @property
    @abstractmethod
    def type_obj(self) -> type:  # pragma: no cover
        """type: Python type object for this field."""
        pass

    @abstractmethod
    def is_many(self) -> bool:  # pragma: no cover
        """Check whether this field represents a one-to-one or one-to-many relationship.

        Returns:
            bool: True if one-to-many relationship, else False.
        """
        pass

    @abstractmethod
    def is_nullable(self) -> bool:  # pragma: no cover
        """Check whether this field is nullable, i.e., can be `None`.

        Returns:
            bool: True if nullable, else False.
        """
        pass

    @abstractmethod
    def __hash__(self) -> int:  # pragma: no cover
        pass

    @property
    def type_name(self) -> str:  # pragma: no cover
        """str: Display name of the Python type object for this field."""
        return repr_type(self.type_obj)

    def dot_row(self) -> str:
        """Returns the DOT language "HTML-like" syntax specification of a row detailing this field
        that is part of a table describing the field's parent data model. It is used as part the
        `label` attribute of data model's node in the graph's DOT representation.

        Returns:
            str: DOT language for table row
        """
        return _row_template.format(name=self.name, type_name=self.type_name)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and hash(self) == hash(other)

    def __repr__(self) -> str:
        return f"<{type(self).__name__}: '{self.name}', {self.type_name}>"


_table_template = """
<<table border="0" cellborder="1" cellspacing="0">
<tr><td port="_root" colspan="2"><b>{name}</b></td></tr>
{rows}
</table>>
"""


class Model(ABC):
    """Abstract base class that holds a data model class, representing a node in our entity
    relationship diagram graph. Concrete implementations should subclass and implement methods.
    """

    @property
    @abstractmethod
    def name(self) -> str:  # pragma: no cover
        """Name of data model."""
        pass

    @property
    @abstractmethod
    def fields(self) -> List[Field]:  # pragma: no cover
        """List of fields this data model contains."""
        pass

    @property
    @abstractmethod
    def docstring(self) -> str:  # pragma: no cover
        """Docstring for this data model."""
        pass

    @abstractmethod
    def __hash__(self):  # pragma: no cover
        pass

    def dot_label(self) -> str:
        """Returns the DOT language "HTML-like" syntax specification of a table for this data
        model. It is used as the `label` attribute of data model's node in the graph's DOT
        representation.

        Returns:
            str: DOT language for table
        """
        rows = "\n".join(field.dot_row() for field in self.fields)
        return _table_template.format(name=self.name, rows=rows).replace("\n", "")

    def __eq__(self, other):
        return isinstance(other, type(self)) and hash(self) == hash(other)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name})"

    def __sort_key__(self) -> str:
        """Key for sorting against other Model instances."""
        return self.name


class DiagramFactory(ABC):
    @staticmethod
    @abstractmethod
    def is_type(model: type) -> bool:  # pragma: no cover
        pass

    @staticmethod
    @abstractmethod
    def create(*models: type) -> "EntityRelationshipDiagram":  # pragma: no cover
        pass


factory_registry: Dict[str, DiagramFactory] = {}


def register_factory(type_name: str) -> Callable[[type], type]:
    def decorator(cls: type) -> type:
        global factory_registry
        if not issubclass(cls, DiagramFactory):
            raise ValueError("Only subclasses of DiagramFactory can be registered.")
        factory_registry[type_name] = cls()  # Verify completeness by instantiating
        return cls

    return decorator
