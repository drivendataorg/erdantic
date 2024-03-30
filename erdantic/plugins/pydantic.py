import re
import sys
from typing import Any, List, Optional, Type

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard

import pydantic
import pydantic.v1

from erdantic.core import FieldInfo, FullyQualifiedName
from erdantic.exceptions import UnresolvableForwardRefError
from erdantic.plugins import register_plugin

## Pydantic v2

PydanticModel = Type[pydantic.BaseModel]


def is_pydantic_model(obj: Any) -> TypeGuard[PydanticModel]:
    """Predicate function to determine if an object is a Pydantic model (not an instance).

    Args:
        obj (Any): The object to check.

    Returns:
        bool: True if the object is a Pydantic model, False otherwise.
    """
    return isinstance(obj, type) and issubclass(obj, pydantic.BaseModel)


def get_fields_from_pydantic_model(model: PydanticModel) -> List[FieldInfo]:
    """Given a Pydantic model, return a list of FieldInfo instances for each field in the model.

    Args:
        model (PydanticModel): The Pydantic model to get fields from.

    Returns:
        List[FieldInfo]: List of FieldInfo instances for each field in the model
    """
    try:
        # Rebuild model schema to resolve forward references
        model.model_rebuild()
    except pydantic.errors.PydanticUndefinedAnnotation as e:
        model_full_name = FullyQualifiedName.from_object(model)
        forward_ref = e.name
        msg = (
            f"Failed to resolve forward reference '{forward_ref}' in the type annotations for "
            f"Pydantic model {model_full_name}. "
            "You should use the model's model_rebuild() method to manually resolve it."
        )
        raise UnresolvableForwardRefError(
            msg, name=forward_ref, model_full_name=model_full_name
        ) from e
    return [
        FieldInfo.from_raw_type(
            model_full_name=FullyQualifiedName.from_object(model),
            name=name,
            # typing special forms currently get typed as object
            # https://github.com/python/mypy/issues/9773
            raw_type=pydantic_field_info.annotation or Any,  # type: ignore
        )
        for name, pydantic_field_info in model.model_fields.items()
    ]


register_plugin(
    key="pydantic", predicate_fn=is_pydantic_model, get_fields_fn=get_fields_from_pydantic_model
)

## Pydantic v1 legacy

PydanticV1Model = Type[pydantic.v1.BaseModel]


def is_pydantic_v1_model(obj) -> TypeGuard[PydanticV1Model]:
    """Predicate function to determine if an object is a Pydantic V1 model (not an instance). This
    is for models that use the legacy `pydantic.v1` namespace.

    Args:
        obj (Any): The object to check.

    Returns:
        bool: True if the object is a Pydantic V1 model, False otherwise.
    """
    return isinstance(obj, type) and issubclass(obj, pydantic.v1.BaseModel)


def get_fields_from_pydantic_v1_model(model: PydanticV1Model) -> List[FieldInfo]:
    """Given a Pydantic V1 model, return a list of FieldInfo instances for each field in the model.

    Args:
        model (PydanticV1Model): The Pydantic V1 model to get fields from.

    Returns:
        List[FieldInfo]: List of FieldInfo instances for each field in the model
    """
    try:
        model.update_forward_refs()
    except NameError as e:
        model_full_name = FullyQualifiedName.from_object(model)
        # NameError attribute 'name' was added in Python 3.10
        forward_ref = getattr(
            e,
            "name",
            re.search(r"(?<=')(?:[^'])*(?=')", str(e)).group(0),  # type: ignore [union-attr]
        )
        msg = (
            f"Failed to resolve forward reference '{forward_ref}' in the type annotations for "
            f"Pydantic V1 model {model_full_name}. "
            "You should call the method update_forward_refs(**locals()) on the model in "
            "the scope where it has been defined to manually resolve it."
        )
        raise UnresolvableForwardRefError(
            msg, name=forward_ref, model_full_name=model_full_name
        ) from e

    return [
        FieldInfo.from_raw_type(
            model_full_name=FullyQualifiedName.from_object(model),
            name=name,
            raw_type=get_type_annotation_from_pydantic_v1_field(field),
        )
        for name, field in model.__fields__.items()
    ]


def get_type_annotation_from_pydantic_v1_field(field_info: pydantic.v1.fields.ModelField) -> type:
    """Utility function to get the type annotation from a Pydantic V1 field info object."""
    tp = field_info.outer_type_
    if field_info.allow_none:
        return Optional[tp]  # type: ignore
    return tp


register_plugin(
    key="pydantic_v1",
    predicate_fn=is_pydantic_v1_model,
    get_fields_fn=get_fields_from_pydantic_v1_model,
)
