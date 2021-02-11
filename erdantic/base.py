from abc import ABC, abstractmethod
import inspect
from typing import Any, Callable, Dict, Generic, List, Type, TypeVar, Union

from erdantic.typing import Final, GenericAlias, repr_type, repr_type_with_mro


_row_template = """<tr><td>{name}</td><td port="{name}">{type_name}</td></tr>"""


FT = TypeVar("FT", bound=Any, covariant=True)
"""Covariant type variable for a field object adapted by adapter class
[`Field`][erdantic.base.Field]."""


class Field(ABC, Generic[FT]):
    """Abstract base class that adapts a field object of a data model class to work with erdantic.
    Concrete implementations should subclass and implement abstract methods.

    Attributes:
        field (FT): Field object on a data model class associated with this adapter
    """

    @abstractmethod
    def __init__(self, field: FT):
        """Initialize Field adapter instance.

        Args:
            field: Field object to associate with this adapter instance
        """
        self.field: Final[FT] = field

    @property
    @abstractmethod
    def name(self) -> str:  # pragma: no cover
        """Name of this field on the parent data model."""

    @property
    @abstractmethod
    def type_obj(self) -> Union[type, GenericAlias]:
        """Python type object for this field."""
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

    @property
    def type_name(self) -> str:  # pragma: no cover
        """String representation of the Python type annotation for this field."""
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

    def __hash__(self) -> int:
        return id(self.field)

    def __repr__(self) -> str:
        return f"<{type(self).__name__}: '{self.name}', {self.type_name}>"


_table_template = """
<<table border="0" cellborder="1" cellspacing="0">
<tr><td port="_root" colspan="2"><b>{name}</b></td></tr>
{rows}
</table>>
"""


MT = TypeVar("MT", bound=type, covariant=True)
"""Covariant type variable for a data model class adapted by adapter class
[`Model`][erdantic.base.Model]. Bounded by `type`."""


class Model(ABC, Generic[MT]):
    """Abstract base class that adapts a data model class to work with erdantic. Instances
    represent a node in our entity relationship diagram graph. Concrete implementations should
    subclass and implement abstract methods.

    Attributes:
        model (MT): Data model class associated with this adapter
    """

    @abstractmethod
    def __init__(self, model: MT):
        """Initialize model adapter instance.

        Args:
            model: Data model class to associate with this adapter instance
        """
        self.model: Final[MT] = model

    @property
    @abstractmethod
    def fields(self) -> List[Field]:  # pragma: no cover
        """List of fields defined on this data model."""
        pass

    @staticmethod
    @abstractmethod
    def is_model_type(obj: Any) -> bool:  # pragma: no cover
        """Check if object is the type of data model class that this model adapter works with."""
        pass

    @property
    def name(self) -> str:  # pragma: no cover
        """Name of this data model."""
        return self.model.__name__

    @property
    def docstring(self) -> str:
        """Docstring for this data model."""
        out = f"{self.model.__module__}.{self.model.__qualname__}"
        docstring = inspect.getdoc(self.model)
        if docstring:
            out += "\n\n" + docstring
        return out

    @property
    def key(self) -> str:
        """Human-readable unique identifier for this data model. Should be stable across
        sessions."""
        return f"{self.model.__module__}.{self.model.__qualname__}"

    def dot_label(self) -> str:
        """Returns the DOT language "HTML-like" syntax specification of a table for this data
        model. It is used as the `label` attribute of data model's node in the graph's DOT
        representation.

        Returns:
            str: DOT language for table
        """
        rows = "\n".join(field.dot_row() for field in self.fields)
        return _table_template.format(name=self.name, rows=rows).replace("\n", "")

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and hash(self) == hash(other)

    def __hash__(self) -> int:
        return hash(self.key)

    def __lt__(self, other) -> bool:
        if not isinstance(other, Model):
            raise ValueError(
                f"Can only compare between instances of Model. Given: {repr_type_with_mro(other)}"
            )
        return self.key < other.key

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name})"


model_adapter_registry: Dict[str, Type[Model]] = {}
"""Registry of concrete [`Model`][erdantic.base.Model] adapter subclasses. A concrete `Model`
subclass must be registered for it to be available to the diagram creation workflow."""


def register_model_adapter(type_name: str) -> Callable[[Type[Model]], Type[Model]]:
    """Create decorator to register a concrete [`Model`][erdantic.base.Model] adapter subclass
    that will be identified under the key `type_name`. A concrete `Model` subclass must be
    registered for it to be available to the diagram creation workflow.

    Args:
        type_name (str): Key used to identify concrete `Model` adapter subclass

    Returns:
        Callable[[Type[Model]], Type[Model]]: A registration decorator for a concrete `Model`
            adapter subclass
    """

    def decorator(cls: type) -> type:
        global model_adapter_registry
        if not issubclass(cls, Model):
            raise ValueError("Only subclasses of Model can be registered.")
        model_adapter_registry[type_name] = cls
        return cls

    return decorator
