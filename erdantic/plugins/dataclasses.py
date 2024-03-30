import dataclasses
import re
import sys
from typing import TYPE_CHECKING, Any, List, Type, get_type_hints

if sys.version_info >= (3, 9):
    # include_extras was added in Python 3.9
    from typing import get_type_hints
else:
    from typing_extensions import get_type_hints

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard

from erdantic.core import FieldInfo, FullyQualifiedName
from erdantic.exceptions import UnresolvableForwardRefError
from erdantic.plugins import register_plugin

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


DataclassType = Type["DataclassInstance"]


def is_dataclass_class(obj: Any) -> TypeGuard[DataclassType]:
    """Predicate function to determine if an object is a dataclass (not an instance).

    Args:
        obj (Any): The object to check.

    Returns:
        bool: True if the object is a dataclass, False otherwise.
    """
    return isinstance(obj, type) and dataclasses.is_dataclass(obj)


def get_fields_from_dataclass(model: DataclassType) -> List[FieldInfo]:
    """Given a dataclass, return a list of FieldInfo instances for each field in the class.

    Args:
        model (DataclassType): The dataclass to get fields from.

    Returns:
        List[FieldInfo]: List of FieldInfo instances for each field in the class
    """
    try:
        # Try to automatically resolve forward references
        resolve_types_on_dataclass(model)
    except NameError as e:
        model_full_name = FullyQualifiedName.from_object(model)
        forward_ref = getattr(
            e,
            "name",
            re.search(r"(?<=')(?:[^'])*(?=')", str(e)).group(0),  # type: ignore [union-attr]
        )
        msg = (
            f"Failed to resolve forward reference '{forward_ref}' in the type annotations for "
            f"dataclass {model_full_name}. "
            "You should use erdantic.plugins.dataclasses.resolve_types_on_dataclass with locals() "
            "where you define the class."
        )
        raise UnresolvableForwardRefError(
            msg, name=forward_ref, model_full_name=model_full_name
        ) from e
    return [
        FieldInfo.from_raw_type(
            model_full_name=FullyQualifiedName.from_object(model),
            name=f.name,
            raw_type=f.type,
        )
        for f in dataclasses.fields(model)
    ]


register_plugin(
    key="dataclasses", predicate_fn=is_dataclass_class, get_fields_fn=get_fields_from_dataclass
)


def resolve_types_on_dataclass(
    cls: DataclassType, globalns=None, localns=None, include_extras=True
) -> DataclassType:
    """Resolve forward references in type annotations on a dataclass. This will modify the fields
    metadata on the class to replace forward references with the actual types.

    Args:
        cls (DataclassType): The dataclass to resolve forward references on.
        globalns (Dict[str, Any] | None, optional): A global namespace to evaluate forward
            references against. Defaults to None.
        localns (Dict[str, Any] | None, optional): A local namespace to evaluate forward
            references against. Defaults to None.
        include_extras (bool, optional): Whether to keep extra metadata from `typing.Annotated`.
            Defaults to True.
    """
    # Cache whether we have already run this on a cls
    # Inspired by attrs.resolve_types
    if getattr(cls, "__erdantic_dataclass_types_resolved__", None) != cls:
        hints = get_type_hints(
            cls, globalns=globalns, localns=localns, include_extras=include_extras
        )
        for field in dataclasses.fields(cls):
            field.type = hints[field.name]
        # Use reference to cls as indicator in case of subclasses
        setattr(cls, "__erdantic_dataclass_types_resolved__", cls)
    return cls
