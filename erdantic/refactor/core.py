from enum import Enum
from importlib import import_module
import inspect
import logging
import os
import textwrap
from typing import Any, Dict, Generic, List, Optional, Set, Tuple, Union

import pydantic
import pygraphviz as pgv
from typenames import REMOVE_ALL_MODULES, typenames

from erdantic.exceptions import (
    UnknownModelTypeError,
)
from erdantic.typing import (
    ModelFieldExtractor,
    ModelPredicate,
    ModelType,
    TypeAnnotation,
    get_recursive_args,
    is_collection_type_of,
    is_nullable_type,
)
from erdantic.version import __version__

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class FullyQualifiedName(pydantic.BaseModel):
    module: str
    qual_name: str

    @classmethod
    def from_object(cls, obj: Any):
        module = obj.__module__
        qual_name = obj.__qualname__
        return FullyQualifiedName(module=module, qual_name=qual_name)

    def __hash__(self) -> int:
        return hash((self.module, self.qual_name))

    def __str__(self) -> str:
        return f"{self.module}.{self.qual_name}"

    def import_object(self):
        module = import_module(self.module)
        obj = module
        for name in self.qual_name.split("."):
            obj = getattr(obj, name)
        return obj


class Cardinality(Enum):
    ONE = "one"
    MANY = "many"

    def to_dot(self) -> str:
        return CARDINALITY_DOT_MAPPING[self]


CARDINALITY_DOT_MAPPING = {
    Cardinality.ONE: "nonetee",
    Cardinality.MANY: "crow",
}


class Modality(Enum):
    ZERO = "zero"
    ONE = "one"

    def to_dot(self) -> str:
        return MODALITY_DOT_MAPPING[self]


MODALITY_DOT_MAPPING = {
    Modality.ZERO: "odot",
    Modality.ONE: "tee",
}

_TABLE_TEMPLATE = textwrap.dedent(
    """\
    <<table border="0" cellborder="1" cellspacing="0">
    <tr><td port="_root" colspan="2"><b>{name}</b></td></tr>
    {rows}
    </table>>
    """
)

_ROW_TEMPLATE = """<tr><td>{name}</td><td port="{name}">{type_name}</td></tr>"""


class FieldInfo(pydantic.BaseModel):
    model_full_name: FullyQualifiedName
    name: str
    type_name: str

    _raw_type: Optional[TypeAnnotation] = pydantic.PrivateAttr(None)

    model_config = pydantic.ConfigDict(
        extra="forbid",
        protected_namespaces=(),
    )

    @classmethod
    def from_raw_type(cls, model_full_name, name, raw_type):
        field_info = cls(
            model_full_name=model_full_name,
            name=name,
            type_name=typenames(raw_type, remove_modules=REMOVE_ALL_MODULES),
        )
        field_info._raw_type = raw_type
        return field_info

    @property
    def raw_type(self):
        if self._raw_type is None:
            model = self.model_full_name.import_object()
            get_fields_fn = registry.get_field_extractor_fn(model)
            if get_fields_fn:
                self._raw_type = get_fields_fn(model)[self.name]._raw_type
            else:
                raise UnknownModelTypeError(model)
        return self._raw_type

    def to_dot_row(self) -> str:
        """Returns the DOT language "HTML-like" syntax specification of a row detailing this field
        that is part of a table describing the field's parent data model. It is used as part the
        `label` attribute of data model's node in the graph's DOT representation.

        Returns:
            str: DOT language for table row
        """
        return _ROW_TEMPLATE.format(name=self.name, type_name=self.type_name)


class ModelInfo(pydantic.BaseModel, Generic[ModelType]):
    full_name: FullyQualifiedName
    name: str
    fields: Dict[str, FieldInfo]
    description: str = ""

    _raw_model: Optional[ModelType] = None

    model_config = pydantic.ConfigDict(
        extra="forbid",
    )

    @classmethod
    def from_raw_model(cls, raw_model: ModelType):
        get_fields_fn = registry.get_field_extractor_fn(raw_model)
        if not get_fields_fn:
            raise UnknownModelTypeError(raw_model)

        full_name = FullyQualifiedName.from_object(raw_model)
        description = str(full_name)
        docstring = inspect.getdoc(raw_model)
        if docstring:
            description += "\n\n" + docstring + "\n"

        model_info = cls(
            full_name=full_name,
            name=raw_model.__name__,
            fields=get_fields_fn(raw_model),
            description=description,
        )
        model_info._raw_model = raw_model
        return model_info

    @property
    def raw_model(self):
        if self._raw_model is None:
            self._raw_model = self.full_name.import_object()
        return self._raw_model

    def to_dot_label(self) -> str:
        """Returns the DOT language "HTML-like" syntax specification of a table for this data
        model. It is used as the `label` attribute of data model's node in the graph's DOT
        representation.

        Returns:
            str: DOT language for table
        """
        rows = "\n".join(field_info.to_dot_row() for field_info in self.fields.values()) + "\n"
        return _TABLE_TEMPLATE.format(name=self.name, rows=rows).replace("\n", "")


class Edge(pydantic.BaseModel):
    source_model_full_name: FullyQualifiedName
    source_field_name: str
    target_model_full_name: FullyQualifiedName
    target_cardinality: Cardinality
    target_modality: Modality
    source_cardinality: Optional[Cardinality] = None
    source_modality: Optional[Modality] = None

    def __hash__(self) -> int:
        return hash(
            (self.source_model_full_name, self.source_field_name, self.target_model_full_name)
        )

    @classmethod
    def from_field_info(cls, target_model, source_field_info: FieldInfo):
        is_collection = is_collection_type_of(source_field_info.raw_type, target_model)
        is_nullable = is_nullable_type(source_field_info.raw_type)
        cardinality = Cardinality.MANY if is_collection else Cardinality.ONE
        modality = Modality.ZERO if is_nullable or is_collection else Modality.ONE
        return Edge(
            source_model_full_name=source_field_info.model_full_name,
            source_field_name=source_field_info.name,
            target_model_full_name=FullyQualifiedName.from_object(target_model),
            target_cardinality=cardinality,
            target_modality=modality,
        )

    def target_dot_arrow_shape(self) -> str:
        """Arrow shape specification in Graphviz DOT language for this edge's head. See
        [Graphviz docs](https://graphviz.org/doc/info/arrows.html) as a reference. Shape returned
        is based on [crow's foot notation](https://www.calebcurry.com/cardinality-and-modality/)
        for the relationship's cardinality and modality.

        Returns:
            str: DOT language specification for arrow shape of this edge's head
        """
        return self.target_cardinality.to_dot() + self.target_modality.to_dot()

    def source_dot_arrow_shape(self) -> str:
        cardinality = self.source_cardinality.to_dot() if self.source_cardinality else ""
        modality = self.source_modality.to_dot() if self.source_modality else ""
        return cardinality + modality


class Registry:
    implementations: List[Tuple[ModelPredicate, ModelFieldExtractor]]

    def __init__(self) -> None:
        self.implementations = []

    def register(self, predicate_fn: ModelPredicate, get_fields_fn: ModelFieldExtractor):
        self.implementations.append((predicate_fn, get_fields_fn))

    def get_field_extractor_fn(self, tp: type) -> Optional[ModelFieldExtractor]:
        for predicate_fn, get_fields_fn in self.implementations:
            if predicate_fn(tp):
                return get_fields_fn
        return None


registry = Registry()


class EntityRelationshipDiagram(pydantic.BaseModel):
    models: Dict[str, ModelInfo] = {}
    edges: Set[Edge] = set()

    def _search(self, model) -> bool:
        logger.info("Searching model %s", model)
        get_fields_fn = registry.get_field_extractor_fn(model)
        if get_fields_fn:
            key = str(FullyQualifiedName.from_object(model))
            if key not in self.models:
                model_info = ModelInfo.from_raw_model(model)
                self.models[key] = model_info
                for field_info in model_info.fields.values():
                    for arg in get_recursive_args(field_info.raw_type):
                        is_model = self._search(arg)
                        if is_model:
                            edge = Edge.from_field_info(arg, field_info)
                            self.edges.add(edge)
        return bool(get_fields_fn)

    def add_model(self, model):
        is_model = self._search(model)
        if not is_model:
            raise UnknownModelTypeError(model)

    def draw(self, out: Union[str, os.PathLike], **kwargs):
        """Render entity relationship diagram for given data model classes to file.

        Args:
            out (Union[str, os.PathLike]): Output file path for rendered diagram.
            **kwargs: Additional keyword arguments to [`pygraphviz.AGraph.draw`](https://pygraphviz.github.io/documentation/latest/reference/agraph.html#pygraphviz.AGraph.draw).
        """
        self.to_graphviz().draw(out, prog="dot", **kwargs)

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
        for full_name, model_info in self.models.items():
            g.add_node(
                full_name,
                label=model_info.to_dot_label(),
                tooltip=model_info.description.replace("\n", "&#xA;"),
            )
        for edge in self.edges:
            g.add_edge(
                edge.source_model_full_name,
                edge.target_model_full_name,
                tailport=f"{edge.source_field_name}:e",
                headport="_root:w",
                arrowhead=edge.target_dot_arrow_shape(),
                arrowtail=edge.source_dot_arrow_shape(),
            )
        return g

    def to_dot(self) -> str:
        """Generate Graphviz [DOT language](https://graphviz.org/doc/info/lang.html) representation
        of entity relationship diagram for given data model classes.

        Returns:
            str: DOT language representation of diagram
        """
        return self.to_graphviz().string()
