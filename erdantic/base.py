from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Type

from erdantic.typing import repr_type


_row_template = """<tr><td>{name}</td><td port="{name}">{type_name}</td></tr>"""


class Field(ABC):
    """Abstract base class that adapts a field object of a data model class to work with erdantic.
    Concrete implementations should subclass and implement methods.
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
    """Abstract base class that adapts a data model class to work with erdantic. Instances
    representing a node in our entity relationship diagram graph. Concrete implementations should
    subclass and implement methods.
    """

    @abstractmethod
    def __init__(self, model):
        pass

    @staticmethod
    @abstractmethod
    def is_type(obj: Any) -> bool:  # pragma: no cover
        """Check if object is the type of data model class that this model adapter works with."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:  # pragma: no cover
        """Name of this data model."""
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

    @property
    def id(self) -> str:
        """Unique identifier for this Model node."""
        return f"{self.name}__{hash(self)}"

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


model_adapter_registry: Dict[str, Type[Model]] = {}
"""Registry of concrete [`Model`][erdantic.base.model] adapter subclasses. A concrete `Model`
subclass must be registered for it to be available to the diagram creation workflow."""


def register_model_adapter(type_name: str) -> Callable[[type], type]:
    """Create decorator to register a concrete [`Model`][erdantic.base.model] adapter subclass
    that will be identified under the key `type_name`. A concrete `Model` subclass must be
    registered for it to be available to the diagram creation workflow.

    Args:
        type_name (str): Key used to identify concrete `Model` adapter subclass

    Returns:
        Callable[[type], type]: A registration decorator for a concrete `Model` adapter subclass
    """

    def decorator(cls: type) -> type:
        global model_adapter_registry
        if not issubclass(cls, Model):
            raise ValueError("Only subclasses of Model can be registered.")
        model_adapter_registry[type_name] = cls
        return cls

    return decorator
