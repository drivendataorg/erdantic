import re
import sys
from typing import Any, List, Type

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard

import attrs

from erdantic.core import FieldInfo, FullyQualifiedName
from erdantic.exceptions import UnresolvableForwardRefError
from erdantic.plugins import register_plugin

AttrsClassType = Type[attrs.AttrsInstance]


def is_attrs_class(obj: Any) -> TypeGuard[AttrsClassType]:
    """Predicate function to determine if an object is an attrs class (not an instance).

    Args:
        obj (Any): The object to check.

    Returns:
        bool: True if the object is an attrs class, False otherwise.
    """
    return isinstance(obj, type) and attrs.has(obj)


def get_fields_from_attrs_class(model: AttrsClassType) -> List[FieldInfo]:
    """Given an attrs class, return a list of FieldInfo instances for each field in the class.

    Args:
        model (AttrsClassType): The attrs class to get fields from.

    Returns:
        List[FieldInfo]: List of FieldInfo instances for each field in the class
    """
    try:
        # Try to automatically resolve forward references
        attrs.resolve_types(model)
    except NameError as e:
        model_full_name = FullyQualifiedName.from_object(model)
        forward_ref = getattr(
            e,
            "name",
            re.search(r"(?<=')(?:[^'])*(?=')", str(e)).group(0),  # type: ignore [union-attr]
        )
        msg = (
            f"Failed to resolve forward reference '{forward_ref}' in the type annotations for "
            f"attrs class {model_full_name}. "
            "You should use attrs.resolve_types with locals() where you define the class."
        )
        raise UnresolvableForwardRefError(
            msg, name=forward_ref, model_full_name=model_full_name
        ) from e
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
