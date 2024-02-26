import dataclasses
from typing import TYPE_CHECKING, Any, Dict, Type, TypeGuard

import typenames

from erdantic.refactor.core import FieldInfo, FullyQualifiedName, registry

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


DataclassType = Type["DataclassInstance"]


def is_dataclass_type(obj: Any) -> TypeGuard[DataclassType]:
    return isinstance(obj, type) and dataclasses.is_dataclass(obj)


def get_fields_from_dataclass(model: DataclassType) -> Dict[str, FieldInfo]:
    return {
        f.name: FieldInfo.from_raw_type(
            model_full_name=FullyQualifiedName.from_object(f),
            name=f.name,
            raw_type=f.type,
        )
        for f in dataclasses.fields(model)
    }


registry.register(predicate_fn=is_dataclass_type, get_fields_fn=get_fields_from_dataclass)
