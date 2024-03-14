import dataclasses
import re
from typing import TYPE_CHECKING, Any, List, Type, TypeGuard, get_type_hints

from erdantic.core import FieldInfo, FullyQualifiedName
from erdantic.exceptions import UnresolvableForwardRefError
from erdantic.plugins import register_plugin

if TYPE_CHECKING:
    from _typeshed import DataclassInstance  # pragma: no cover


DataclassType = Type["DataclassInstance"]


def is_dataclass_type(obj: Any) -> TypeGuard[DataclassType]:
    return isinstance(obj, type) and dataclasses.is_dataclass(obj)


def get_fields_from_dataclass(model: DataclassType) -> List[FieldInfo]:
    try:
        # Try to automatically resolve forward references
        resolve_types_on_dataclass(model)
    except NameError:
        # Don't error if a forward reference can't be resolved
        # typing.get_type_hints will error even if forward references had been resolved manually
        # We'll just have to let EntityRelationDiagram.add_model error later
        pass
    return [
        FieldInfo.from_raw_type(
            model_full_name=FullyQualifiedName.from_object(model),
            name=f.name,
            raw_type=f.type,
        )
        for f in dataclasses.fields(model)
    ]


register_plugin(
    key="dataclasses", predicate_fn=is_dataclass_type, get_fields_fn=get_fields_from_dataclass
)


def resolve_types_on_dataclass(
    cls: DataclassType, globalns=None, localns=None, include_extras=False
) -> DataclassType:
    hints = get_type_hints(cls, globalns=globalns, localns=localns, include_extras=include_extras)
    for field in dataclasses.fields(cls):
        field.type = hints[field.name]
    return cls
