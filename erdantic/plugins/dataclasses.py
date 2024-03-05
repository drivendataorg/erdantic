import dataclasses
from typing import TYPE_CHECKING, Any, List, Type, TypeGuard

from erdantic.core import FieldInfo, FullyQualifiedName
from erdantic.plugins import register_plugin

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


DataclassType = Type["DataclassInstance"]


def is_dataclass_type(obj: Any) -> TypeGuard[DataclassType]:
    return isinstance(obj, type) and dataclasses.is_dataclass(obj)


def get_fields_from_dataclass(model: DataclassType) -> List[FieldInfo]:
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
