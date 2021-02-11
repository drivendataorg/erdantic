import collections.abc
import dataclasses
from typing import Any, List, Union


from erdantic.base import Field, Model, register_model_adapter
from erdantic.typing import GenericAlias, get_args, get_origin


class DataClassField(Field[dataclasses.Field]):
    """Concrete field adapter class for dataclass fields.

    Attributes:
        field (dataclasses.Field): The dataclass field instance that is associated with this
            adapter instance
    """

    def __init__(self, field: dataclasses.Field):
        if not isinstance(field, dataclasses.Field):
            raise ValueError(f"field must be of type dataclasses.Field. Got: {type(field)}")
        super().__init__(field=field)

    @property
    def name(self) -> str:
        return self.field.name

    @property
    def type_obj(self) -> Union[type, GenericAlias]:
        return self.field.type

    def is_many(self) -> bool:
        origin = get_origin(self.type_obj)
        return isinstance(origin, type) and (
            issubclass(origin, collections.abc.Container)
            or issubclass(origin, collections.abc.Iterable)
            or issubclass(origin, collections.abc.Sized)
        )

    def is_nullable(self) -> bool:
        return get_origin(self.type_obj) is Union and type(None) in get_args(self.type_obj)


@register_model_adapter("dataclasses")
class DataClassModel(Model[type]):
    """Concrete model adapter class for a
    [`dataclasses` module](https://docs.python.org/3/library/dataclasses.html) dataclass.

    Attributes:
        model (type): The dataclass that is associated with this adapter instance
    """

    def __init__(self, model: type):
        if not self.is_model_type(model):
            raise ValueError(f"Argument model must be a dataclass: {repr(model)}")
        super().__init__(model=model)

    @staticmethod
    def is_model_type(obj: Any) -> bool:
        return isinstance(obj, type) and dataclasses.is_dataclass(obj)

    @property
    def fields(self) -> List[Field]:
        return [DataClassField(field=f) for f in dataclasses.fields(self.model)]
