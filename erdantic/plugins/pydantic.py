from typing import Any, List, Optional, Type, TypeGuard

import pydantic
import pydantic.v1

from erdantic.core import FieldInfo, FullyQualifiedName
from erdantic.plugins import register_plugin

## Pydantic v2

PydanticModel = Type[pydantic.BaseModel]


def is_pydantic_model(obj: Any) -> TypeGuard[PydanticModel]:
    return isinstance(obj, type) and issubclass(obj, pydantic.BaseModel)


def get_fields_from_pydantic_model(model: PydanticModel) -> List[FieldInfo]:
    return [
        FieldInfo.from_raw_type(
            model_full_name=FullyQualifiedName.from_object(model),
            name=name,
            raw_type=field_info.annotation,
        )
        for name, field_info in model.model_fields.items()
    ]


register_plugin(
    key="pydantic", predicate_fn=is_pydantic_model, get_fields_fn=get_fields_from_pydantic_model
)

## Pydantic v1 legacy

PydanticV1Model = Type[pydantic.v1.BaseModel]


def is_pydantic_v1_model(obj) -> TypeGuard[PydanticV1Model]:
    return isinstance(obj, type) and issubclass(obj, pydantic.v1.BaseModel)


def get_fields_from_pydantic_v1_model(model: PydanticV1Model) -> List[FieldInfo]:
    return [
        FieldInfo.from_raw_type(
            model_full_name=FullyQualifiedName.from_object(model),
            name=name,
            raw_type=get_type_annotation_from_pydantic_v1_field(field),
        )
        for name, field in model.__fields__.items()
    ]


def get_type_annotation_from_pydantic_v1_field(field_info: pydantic.v1.fields.ModelField) -> type:
    tp = field_info.outer_type_
    if field_info.allow_none:
        return Optional[tp]
    return tp


register_plugin(
    key="pydantic_v1",
    predicate_fn=is_pydantic_v1_model,
    get_fields_fn=get_fields_from_pydantic_v1_model,
)
