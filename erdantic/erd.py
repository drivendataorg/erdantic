import os
from abc import ABC, abstractmethod
from typing import Any, List, Set, Union

import pygraphviz as pgv


row_template = """<tr><td>{name}</td><td port="{name}">{type_name}</td></tr>"""


class Field(ABC):
    @property
    @abstractmethod
    def name(self) -> str:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def type_name(self) -> str:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def type_obj(self) -> type:  # pragma: no cover
        pass

    @abstractmethod
    def is_many(self) -> bool:  # pragma: no cover
        pass

    @abstractmethod
    def is_nullable(self) -> bool:  # pragma: no cover
        pass

    @abstractmethod
    def __hash__(self) -> int:  # pragma: no cover
        pass

    def dot_row(self) -> str:
        return row_template.format(name=self.name, type_name=self.type_name)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and hash(self) == hash(other)


table_template = """
<<table border="0" cellborder="1" cellspacing="0">
<tr><td port="_root" colspan="2"><b>{name}</b></td></tr>
{rows}
</table>>
"""


class Model(ABC):
    @property
    @abstractmethod
    def name(self) -> str:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def fields(self) -> List[Field]:  # pragma: no cover
        pass

    @abstractmethod
    def __hash__(self):  # pragma: no cover
        pass

    def dot_label(self) -> str:
        rows = "\n".join(field.dot_row() for field in self.fields)
        return table_template.format(name=self.name, rows=rows).replace("\n", "")

    def __eq__(self, other):
        return isinstance(other, type(self)) and hash(self) == hash(other)

    def __repr__(self) -> str:
        return class_repr(self)


class Edge:
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
        return class_repr(self)


class EntityRelationshipDiagram:
    models: Set[Model]
    edges: Set[Edge]

    def __init__(self, models, edges):
        self.models = models
        self.edges = edges

    def draw(self, path: Union[str, os.PathLike], **kwargs):
        return self.graph().draw(path, prog="dot", **kwargs)

    def graph(self) -> pgv.AGraph:
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
        return self.graph().string()

    def __repr__(self) -> str:
        return class_repr(self)

    def _repr_svg_(self):
        graph = self.graph()
        return graph.draw(prog="dot", format="svg").decode(graph.encoding)


implementation_registry = {}


def register_type_checker(key: str):
    def decorator(fcn):
        global implementation_registry
        if key not in implementation_registry:
            implementation_registry[key] = {}
        implementation_registry[key]["type_checker"] = fcn
        return fcn

    return decorator


def register_constructor(key: str):
    def decorator(fcn):
        global implementation_registry
        if key not in implementation_registry:
            implementation_registry[key] = {}
        implementation_registry[key]["constructor"] = fcn
        return fcn

    return decorator


def create(*models: type):
    key = None
    for k, impl in implementation_registry.items():
        if impl["type_checker"](models[0]):
            key = k
    if key is None:
        raise ValueError(f"Passed data model class with MRO {models[0].__mro__} is not supported.")

    if "constructor" not in implementation_registry[key]:
        raise NotImplementedError(
            f"Implementation for {key} is missing a diagram constuctor function."
        )
    constructor = implementation_registry[key]["constructor"]
    return constructor(*models)


def draw(*models: type, path: Union[str, os.PathLike], **kwargs):
    diagram = create(*models)
    diagram.draw(path=path, **kwargs)


def to_dot(*models: type):
    diagram = create(*models)
    return diagram.to_dot()


def class_repr(obj):
    items = (f"{k}={v}" for k, v in obj.__dict__.items() if not k.startswith("_"))
    return f"{type(obj)}({','.join(items)})"
