from enum import Enum
from functools import total_ordering
from importlib import import_module
import inspect
import logging
import os
import sys
import textwrap
from typing import Any, Dict, Generic, Mapping, Optional, Tuple, TypeVar, Union

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

import pydantic
import pygraphviz as pgv  # type: ignore [import-not-found]
from sortedcontainers_pydantic import SortedDict, SortedSet
from typenames import REMOVE_ALL_MODULES, typenames

from erdantic._version import __version__
from erdantic.exceptions import (
    FieldNotFoundError,
    UnevaluatedForwardRefError,
    UnknownModelTypeError,
    _UnevaluatedForwardRefError,
)
from erdantic.plugins import identify_field_extractor_fn
from erdantic.typing_utils import (
    get_recursive_args,
    is_collection_type_of,
    is_nullable_type,
)

logger = logging.getLogger(__name__)

_ModelType = TypeVar("_ModelType", bound=type)


@total_ordering
class FullyQualifiedName(pydantic.BaseModel):
    """Holds the fully qualified name components (module and qualified name) of a Python object.
    This is used to uniquely identify an object, can be used to import it.

    Attributes:
        module (str): Name of the module that the object is defined in.
        qual_name (str): Qualified name of the object.
    """

    module: str
    qual_name: str

    @classmethod
    def from_object(cls, obj: Any) -> Self:
        """Constructor method to create a new instance from a Python object.

        Args:
            obj (Any): Python object.

        Returns:
            Self: Fully qualified name of the object.
        """
        return cls(module=obj.__module__, qual_name=obj.__qualname__)

    def __hash__(self) -> int:
        return hash((self.module, self.qual_name))

    def __str__(self) -> str:
        return f"{self.module}.{self.qual_name}"

    def import_object(self) -> Any:
        """Imports the object from the module and returns it.

        Returns:
            Any: Object referenced by this FullyQualifiedName instance.
        """
        module = import_module(self.module)
        obj = module
        for name in self.qual_name.split("."):
            obj = getattr(obj, name)
        return obj

    def __lt__(self, other: Self) -> bool:
        if not isinstance(other, FullyQualifiedName):
            return NotImplemented
        return (self.module, self.qual_name) < (other.module, other.qual_name)


class FieldInfo(pydantic.BaseModel):
    """Holds information about a field of an analyzed data model class.

    Attributes:
        model_full_name (FullyQualifiedName): Fully qualified name of the data model class that
            the field belongs to.
        name (str): Name of the field.
        type_name (str): String representation of the field's type.
    """

    model_full_name: FullyQualifiedName
    name: str
    type_name: str

    model_config = pydantic.ConfigDict(
        extra="forbid",
        protected_namespaces=(),
    )

    _ROW_TEMPLATE = """<tr><td>{name}</td><td port="{name}">{type_name}</td></tr>"""

    _raw_type: Optional[type] = pydantic.PrivateAttr(None)

    @classmethod
    def from_raw_type(cls, model_full_name: FullyQualifiedName, name: str, raw_type: type) -> Self:
        """Constructor method to create a new instance from a raw type annotation.

        Args:
            model_full_name (FullyQualifiedName): Fully qualified name of the data model class that
            the field belongs to.
            name (str): Name of field.
            raw_type (type): Type annotation.

        Returns:
            Self: _description_
        """
        field_info = cls(
            model_full_name=model_full_name,
            name=name,
            type_name=typenames(raw_type, remove_modules=REMOVE_ALL_MODULES),
        )
        field_info._raw_type = raw_type
        return field_info

    @property
    def raw_type(self) -> type:
        """Returns the raw type annotation of the field. This is a cached property. If the raw
        type is not already known, it will attempt to import the data model class and reextract
        the field's type annotation.

        Raises:
            FieldNotFoundError: _description_
            UnknownModelTypeError: _description_

        Returns:
            type: Type annotation.
        """
        if self._raw_type is None:
            model = self.model_full_name.import_object()
            get_fields_fn = identify_field_extractor_fn(model)
            if get_fields_fn:
                for field_info in get_fields_fn(model):
                    if field_info.name == self.name:
                        self._raw_type = field_info.raw_type
                        break
                else:
                    raise FieldNotFoundError(
                        name=self.name, obj=model, model_full_name=self.model_full_name
                    )
            else:
                raise UnknownModelTypeError(model=model)
        return self._raw_type

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, FieldInfo):
            return NotImplemented
        return self.model_dump() == other.model_dump()

    def to_dot_row(self) -> str:
        """Returns the DOT language "HTML-like" syntax specification of a row detailing this field
        that is part of a table describing the field's parent data model. It is used as part the
        `label` attribute of data model's node in the graph's DOT representation.

        Returns:
            str: DOT language for table row
        """
        return self._ROW_TEMPLATE.format(name=self.name, type_name=self.type_name)


class ModelInfo(pydantic.BaseModel, Generic[_ModelType]):
    """Holds information about an analyzed data model class.

    Attributes:
        full_name (FullyQualifiedName): Fully qualified name of the data model class.
        name (str): Name of the data model class.
        fields (Dict[str, FieldInfo]): A mapping to FieldInfo instances for each field of the data
            model class.
        description (str): Docstring or other description of the data model class.
    """

    full_name: FullyQualifiedName
    name: str
    fields: Dict[str, FieldInfo]
    description: str = ""

    model_config = pydantic.ConfigDict(
        extra="forbid",
    )

    _TABLE_TEMPLATE = textwrap.dedent(
        """\
        <<table border="0" cellborder="1" cellspacing="0">
        <tr><td port="_root" colspan="2"><b>{name}</b></td></tr>
        {rows}
        </table>>
        """
    )

    _raw_model: Optional[_ModelType] = pydantic.PrivateAttr(None)

    @classmethod
    def from_raw_model(cls, raw_model: _ModelType) -> Self:
        """Constructor method to create a new instance from a raw data model class.

        Args:
            raw_model (type): Data model class.

        Returns:
            Self: New instance of ModelInfo.
        """
        get_fields_fn = identify_field_extractor_fn(raw_model)
        if not get_fields_fn:
            raise UnknownModelTypeError(model=raw_model)

        full_name = FullyQualifiedName.from_object(raw_model)
        description = str(full_name)
        docstring = inspect.getdoc(raw_model)
        if docstring:
            description += "\n\n" + docstring + "\n"

        model_info = cls(
            full_name=full_name,
            name=raw_model.__name__,
            fields={field_info.name: field_info for field_info in get_fields_fn(raw_model)},
            description=description,
        )
        model_info._raw_model = raw_model
        return model_info

    @property
    def raw_model(self) -> _ModelType:
        """Returns the raw data model class. This is a cached property. If the raw model is not
        already known, it will attempt to import the data model class.
        """
        if self._raw_model is None:
            self._raw_model = self.full_name.import_object()
        return self._raw_model

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ModelInfo):
            return NotImplemented
        return self.model_dump() == other.model_dump()

    def to_dot_label(self) -> str:
        """Returns the DOT language "HTML-like" syntax specification of a table for this data
        model. It is used as the `label` attribute of data model's node in the graph's DOT
        representation.

        Returns:
            str: DOT language for table
        """
        rows = "\n".join(field_info.to_dot_row() for field_info in self.fields.values()) + "\n"
        return self._TABLE_TEMPLATE.format(name=self.name, rows=rows).replace("\n", "")


class Cardinality(Enum):
    """Enumeration of possible cardinality values for a relationship between two data model
    classes. Cardinality measures the maximum number of associations—valid values are 'one' or
    'many'.
    """

    UNSPECIFIED = "unspecified"
    ONE = "one"
    MANY = "many"

    def to_dot(self) -> str:
        """Returns the DOT language specification for the arrowhead styling associated with the
        cardinality value.
        """
        return _CARDINALITY_DOT_MAPPING[self]


_CARDINALITY_DOT_MAPPING = {
    Cardinality.UNSPECIFIED: "none",
    Cardinality.ONE: "nonetee",
    Cardinality.MANY: "crow",
}


class Modality(Enum):
    """Enumeration of possible cardinality values for a relationship between two data model
    classes. Cardinality measures the minimum number of associations—valid values are 'zero' or
    'one'.
    """

    UNSPECIFIED = "unspecified"
    ZERO = "zero"
    ONE = "one"

    def to_dot(self) -> str:
        """Returns the DOT language specification for the arrowhead styling associated with the
        modality value.
        """
        return _MODALITY_DOT_MAPPING[self]


_MODALITY_DOT_MAPPING = {
    Modality.UNSPECIFIED: "none",
    Modality.ZERO: "odot",
    Modality.ONE: "tee",
}


@total_ordering
class Edge(pydantic.BaseModel):
    """Hold information about a relationship between two data model classes. These represent
    directed edges in the entity relationship diagram.

    Attributes:
        source_model_full_name (FullyQualifiedName): Fully qualified name of the source model,
            i.e., the model that contains a field that references the target model.
        source_field_name (str): Name of the field on the source model that references the target
            model.
        target_model_full_name (FullyQualifiedName): Fully qualified name of the target model,
            i.e., the model that is referenced by the source model's field.
        target_cardinality (Cardinality): Cardinality of the target model in the relationship,
            e.g., if the relationship is one (source) to many (target), this value will be
            `Cardinality.MANY`.
        target_modality (Modality): Modality of the target model in the relationship, e.g., if the
            relationship is one (source) to zero (target), meaning that the target is optional,
            this value will be `Modality.ZERO`.
        source_cardinality (Optional[Cardinality]): Cardinality of the source model in the
            relationship. This will never be set for Edges created by erdantic, but you can set it
            manually to notate an externally known cardinality.
        source_modality (Optional[Modality]): Modality of the source model in the relationship.
            This will never be set for Edges created by erdantic, but you can set it manually to
            notate an externally known modality.
    """

    source_model_full_name: FullyQualifiedName
    source_field_name: str
    target_model_full_name: FullyQualifiedName
    target_cardinality: Cardinality
    target_modality: Modality
    source_cardinality: Cardinality = Cardinality.UNSPECIFIED
    source_modality: Modality = Modality.UNSPECIFIED

    def __hash__(self) -> int:
        return hash(
            (self.source_model_full_name, self.source_field_name, self.target_model_full_name)
        )

    @property
    def _sort_key(self) -> Tuple[FullyQualifiedName, str, FullyQualifiedName]:
        """Used to define an ordering for instances of Edges."""
        return (
            self.source_model_full_name,
            self.source_field_name,
            self.target_model_full_name,
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, Edge):
            return NotImplemented
        return self._sort_key < other._sort_key

    @classmethod
    def from_field_info(cls, target_model: type, source_field_info: FieldInfo) -> Self:
        """Constructor method to create a new instance from a target model instance and a source
        model's FieldInfo.

        Args:
            target_model (type): Target model class.
            source_field_info (FieldInfo): FieldInfo instance for the field on the source model
                that references the target model.

        Returns:
            Self: New instance of Edge.
        """
        is_collection = is_collection_type_of(source_field_info.raw_type, target_model)
        is_nullable = is_nullable_type(source_field_info.raw_type)
        cardinality = Cardinality.MANY if is_collection else Cardinality.ONE
        if is_nullable:
            modality = Modality.ZERO
        else:
            modality = Modality.UNSPECIFIED if is_collection else Modality.ONE
        return cls(
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
        return self.source_cardinality.to_dot() + self.source_modality.to_dot()


_DEFAULT_GRAPH_ATTRS = (
    ("nodesep", "0.5"),
    ("ranksep", "1.5"),
    ("rankdir", "LR"),
    ("label", f"Created by erdantic v{__version__} <https://github.com/drivendataorg/erdantic>"),
    ("fontname", "Times New Roman,Times,Liberation Serif,serif"),
    ("fontsize", "9"),
    ("fontcolor", "gray66"),
)

_DEFAULT_NODE_ATTRS = (
    ("fontname", "Times New Roman,Times,Liberation Serif,serif"),
    ("fontsize", 14),
    ("shape", "plain"),
)

_DEFAULT_EDGE_ATTRS = (("dir", "both"),)


class EntityRelationshipDiagram(pydantic.BaseModel):
    """Holds information about an entity relationship diagram for a set of data model classes and
    their relationships, and provides methods to render the diagram.

    Attributes:
        models (SortedDict[str, ModelInfo]): Mapping of ModelInfo instances for models included
            in the diagram. Each key is the string representation of the fully qualified name of
            the model.
        edges (SortedSet[Edge]): Set of edges representing relationships between the models.
    """

    models: SortedDict[str, ModelInfo] = SortedDict()
    edges: SortedSet[Edge] = SortedSet()

    def _add_if_model(self, model: type, recurse: bool) -> bool:
        """Private recursive method to add a model to the diagram."""
        key = str(FullyQualifiedName.from_object(model))
        if key not in self.models:
            try:
                model_info = ModelInfo.from_raw_model(model)
                self.models[key] = model_info
                logger.debug("Sucessfully added model '%s'.", key)
                if recurse:
                    logger.debug("Searching fields of '%s' for other models...", key)
                    for field_info in model_info.fields.values():
                        logger.debug(
                            "Analyzing model '%s' field '%s' of type '%s'...",
                            key,
                            field_info.name,
                            field_info.type_name,
                        )
                        try:
                            for arg in get_recursive_args(field_info.raw_type):
                                is_model = self._add_if_model(arg, recurse=recurse)
                                if is_model:
                                    edge = Edge.from_field_info(arg, field_info)
                                    self.edges.add(edge)
                        except _UnevaluatedForwardRefError as e:
                            raise UnevaluatedForwardRefError(
                                model_full_name=model_info.full_name,
                                field_name=field_info.name,
                                forward_ref=e.forward_ref,
                            )
            except UnknownModelTypeError:
                return False
        else:
            logger.debug("Model '%s' already exists in diagram.", key)
        return True

    def add_model(self, model: type, recurse=True):
        """Add a data model class to the diagram.

        Args:
            model (type): Data model class to add to the diagram.
            recurse (bool, optional): Whether to recursively add models referenced by fields of
                the given model. Defaults to True.

        Raises:
            UnknownModelTypeError: If the model is not recognized as a data model class type that
                is supported by registered plugins.
        """
        logger.info("Adding model to '%s' to diagram...", typenames(model))
        is_model = self._add_if_model(model, recurse=recurse)
        if not is_model:
            raise UnknownModelTypeError(model=model)

    def draw(
        self,
        out: Union[str, os.PathLike],
        graph_attrs: Optional[Mapping[str, Any]] = None,
        node_attrs: Optional[Mapping[str, Any]] = None,
        edge_attrs: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ):
        """Render entity relationship diagram for given data model classes to file. The file format
        can be inferred from the file extension. Typical formats include '.png', '.svg', and
        '.pdf'.

        Args:
            out (str | os.PathLike): Output file path for rendered diagram.
            graph_attrs (Mapping[str, Any] | None, optional): Override any graph attributes on
                the `pygraphviz.AGraph` instance. Defaults to None.
            node_attrs (Mapping[str, Any] | None, optional): Override any node attributes for all
                nodes on the `pygraphviz.AGraph` instance. Defaults to None.
            edge_attrs (Mapping[str, Any] | None, optional): Override any edge attributes for all
                edges on the `pygraphviz.AGraph` instance. Defaults to None.
            **kwargs: Additional keyword arguments to [`pygraphviz.AGraph.draw`](https://pygraphviz.github.io/documentation/latest/reference/agraph.html#pygraphviz.AGraph.draw).
        """
        logger.info("Rendering diagram to %s", out)
        self.to_graphviz(
            graph_attrs=graph_attrs,
            node_attrs=node_attrs,
            edge_attrs=edge_attrs,
        ).draw(out, prog="dot", **kwargs)

    def to_graphviz(
        self,
        graph_attrs: Optional[Mapping[str, Any]] = None,
        node_attrs: Optional[Mapping[str, Any]] = None,
        edge_attrs: Optional[Mapping[str, Any]] = None,
    ) -> pgv.AGraph:
        """Return [`pygraphviz.AGraph`](https://pygraphviz.github.io/documentation/latest/reference/agraph.html)
        instance for diagram.

        Args:
            graph_attrs (Mapping[str, Any] | None, optional): Override any graph attributes on
                the `pygraphviz.AGraph` instance. Defaults to None.
            node_attrs (Mapping[str, Any] | None, optional): Override any node attributes for all
                nodes on the `pygraphviz.AGraph` instance. Defaults to None.
            edge_attrs (Mapping[str, Any] | None, optional): Override any edge attributes for all
                edges on the `pygraphviz.AGraph` instance. Defaults to None.

        Returns:
            pygraphviz.AGraph: graph object for diagram
        """
        g = pgv.AGraph(
            name="Entity Relationship Diagram",
            directed=True,
            strict=False,
        )
        g.graph_attr.update(_DEFAULT_GRAPH_ATTRS)
        g.graph_attr.update(graph_attrs or {})
        g.node_attr.update(_DEFAULT_NODE_ATTRS)
        g.node_attr.update(node_attrs or {})
        g.edge_attr.update(_DEFAULT_EDGE_ATTRS)
        g.edge_attr.update(edge_attrs or {})
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

    def to_dot(
        self,
        graph_attrs: Optional[Mapping[str, Any]] = None,
        node_attrs: Optional[Mapping[str, Any]] = None,
        edge_attrs: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """Generate Graphviz [DOT language](https://graphviz.org/doc/info/lang.html) representation
        of entity relationship diagram for given data model classes.

        Args:
            graph_attrs (Mapping[str, Any] | None, optional): Override any graph attributes on
                the `pygraphviz.AGraph` instance. Defaults to None.
            node_attrs (Mapping[str, Any] | None, optional): Override any node attributes for all
                nodes on the `pygraphviz.AGraph` instance. Defaults to None.
            edge_attrs (Mapping[str, Any] | None, optional): Override any edge attributes for all
                edges on the `pygraphviz.AGraph` instance. Defaults to None.

        Returns:
            str: DOT language representation of diagram
        """
        return self.to_graphviz(
            graph_attrs=graph_attrs,
            node_attrs=node_attrs,
            edge_attrs=edge_attrs,
        ).string()
