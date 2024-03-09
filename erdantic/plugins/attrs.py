from typing import Any, List, Type, TypeGuard

import attrs

from erdantic.core import FieldInfo, FullyQualifiedName
from erdantic.exceptions import UnresolvableForwardRefError
from erdantic.plugins import register_plugin

AttrsClassType = Type[attrs.AttrsInstance]


def is_attrs_class(obj: Any) -> TypeGuard[AttrsClassType]:
    return isinstance(obj, type) and attrs.has(obj)


def get_fields_from_attrs_class(model: AttrsClassType) -> List[FieldInfo]:
    try:
        attrs.resolve_types(model)
    except NameError as e:
        model_full_name = FullyQualifiedName.from_object(model)
        if getattr(e, "name", None):
            msg = (
                f"Failed to resolve forward reference '{e.name}' in the type annotations for "
                f"attrs class {model_full_name}."
            )
        else:
            msg = (
                "Failed to resolve a forward reference in the type annotations for "
                f"attrs class {model_full_name}."
            )
        msg += " " + "You should use attrs.resolve_types with locals() where you define the class."
        raise UnresolvableForwardRefError(msg) from e
    return [
        FieldInfo.from_raw_type(
            model_full_name=FullyQualifiedName.from_object(model),
            name=attrib.name,
            raw_type=attrib.type,
        )
        for attrib in attrs.fields(model)
    ]


register_plugin(
    key="attrs", predicate_fn=is_attrs_class, get_fields_fn=get_fields_from_attrs_class
)
