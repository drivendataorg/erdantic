import collections.abc
import dataclasses
import inspect
from typing import Any, List, Union


from erdantic.base import Field, Model, register_model_adapter
from erdantic.typing import get_args, get_origin


class DataClassField(Field):
    dataclass_field: dataclasses.Field

    def __init__(self, dataclass_field: dataclasses.Field):
        if not isinstance(dataclass_field, dataclasses.Field):
            raise ValueError(
                "dataclass_field must be of type dataclasses.Field. "
                f"Got: {type(dataclass_field)}"
            )
        self.dataclass_field = dataclass_field

    @property
    def name(self) -> str:
        return self.dataclass_field.name

    @property
    def type_obj(self) -> type:
        return self.dataclass_field.type

    def is_many(self) -> bool:
        origin = get_origin(self.type_obj)
        return isinstance(origin, type) and (
            issubclass(origin, collections.abc.Container)
            or issubclass(origin, collections.abc.Iterable)
            or issubclass(origin, collections.abc.Sized)
        )

    def is_nullable(self) -> bool:
        return get_origin(self.type_obj) is Union and type(None) in get_args(self.type_obj)

    def __hash__(self) -> int:
        return id(self.dataclass_field)


@register_model_adapter("dataclasses")
class DataClassModel(Model):
    dataclass: type

    def __init__(self, dataclass: type):
        if not self.is_type(dataclass):
            raise ValueError(f"Argument dataclass must be a dataclass. Got {dataclass}")
        self.dataclass = dataclass

    @staticmethod
    def is_type(obj: Any) -> bool:
        return isinstance(obj, type) and dataclasses.is_dataclass(obj)

    @property
    def name(self) -> str:
        return self.dataclass.__name__

    @property
    def fields(self) -> List[Field]:
        return [DataClassField(dataclass_field=f) for f in dataclasses.fields(self.dataclass)]

    @property
    def docstring(self) -> str:
        out = f"{self.dataclass.__module__}.{self.name}"
        docstring = inspect.getdoc(self.dataclass)
        if docstring:
            out += "\n\n" + docstring
        return out

    def __hash__(self) -> int:
        return id(self.dataclass)
