import re
import sys
from typing import Any, Type

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard

import msgspec

from erdantic.core import FieldInfo, FullyQualifiedName
from erdantic.exceptions import UnresolvableForwardRefError
from erdantic.plugins import register_plugin

MsgspecStruct = Type[msgspec.Struct]


def is_msgspec_struct(obj: Any) -> TypeGuard[MsgspecStruct]:
    """Predicate function to determine if an object is a msgspect struct (class, not instance).

    Args:
        obj (Any): The object to check.

    Returns:
        bool: True if the object is a Struct class, False otherwise.
    """
    return isinstance(obj, type) and issubclass(obj, msgspec.Struct)


def get_fields_from_msgspec_struct(model: MsgspecStruct) -> list[FieldInfo]:
    """Given a msgspec struct, return a list of FieldInfo instances for each field in the
    struct.

    Args:
        model (PydanticModel): The struct to get fields from.

    Returns:
        list[FieldInfo]: List of FieldInfo instances for each field in the struct
    """
    try:
        msgspec._utils.get_class_annotations(model)  # type: ignore [attr-defined]
        return [
            FieldInfo.from_raw_type(
                model_full_name=FullyQualifiedName.from_object(model),
                name=msgspec_field_info.name,
                raw_type=msgspec_field_info.type,
            )
            for msgspec_field_info in msgspec.structs.fields(model)
        ]
    except NameError as e:
        model_full_name = FullyQualifiedName.from_object(model)
        forward_ref = getattr(
            e,
            "name",
            re.search(r"(?<=')(?:[^'])*(?=')", str(e)).group(0),  # type: ignore [union-attr]
        )
        msg = (
            f"Failed to resolve forward reference '{forward_ref}' in the type annotations for "
            f"struct {model_full_name}. "
            "erdantic does not currently support manually resolving forward references for "
            "structs."
        )
        raise UnresolvableForwardRefError(
            msg, name=forward_ref, model_full_name=model_full_name
        ) from e


register_plugin(
    key="msgspec", predicate_fn=is_msgspec_struct, get_fields_fn=get_fields_from_msgspec_struct
)
