from typing import Any, List, Type

import pydantic
import pydantic.fields

from erdantic.base import Field, Model, register_model_adapter
from erdantic.typing import repr_type_with_mro


class PydanticField(Field):

    field: pydantic.fields.ModelField

    def __init__(self, field: Any):
        if not isinstance(field, pydantic.fields.ModelField):
            raise ValueError(
                f"field must be of type pydantic.fields.ModelField. Got: {type(field)}"
            )
        self.field = field

    @property
    def name(self) -> str:
        return self.field.name

    @property
    def type_obj(self) -> type:
        return self.field.type_

    def is_many(self) -> bool:
        return self.field.shape > 1

    def is_nullable(self) -> bool:
        return self.field.allow_none


@register_model_adapter("pydantic")
class PydanticModel(Model):
    model: Type[pydantic.BaseModel]

    def __init__(self, model: Any):
        if not self.is_type(model):
            raise ValueError(
                "Argument model must be a subclass of pydantic.BaseModel. "
                f"Got {repr_type_with_mro(model)}"
            )
        self.model = model

    @staticmethod
    def is_type(obj: Any) -> bool:
        return isinstance(obj, type) and issubclass(obj, pydantic.BaseModel)

    @property
    def fields(self) -> List[Field]:
        return [PydanticField(field=f) for f in self.model.__fields__.values()]
