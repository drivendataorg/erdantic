from operator import methodcaller
import os
from typing import Any, List, Tuple, Union, TYPE_CHECKING

import pygraphviz as pgv

from erdantic.base import factory_registry
from erdantic.errors import ModelTypeMismatchError, UnknownModelTypeError
from erdantic.version import __version__

if TYPE_CHECKING:
    from erdantic.base import Field, Model  # pragma: no cover


class Edge:
    """Class for an edge in the entity relationship diagram graph. Represents the composition
    relationship between a composite model (`source` via `source_field`) with a component model
    (`target`).

    Attributes:
        source (Model): Composite data model.
        source_field (Field): Field on `source` that has type of `target.
        target (Model): Component data model.
    """

    source: "Model"
    source_field: "Field"
    target: "Model"

    def __init__(self, source: "Model", source_field: "Field", target: "Model"):
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

    def __sort_key__(self) -> Tuple[str, int]:
        """Key for sorting against other Edge instances."""
        return (self.source.name, self.source.fields.index(self.source_field))


class EntityRelationshipDiagram:
    """Class for entity relationship diagram.

    Attributes:
        models (List[Model]): Data models (nodes) in diagram.
        attr2 (List[Edge]): Edges in diagram, representing the composition relationship between
            models.
    """

    models: List["Model"]
    edges: List["Edge"]

    def __init__(self, models: List["Model"], edges: List["Edge"]):
        self.models = sorted(models, key=methodcaller("__sort_key__"))
        self.edges = sorted(edges, key=methodcaller("__sort_key__"))

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
        g = pgv.AGraph(
            directed=True,
            strict=False,
            nodesep=0.5,
            ranksep=1.5,
            rankdir="LR",
            name="Entity Relationship Diagram",
            label=f"Created by erdantic v{__version__} <https://github.com/drivendataorg/erdantic>",
            fontsize=9,
            fontcolor="gray66",
        )
        g.node_attr["fontsize"] = 14
        g.node_attr["shape"] = "plain"
        for model in self.models:
            g.add_node(model.name, label=model.dot_label(), tooltip=model.docstring)
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

    def __hash__(self) -> int:
        return hash((tuple(self.models), tuple(self.edges)))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and hash(self) == hash(other)

    def __repr__(self) -> str:
        models = ", ".join(repr(m) for m in self.models)
        edges = ", ".join(repr(e) for e in self.edges)
        return f"EntityRelationshipDiagram(models=[{models}], edges=[{edges}])"

    def _repr_png_(self) -> bytes:
        graph = self.graph()
        return graph.draw(prog="dot", format="png")

    def _repr_svg_(self) -> str:
        graph = self.graph()
        return graph.draw(prog="dot", format="svg").decode(graph.encoding)


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
    for type_name, factory in factory_registry.items():
        if factory.is_type(models[0]):
            # Validate additional models
            for addl in models[1:]:
                if not factory.is_type(addl):
                    raise ModelTypeMismatchError(
                        mismatched_model=addl, first_model=models[0], expected=type_name
                    )
            return factory.create(*models)
    raise UnknownModelTypeError(model=models[0])


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
