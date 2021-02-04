import os
from abc import ABC, abstractmethod
from typing import Any, List, Set, Union, get_type_hints, get_origin, get_args

import pygraphviz as pgv


row_template = """<tr><td>{name}</td><td port="{name}">{type_name}</td></tr>"""


class Field(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def type_name(self) -> str:
        pass

    @property
    @abstractmethod
    def type_obj(self) -> type:
        pass

    @abstractmethod
    def is_many(self) -> bool:
        pass

    @abstractmethod
    def is_nullable(self) -> bool:
        pass

    @abstractmethod
    def __hash__(self) -> int:
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
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def fields(self) -> List[Field]:
        pass

    @abstractmethod
    def __hash__(self):
        pass

    def dot_label(self) -> str:
        rows = "\n".join(field.dot_row() for field in self.fields)
        return table_template.format(name=self.name, rows=rows).replace("\n", "")

    def __eq__(self, other):
        return isinstance(other, type(self)) and hash(self) == hash(other)


class Edge:
    source: Model
    source_field: Field
    target: Model

    def __init__(self, source: Model, source_field: Field, target: Model):
        if source_field not in set(source.fields):
            print(hash(source_field))
            print([hash(f) for f in source.fields])
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


class EntityRelationshipDiagram:
    models: Set[Model]
    edges: Set[Edge]

    def __init__(self, models, edges):
        self.models = models
        self.edges = edges

    def draw(self, path: Union[str, os.PathLike], **kwargs):
        return self.graph().draw(path, prog="dot", **kwargs)

    def graph(self) -> pgv.AGraph:
        g = pgv.AGraph(directed=True, nodesep=0.5, ranksep=1.5, rankdir="LR")
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

    def _repr_svg_(self):
        graph = self.graph()
        return graph.draw(prog="dot", format="svg").decode(graph.encoding)


constructor_registry = {}


def register_constructor(fcn):
    """Decorator to register functions that construct EntityRelationshipDiagram from data model
    classes.
    """
    type_hints = get_type_hints(fcn)
    models_type = type_hints["models"]
    if get_origin(models_type) is not type:
        raise ValueError(f"models must have type typing.Type[...]. Got {models_type}")
    constructor_registry[id(get_args(models_type)[0])] = fcn
    return fcn


def create_erd(*models: type):
    key = None
    for cls in models[0].__mro__:
        if id(cls) in constructor_registry:
            key = id(cls)
            break
    if key is None:
        raise ValueError("Passed data model class is not supported.")

    constructor = constructor_registry[key]
    return constructor(*models)


def draw(*models: type, path: Union[str, os.PathLike], **kwargs):
    diagram = create_erd(*models)
    diagram.draw(path=path, **kwargs)


def to_dot(*models: type):
    diagram = create_erd(*models)
    return diagram.to_dot()
