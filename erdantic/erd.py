import os
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Union

import pygraphviz as pgv

from erdantic.errors import MissingCreateError, UnknownModelTypeError

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
    def type_name(self) -> str:  # pragma: no cover
        """str: Display name of the Python type object for this field."""

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
        """str: Name of data model."""
        pass

    @property
    @abstractmethod
    def fields(self) -> List[Field]:  # pragma: no cover
        """List[Field]: List of fields this data model contains."""
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


class Edge:
    """Class for an edge in the entity relationship diagram graph. Represents the composition
    relationship from between a composite model (`source` via `source_field`) to component model
    (`target`).

    Attributes:
        source (Model): Composite data model.
        source_field (Field): Field on `source` that has type of `target.
        target (Model): Component data model.
    """

    source: Model
    source_field: Field
    target: Model

    def __init__(self, source: Model, source_field: Field, target: Model):
        if source_field not in set(source.fields):
            raise ValueError("source_field is not a field of source")
        self.source = source
        self.source_field = source_field
        self.target = target

    def dot_arrowhead(self) -> str:
        """Arrow shape specification in Graphviz DOT language for this edge's head. See
        [Graphviz docs](https://graphviz.org/doc/info/arrows.html) as a reference. Shape returned
        is based on [crow's foot notation](https://www.calebcurry.com/cardinality-and-modality/)
        for the relationship's cardinality and modality.

        Returns:
            str: DOT language specification for arrow shape of this edge's head
        """
        cardinality = "crow" if self.source_field.is_many() else "nonetee"
        modality = (
            "odot" if self.source_field.is_nullable() or self.source_field.is_many() else "tee"
        )
        return cardinality + modality

    def __hash__(self) -> int:
        return hash((self.source, self.source_field, self.target))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and hash(self) == hash(other)

    def __repr__(self) -> str:
        return (
            f"Edge(source={repr(self.source)}, source_field={self.source_field}, "
            f"target={self.target})"
        )


class EntityRelationshipDiagram:
    """Class for entity relationship diagram.

    Attributes:
        models (List[Model]): Data models (nodes) in diagram.
        attr2 (List[Edge]): Edges in diagram, representing the composition relationship between
            models.
    """

    models: List[Model]
    edges: List[Edge]

    def __init__(self, models: List[Model], edges: List[Edge]):
        self.models = models
        self.edges = edges

    def draw(self, out: Union[str, os.PathLike], **kwargs):
        """Render entity relationship diagram for given data model classes to file.

        Args:
            out (Union[str, os.PathLike]): Output file path for rendered diagram.
            **kwargs: Additional keyword arguments to [`pygraphviz.AGraph.draw`](https://pygraphviz.github.io/documentation/latest/reference/agraph.html#pygraphviz.AGraph.draw).
        """
        self.graph().draw(out, prog="dot", **kwargs)

    def graph(self) -> pgv.AGraph:
        """Return [`pygraphviz.AGraph`](https://pygraphviz.github.io/documentation/latest/reference/agraph.html)
        instance for diagram.

        Returns:
            pgv.AGraph: graph object for diagram
        """
        g = pgv.AGraph(directed=True, strict=False, nodesep=0.5, ranksep=1.5, rankdir="LR")
        g.node_attr["shape"] = "plain"
        for model in self.models:
            g.add_node(model.name, label=model.dot_label())
        for edge in self.edges:
            g.add_edge(
                edge.source.name,
                edge.target.name,
                tailport=f"{edge.source_field.name}:e",
                headport="_root:w",
                arrowhead=edge.dot_arrowhead(),
            )
        return g

    def to_dot(self) -> str:
        """Generate Graphviz [DOT language](https://graphviz.org/doc/info/lang.html) representation
        of entity relationship diagram for given data model classes.

        Returns:
            str: DOT language representation of diagram
        """
        return self.graph().string()

    def __repr__(self) -> str:
        models = ", ".join(repr(m) for m in self.models)
        edges = ", ".join(repr(e) for e in self.edges)
        return f"EntityRelationshipDiagram(models=[{models}], edges=[{edges}])"

    def _repr_svg_(self):
        graph = self.graph()
        return graph.draw(prog="dot", format="svg").decode(graph.encoding)


implementation_registry: Dict[str, Dict[str, Callable]] = {}
"""Dict[str, Dict[str, Callable]]: Registry of erdantic implementations for automatic dispatching.
Structure is `{key: {"type_checker": checker_func, "constructor": constructor_func}}` where `key`
is a string identifier for a given data model class type, and checker_func and constructor_func are
used to determine applicability to a data model class and to construct an
[`EntityRelationshipDiagram`][erdantic.erd.EntityRelationshipDiagram] instance, respectively
"""


def register_type_checker(key: str) -> Callable[[Callable], Callable]:
    """Create decorator to register a checker function whose purpose will be to determine if a
    given data model class belongs to the category for `key`.

    Args:
        key (str): Key for category of model type to register checker function for.

    Returns:
        Callable[Callable, Callable]: Decorator for `key`
    """

    def decorator(fcn: Callable) -> Callable:
        global implementation_registry
        if key not in implementation_registry:
            implementation_registry[key] = {}
        implementation_registry[key]["type_checker"] = fcn
        return fcn

    return decorator


def register_constructor(key: str) -> Callable[[Callable], Callable]:
    """Create decorator to register a constructor function that will be used to create an
    [`EntityRelationshipDiagram`][erdantic.erd.EntityRelationshipDiagram] instance from given data
    model classes of type `key`.

    Args:
        key (str): Key for category of model type to register constructor function for.

    Returns:
        Callable[Callable, Callable]: Decorator for `key`
    """

    def decorator(fcn: Callable) -> Callable:
        global implementation_registry
        if key not in implementation_registry:
            implementation_registry[key] = {}
        implementation_registry[key]["constructor"] = fcn
        return fcn

    return decorator


def create(*models: type) -> EntityRelationshipDiagram:
    """Construct [`EntityRelationshipDiagram`][erdantic.erd.EntityRelationshipDiagram] from given
    data model classes.

    Raises:
        UnknownModelTypeError: If model is not recognized as a supported model type.
        MissingCreateError: If model is recognized as a supported, type but a registered `create`
            function is missing for that type.

    Returns:
        EntityRelationshipDiagram: diagram object for given data model.
    """

    key = None
    for k, impl in implementation_registry.items():
        if impl["type_checker"](models[0]):
            key = k
    if key is None:
        raise UnknownModelTypeError(
            f"Given data model class with MRO {models[0].__mro__} is not supported."
        )

    if "constructor" not in implementation_registry[key]:
        raise MissingCreateError(
            f"Implementation for {key} is missing a diagram constuctor function."
        )
    constructor = implementation_registry[key]["constructor"]
    return constructor(*models)


def draw(*models: type, out: Union[str, os.PathLike], **kwargs):
    """Render entity relationship diagram for given data model classes to file.

    Args:
        *models (type): Data model classes to diagram.
        out (Union[str, os.PathLike]): Output file path for rendered diagram.
        **kwargs: Additional keyword arguments to [`pygraphviz.AGraph.draw`](https://pygraphviz.github.io/documentation/latest/reference/agraph.html#pygraphviz.AGraph.draw).
    """
    diagram = create(*models)
    diagram.draw(out=out, **kwargs)


def to_dot(*models: type) -> str:
    """Generate Graphviz [DOT language](https://graphviz.org/doc/info/lang.html) representation of
    entity relationship diagram for given data model classes.

    Args:
        *models (type): Data model classes to diagram.

    Returns:
        str: DOT language representation of diagram
    """
    diagram = create(*models)
    return diagram.to_dot()
