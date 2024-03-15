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
    except NameError as e:
        model_full_name = FullyQualifiedName.from_object(model)
        forward_ref = getattr(e, "name", re.search(r"(?<=')(?:[^'])*(?=')", str(e)).group(0))
        msg = (
            f"Failed to resolve forward reference '{forward_ref}' in the type annotations for "
            f"dataclass {model_full_name}. "
            "You should use erdantic.plugins.dataclasses.resolve_types_on_dataclass with locals() "
            "where you define the class."
        )
        raise UnresolvableForwardRefError(msg, name=forward_ref) from e
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
    # Cache whether we have already run this on a cls
    # Inspired by attrs.resolve_types
    if getattr(cls, "__erdantic_dataclass_types_resolved__", None) != cls:
        hints = get_type_hints(
            cls, globalns=globalns, localns=localns, include_extras=include_extras
        )
        for field in dataclasses.fields(cls):
            field.type = hints[field.name]
        # Use reference to cls as indicator in case of subclasses
        cls.__erdantic_dataclass_types_resolved__ = cls
    return cls
