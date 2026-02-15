from dataclasses import dataclass
from dataclasses import field as dc_field
import sys
from typing import Optional, Union

from attrs import define
from attrs import field as attrs_field
import msgspec
import pydantic


@define
class AttrsRelatedNode:
    name: str


@define
class AttrsRelationSemantics:
    required_node: AttrsRelatedNode
    optional_node: Optional[AttrsRelatedNode] = None
    related_nodes: list[AttrsRelatedNode] = attrs_field(factory=list)


@define
class AttrsAltNode:
    name: str


@define
class AttrsUnionSemantics:
    union_node: Union[AttrsRelatedNode, AttrsAltNode]
    optional_union_node: Optional[Union[AttrsRelatedNode, AttrsAltNode]] = None


@define
class AttrsNestedTypes:
    node_map: dict[str, Optional[AttrsRelatedNode]] = attrs_field(factory=dict)
    node_groups: list[list[AttrsRelatedNode]] = attrs_field(factory=list)


@define
class AttrsRecursive:
    parent: Optional["AttrsRecursive"] = None
    children: list["AttrsRecursive"] = attrs_field(factory=list)


@dataclass
class DataclassRelatedNode:
    name: str


@dataclass
class DataclassRelationSemantics:
    required_node: DataclassRelatedNode
    optional_node: Optional[DataclassRelatedNode] = None
    related_nodes: list[DataclassRelatedNode] = dc_field(default_factory=list)


@dataclass
class DataclassAltNode:
    name: str


@dataclass
class DataclassUnionSemantics:
    union_node: Union[DataclassRelatedNode, DataclassAltNode]
    optional_union_node: Optional[Union[DataclassRelatedNode, DataclassAltNode]] = None


@dataclass
class DataclassNestedTypes:
    node_map: dict[str, Optional[DataclassRelatedNode]] = dc_field(default_factory=dict)
    node_groups: list[list[DataclassRelatedNode]] = dc_field(default_factory=list)


@dataclass
class DataclassRecursive:
    parent: Optional["DataclassRecursive"] = None
    children: list["DataclassRecursive"] = dc_field(default_factory=list)


class PydanticRelatedNode(pydantic.BaseModel):
    name: str


class PydanticRelationSemantics(pydantic.BaseModel):
    required_node: PydanticRelatedNode
    optional_node: Optional[PydanticRelatedNode] = None
    related_nodes: list[PydanticRelatedNode] = []


class PydanticAltNode(pydantic.BaseModel):
    name: str


class PydanticUnionSemantics(pydantic.BaseModel):
    union_node: Union[PydanticRelatedNode, PydanticAltNode]
    optional_union_node: Optional[Union[PydanticRelatedNode, PydanticAltNode]] = None


class PydanticNestedTypes(pydantic.BaseModel):
    node_map: dict[str, Optional[PydanticRelatedNode]] = {}
    node_groups: list[list[PydanticRelatedNode]] = []


class PydanticRecursive(pydantic.BaseModel):
    parent: Optional["PydanticRecursive"] = None
    children: list["PydanticRecursive"] = []


class MsgspecRelatedNode(msgspec.Struct):
    name: str


class MsgspecRelationSemantics(msgspec.Struct):
    required_node: MsgspecRelatedNode
    optional_node: Optional[MsgspecRelatedNode] = None
    related_nodes: list[MsgspecRelatedNode] = msgspec.field(default_factory=list)


class MsgspecAltNode(msgspec.Struct):
    name: str


class MsgspecUnionSemantics(msgspec.Struct):
    union_node: Union[MsgspecRelatedNode, MsgspecAltNode]
    optional_union_node: Optional[Union[MsgspecRelatedNode, MsgspecAltNode]] = None


class MsgspecNestedTypes(msgspec.Struct):
    node_map: dict[str, Optional[MsgspecRelatedNode]] = msgspec.field(default_factory=dict)
    node_groups: list[list[MsgspecRelatedNode]] = msgspec.field(default_factory=list)


class MsgspecRecursive(msgspec.Struct):
    parent: Optional["MsgspecRecursive"] = None
    children: list["MsgspecRecursive"] = msgspec.field(default_factory=list)


SNAPSHOT_CASES = [
    ("attrs_relation_semantics", AttrsRelationSemantics),
    ("attrs_union_semantics", AttrsUnionSemantics),
    ("attrs_nested_types", AttrsNestedTypes),
    ("dataclasses_relation_semantics", DataclassRelationSemantics),
    ("dataclasses_union_semantics", DataclassUnionSemantics),
    ("dataclasses_nested_types", DataclassNestedTypes),
    ("pydantic_relation_semantics", PydanticRelationSemantics),
    ("pydantic_union_semantics", PydanticUnionSemantics),
    ("pydantic_nested_types", PydanticNestedTypes),
    ("msgspec_relation_semantics", MsgspecRelationSemantics),
    ("msgspec_union_semantics", MsgspecUnionSemantics),
    ("msgspec_nested_types", MsgspecNestedTypes),
]

if sys.version_info >= (3, 11):
    SNAPSHOT_CASES.extend(
        [
            ("attrs_recursive", AttrsRecursive),
            ("dataclasses_recursive", DataclassRecursive),
            ("pydantic_recursive", PydanticRecursive),
            ("msgspec_recursive", MsgspecRecursive),
        ]
    )
