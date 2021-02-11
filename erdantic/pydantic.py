from typing import Any, List, Optional, Union, Type

import pydantic
import pydantic.fields

from erdantic.base import Field, Model, register_model_adapter
from erdantic.typing import GenericAlias, repr_type_with_mro


class PydanticField(Field[pydantic.fields.ModelField]):
    """Concrete field adapter class for Pydantic fields.

    Attributes:
        field (pydantic.fields.ModelField): The Pydantic field object that is associated with this
            adapter instance
    """

    def __init__(self, field: pydantic.fields.ModelField):
        if not isinstance(field, pydantic.fields.ModelField):
            raise ValueError(
                f"field must be of type pydantic.fields.ModelField. Got: {type(field)}"
            )
        super().__init__(field=field)

    @property
    def name(self) -> str:
        return self.field.name

    @property
    def type_obj(self) -> Union[type, GenericAlias]:
        tp = self.field.outer_type_
        if self.field.allow_none:
            return Optional[tp]
        return tp

    def is_many(self) -> bool:
        return self.field.shape > 1

    def is_nullable(self) -> bool:
        return self.field.allow_none


@register_model_adapter("pydantic")
class PydanticModel(Model[Type[pydantic.BaseModel]]):
    """Concrete model adapter class for a Pydantic
    [`BaseModel`](https://pydantic-docs.helpmanual.io/usage/models/).

    Attributes:
        model (Type[pydantic.BaseModel]): The Pydantic model class that is associated with this
            adapter instance
    """

    def __init__(self, model: Type[pydantic.BaseModel]):
        if not self.is_model_type(model):
            raise ValueError(
                "Argument model must be a subclass of pydantic.BaseModel. "
                f"Got {repr_type_with_mro(model)}"
            )
        super().__init__(model=model)

    @staticmethod
    def is_model_type(obj: Any) -> bool:
        return isinstance(obj, type) and issubclass(obj, pydantic.BaseModel)

    @property
    def fields(self) -> List[Field]:
        return [PydanticField(field=f) for f in self.model.__fields__.values()]
