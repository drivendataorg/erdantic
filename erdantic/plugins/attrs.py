from typing import Any, Dict, Type, TypeGuard

import attrs

from erdantic.plugins import registry
from erdantic.core import FieldInfo, FullyQualifiedName

AttrsClassType = Type[attrs.AttrsInstance]


def is_attrs_class(obj: Any) -> TypeGuard[AttrsClassType]:
    return isinstance(obj, type) and attrs.has(obj)


def get_fields_from_attrs_class(model: AttrsClassType) -> Dict[str, FieldInfo]:
    return {
        attrib.name: FieldInfo.from_raw_type(
            model_full_name=FullyQualifiedName.from_object(model),
            name=attrib.name,
            raw_type=attrib.type,
        )
        for attrib in attrs.fields(model)
    }


registry.register(
    key="attrs", predicate_fn=is_attrs_class, get_fields_fn=get_fields_from_attrs_class
)
