import dataclasses
from enum import Enum
from typing import Callable, Dict, Generic, List, Optional, TypeGuard, TypeVar

from pydantic import BaseModel
import pygraphviz as pgv
from typenames import REMOVE_ALL_MODULES, typenames

from erdantic.exceptions import (
    StringForwardRefError,
    UnevaluatedForwardRefError,
    UnknownModelTypeError,
    _StringForwardRefError,
    _UnevaluatedForwardRefError,
)
from erdantic.typing import (
    TypeAnnotation,
    get_recursive_args,
    is_collection_type,
    is_nullable_type,
)


class Cardinality(Enum):
    ONE = "one"
    MANY = "many"


class Modality(Enum):
    ZERO = "zero"
    ONE = "one"


class FieldInfo(BaseModel):
    name: str
    type_obj: TypeAnnotation
    type_name: str

    @property
    def is_collection(self) -> bool:
        return is_collection_type(self.type_obj)

    @property
    def is_nullable(self) -> bool:
        return is_nullable_type(self.type_obj)


ModelType = TypeVar("ModelType")


class ModelInfo(BaseModel, Generic[ModelType]):
    raw: ModelType
    name: str
    fields: List[FieldInfo]
    docstring: str


class Edge(BaseModel):
    source_field: FieldInfo
    target_model: ModelType
    target_cardinality: Cardinality
    target_modality: Modality
    source_cardinality: Optional[Cardinality] = None
    source_modality: Optional[Modality] = None


# Steps
# Create FieldInfo for all fields
# Create ModelInfo
# Create Edges
# Recurse Edge targets

ModelAnalyzer = Callable[[ModelType], ModelInfo[ModelType]]
ModelPredicate = Callable[[ModelType], TypeGuard[ModelType]]


class Registery:
    def __init__(self) -> None:
        self.implementations = []

    def register(self, analyzer_fn: ModelAnalyzer, predicate_fn: ModelPredicate):
        self.implementations.append((analyzer_fn, predicate_fn))

    def get_analyzer(self, tp: type) -> Optional[ModelAnalyzer]:
        for analyzer_fn, predicate_fn in self.implementations:
            if predicate_fn(tp):
                return analyzer_fn
        return None


registry = Registery()


def is_dataclass(obj) -> bool:
    return isinstance(obj, type) and dataclasses.is_dataclass(obj)


def analyze_dataclass_model(model: ModelType) -> ModelInfo[ModelType]:
    return ModelInfo(
        name=model.__name__,
        raw=model,
        fields=[
            FieldInfo(name=f.name, type_obj=f.type, type_name=typenames(f.type))
            for f in dataclasses.fields(model)
        ],
        docstring=model.__doc__,
    )


def is_pydantic_model(obj) -> bool:
    return isinstance(obj, type) and issubclass(obj, BaseModel)


class Graph(BaseModel):
    nodes: Dict[ModelType, ModelInfo[ModelType]] = {}
    edges: List[Edge] = []

    def search(self, model):
        if model not in self.nodes:
            analyzer_fn = registry.get_analyzer(model)
            if analyzer_fn:
                model_info = analyzer_fn(model)
                self.models[model] = model_info
                for field_info in model_info.fields:
                    try:
                        for arg in get_recursive_args(field_info.type_obj):
                            try:
                                field_model = self.search(arg)
                                self.edges.append(
                                    Edge(
                                        source_field=field_info,
                                        target_model=field_model,
                                        target_cardinality=0,
                                        target_modality=0,
                                    )
                                )
                            except UnknownModelTypeError:
                                pass
                    except _UnevaluatedForwardRefError as e:
                        raise UnevaluatedForwardRefError(
                            model=model, field=field_info, forward_ref=e.forward_ref
                        ) from None
                    except _StringForwardRefError as e:
                        raise StringForwardRefError(
                            model=model, field=field_info, forward_ref=e.forward_ref
                        ) from None
        return model

    def draw(self, out: Union[str, os.PathLike], **kwargs):
        """Render entity relationship diagram for given data model classes to file.

        Args:
            out (Union[str, os.PathLike]): Output file path for rendered diagram.
            **kwargs: Additional keyword arguments to [`pygraphviz.AGraph.draw`](https://pygraphviz.github.io/documentation/latest/reference/agraph.html#pygraphviz.AGraph.draw).
        """
        self.graph().draw(out, prog="dot", **kwargs)

    def to_graphviz(self) -> pgv.AGraph:
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
        return self.to_graphviz().string()
