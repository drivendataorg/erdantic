import inspect
import os
from types import ModuleType
from typing import Any, Iterable, Iterator, List, Optional, Sequence, Set, Type, Union

import pygraphviz as pgv

from erdantic.base import Field, get_model_adapter, Model, model_adapter_registry
from erdantic.exceptions import (
    NotATypeError,
    _StringForwardRefError,
    StringForwardRefError,
    _UnevaluatedForwardRefError,
    UnevaluatedForwardRefError,
    UnknownFieldError,
    UnknownModelTypeError,
)
from erdantic.typing import get_recursive_args
from erdantic.version import __version__


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
            raise UnknownFieldError(
                f"source_field {source_field} is not a field of source {source}"
            )
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

    def __lt__(self, other) -> bool:
        if isinstance(other, Edge):
            self_key = (self.source, self.source.fields.index(self.source_field), self.target)
            other_key = (other.source, other.source.fields.index(other.source_field), other.target)
            return self_key < other_key
        return NotImplemented


class EntityRelationshipDiagram:
    """Class for entity relationship diagram.

    Attributes:
        models (List[Model]): Data models (nodes) in diagram.
        attr2 (List[Edge]): Edges in diagram, representing the composition relationship between
            models.
    """

    models: List["Model"]
    edges: List["Edge"]

    def __init__(self, models: Sequence["Model"], edges: Sequence["Edge"]):
        self.models = sorted(models)
        self.edges = sorted(edges)

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
            pygraphviz.AGraph: graph object for diagram
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
            g.add_node(
                model.key,
                label=model.dot_label(),
                tooltip=model.docstring.replace("\n", "&#xA;"),
            )
        for edge in self.edges:
            g.add_edge(
                edge.source.key,
                edge.target.key,
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


def create(
    *models_or_modules: Union[type, ModuleType],
    termini: Sequence[type] = [],
    limit_search_models_to: Optional[Iterable[str]] = None,
) -> EntityRelationshipDiagram:
    """Construct [`EntityRelationshipDiagram`][erdantic.erd.EntityRelationshipDiagram] from given
    data model classes.

    Args:
        *models_or_modules (type): Data model classes to diagram or modules containing them.
        termini (Sequence[type]): Data model classes to set as terminal nodes. erdantic will stop
            searching for component classes when it reaches these models
        limit_search_models_to (Optional[Iterable[sr]], optional): Iterable of identifiers of data
            model classes that erdantic supports. If any are specified, when searching a module,
            limit data model classes to those ones. Defaults to None which will find all data model
            classes supported by erdantic.
    Raises:
        UnknownModelTypeError: If model is not recognized as a supported model type.

    Returns:
        EntityRelationshipDiagram: diagram object for given data model.
    """
    models = []
    for mm in models_or_modules:
        if isinstance(mm, type):
            models.append(mm)
        elif isinstance(mm, ModuleType):
            models.extend(find_models(mm, limit_search_models_to=limit_search_models_to))
        else:
            raise NotATypeError(f"Given model is not a type: {mm}")
    for terminal_model in tuple(termini):
        if not isinstance(terminal_model, type):
            raise NotATypeError(f"Given terminal model is not a type: {terminal_model}")

    seen_models: Set[Model] = {adapt_model(t) for t in termini}
    seen_edges: Set[Edge] = set()
    for raw_model in models:
        model = adapt_model(raw_model)
        search_composition_graph(model=model, seen_models=seen_models, seen_edges=seen_edges)
    return EntityRelationshipDiagram(models=list(seen_models), edges=list(seen_edges))


def find_models(
    module: ModuleType, limit_search_models_to: Optional[Iterable[str]] = None
) -> Iterator[type]:
    """Searches a module and yields all data model classes found.

    Args:
        module (ModuleType): Module to search for data model classes
        limit_search_models_to (Optional[Iterable[sr]], optional): Iterable of identifiers of data
            model classes that erdantic supports. If any are specified, when searching a module,
            limit data model classes to those ones. Defaults to None which will find all data model
            classes supported by erdantic.

    Yields:
        Iterator[type]: Members of module that are data model classes.
    """
    limit_search_models_to_adapters: Iterable[Type[Model]]
    if limit_search_models_to is None:
        limit_search_models_to_adapters = model_adapter_registry.values()
    else:
        limit_search_models_to_adapters = [get_model_adapter(m) for m in limit_search_models_to]

    for _, member in inspect.getmembers(module, inspect.isclass):
        if member.__module__ == module.__name__:
            for model_adapter in limit_search_models_to_adapters:
                if model_adapter.is_model_type(member):
                    yield member


def adapt_model(obj: Any) -> Model:
    """Dispatch object to appropriate concrete [`Model`][erdantic.base.Model] adapter subclass and
    return instantiated adapter instance.

    Args:
        obj (Any): Data model class to adapt

    Raises:
        UnknownModelTypeError: If obj does not match registered Model adapter classes

    Returns:
        Model: Instantiated concrete `Model` subclass instance
    """
    for model_adapter in model_adapter_registry.values():
        if model_adapter.is_model_type(obj):
            return model_adapter(obj)
    raise UnknownModelTypeError(model=obj)


def search_composition_graph(
    model: Model,
    seen_models: Set[Model],
    seen_edges: Set[Edge],
):
    """Recursively search composition graph for a model, where nodes are models and edges are
    composition relationships between models. Nodes and edges that are discovered will be added to
    the two respective provided set instances.

    Args:
        model (Model): Root node to begin search.
        seen_models (Set[Model]): Set instance that visited nodes will be added to.
        seen_edges (Set[Edge]): Set instance that traversed edges will be added to.
    """
    if model not in seen_models:
        seen_models.add(model)
        for field in model.fields:
            try:
                for arg in get_recursive_args(field.type_obj):
                    try:
                        field_model = adapt_model(arg)
                        seen_edges.add(Edge(source=model, source_field=field, target=field_model))
                        search_composition_graph(field_model, seen_models, seen_edges)
                    except UnknownModelTypeError:
                        pass
            except _UnevaluatedForwardRefError as e:
                raise UnevaluatedForwardRefError(
                    model=model, field=field, forward_ref=e.forward_ref
                ) from None
            except _StringForwardRefError as e:
                raise StringForwardRefError(
                    model=model, field=field, forward_ref=e.forward_ref
                ) from None


def draw(
    *models_or_modules: Union[type, ModuleType],
    out: Union[str, os.PathLike],
    termini: Sequence[type] = [],
    limit_search_models_to: Optional[Iterable[str]] = None,
    **kwargs,
):
    """Render entity relationship diagram for given data model classes to file.

    Args:
        *models_or_modules (type): Data model classes to diagram, or modules containing them.
        out (Union[str, os.PathLike]): Output file path for rendered diagram.
        termini (Sequence[type]): Data model classes to set as terminal nodes. erdantic will stop
            searching for component classes when it reaches these models
        limit_search_models_to (Optional[Iterable[sr]], optional): Iterable of identifiers of data
            model classes that erdantic supports. If any are specified, when searching a module,
            limit data model classes to those ones. Defaults to None which will find all data model
            classes supported by erdantic.
        **kwargs: Additional keyword arguments to [`pygraphviz.AGraph.draw`](https://pygraphviz.github.io/documentation/latest/reference/agraph.html#pygraphviz.AGraph.draw).
    """
    diagram = create(
        *models_or_modules, termini=termini, limit_search_models_to=limit_search_models_to
    )
    diagram.draw(out=out, **kwargs)


def to_dot(
    *models_or_modules: Union[type, ModuleType],
    termini: Sequence[type] = [],
    limit_search_models_to: Optional[Iterable[str]] = None,
) -> str:
    """Generate Graphviz [DOT language](https://graphviz.org/doc/info/lang.html) representation of
    entity relationship diagram for given data model classes.

    Args:
        *models_or_modules (type): Data model classes to diagram, or modules containing them.
        termini (Sequence[type]): Data model classes to set as terminal nodes. erdantic will stop
            searching for component classes when it reaches these models
        limit_search_models_to (Optional[Iterable[sr]], optional): Iterable of identifiers of data
            model classes that erdantic supports. If any are specified, when searching a module,
            limit data model classes to those ones. Defaults to None which will find all data model
            classes supported by erdantic.

    Returns:
        str: DOT language representation of diagram
    """
    diagram = create(
        *models_or_modules, termini=termini, limit_search_models_to=limit_search_models_to
    )
    return diagram.to_dot()
