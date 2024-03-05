from typing import Any, List, Type, TypeGuard

import attrs

from erdantic.core import FieldInfo, FullyQualifiedName
from erdantic.plugins import register_plugin

AttrsClassType = Type[attrs.AttrsInstance]


def is_attrs_class(obj: Any) -> TypeGuard[AttrsClassType]:
    return isinstance(obj, type) and attrs.has(obj)


def get_fields_from_attrs_class(model: AttrsClassType) -> List[FieldInfo]:
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
