import dataclasses
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
    # Try to resolve forward references
    try:
        annotations = get_type_hints(model)
    except NameError as e:
        model_full_name = FullyQualifiedName.from_object(model)
        if getattr(e, "name", None):
            msg = (
                f"Failed to resolve forward reference '{e.name}' in the type annotations for "
                f"dataclass {model_full_name}."
            )
        else:
            msg = (
                "Failed to resolve a forward reference in the type annotations for "
                f"dataclass {model_full_name}."
            )
        raise UnresolvableForwardRefError(msg) from e

    return [
        FieldInfo.from_raw_type(
            model_full_name=FullyQualifiedName.from_object(model),
            name=f.name,
            raw_type=annotations[f.name],
        )
        for f in dataclasses.fields(model)
    ]


register_plugin(
    key="dataclasses", predicate_fn=is_dataclass_type, get_fields_fn=get_fields_from_dataclass
)
