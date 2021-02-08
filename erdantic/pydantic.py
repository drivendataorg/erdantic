import inspect
from typing import Any, List, Type

import pydantic
import pydantic.fields

from erdantic.base import Adapter, Field, Model, register_adapter


class PydanticField(Field):
    pydantic_field: pydantic.fields.ModelField

    def __init__(self, pydantic_field):
        if not isinstance(pydantic_field, pydantic.fields.ModelField):
            raise ValueError(
                "pydantic_field must be of type pydantic.fields.ModelField. "
                f"Got: {type(pydantic_field)}"
            )
        self.pydantic_field = pydantic_field

    @property
    def name(self) -> str:
        return self.pydantic_field.name

    @property
    def type_obj(self) -> type:
        return self.pydantic_field.type_

    def is_many(self) -> bool:
        return self.pydantic_field.shape > 1

    def is_nullable(self) -> bool:
        return self.pydantic_field.allow_none

    def __hash__(self) -> int:
        return id(self.pydantic_field)


class PydanticModel(Model):
    pydantic_model: Type[pydantic.BaseModel]

    def __init__(self, pydantic_model: Type[pydantic.BaseModel]):
        if not isinstance(pydantic_model, type) or not issubclass(
            pydantic_model, pydantic.BaseModel
        ):
            raise ValueError(
                "Argument pydantic_model must be a subclass of pydantic.BaseModel. "
                f"Received: {repr(pydantic_model)}"
            )
        self.pydantic_model = pydantic_model

    @property
    def name(self) -> str:
        return self.pydantic_model.__name__

    @property
    def fields(self) -> List[Field]:
        return [PydanticField(pydantic_field=f) for f in self.pydantic_model.__fields__.values()]

    @property
    def docstring(self) -> str:
        out = f"{self.pydantic_model.__module__}.{self.name}"
        docstring = inspect.getdoc(self.pydantic_model)
        if docstring:
            out += "\n\n" + docstring
        return out

    def __hash__(self) -> int:
        return id(self.pydantic_model)


@register_adapter("pydantic")
class PydanticAdapter(Adapter):
    @staticmethod
    def is_type(obj: Any) -> bool:
        return isinstance(obj, type) and issubclass(obj, pydantic.BaseModel)

    @property
    def model_class(self) -> Type[Model]:
        return PydanticModel
