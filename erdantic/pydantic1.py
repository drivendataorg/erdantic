from typing import Any, List, Optional, Type, Union

import pydantic.v1
import pydantic.v1.fields

from erdantic.base import Field, Model, register_model_adapter
from erdantic.exceptions import InvalidFieldError, InvalidModelError
from erdantic.typing import GenericAlias, repr_type_with_mro


class Pydantic1Field(Field[pydantic.v1.fields.ModelField]):
    """Concrete field adapter class for Pydantic fields.

    Attributes:
        field (pydantic.fields.ModelField): The Pydantic field object that is associated with this
            adapter instance.
    """

    def __init__(self, field: pydantic.v1.fields.ModelField):
        if not isinstance(field, pydantic.v1.fields.ModelField):
            raise InvalidFieldError(
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


@register_model_adapter("pydantic1")
class PydanticModel(Model[Type[pydantic.v1.BaseModel]]):
    """Concrete model adapter class for a Pydantic
    [`BaseModel`](https://pydantic-docs.helpmanual.io/usage/models/).

    Attributes:
        model (Type[pydantic.BaseModel]): The Pydantic model class that is associated with this
            adapter instance.
        forward_ref_help (Optional[str]): Instructions for how to resolve an unevaluated forward
            reference in a field's type declaration.
    """

    forward_ref_help = (
        "Call 'update_forward_refs' after model is created to resolve. "
        "See: https://pydantic-docs.helpmanual.io/usage/postponed_annotations/"
    )

    def __init__(self, model: Type[pydantic.v1.BaseModel]):
        if not self.is_model_type(model):
            raise InvalidModelError(
                "Argument model must be a subclass of pydantic.v1.BaseModel. "
                f"Got {repr_type_with_mro(model)}"
            )
        super().__init__(model=model)

    @staticmethod
    def is_model_type(obj: Any) -> bool:
        return isinstance(obj, type) and issubclass(obj, pydantic.v1.BaseModel)

    @property
    def fields(self) -> List[Field]:
        return [Pydantic1Field(field=f) for f in self.model.__fields__.values()]

    @property
    def docstring(self) -> str:
        out = super().docstring
        field_descriptions = [
            getattr(field.field.field_info, "description", None) for field in self.fields
        ]
        if any(descr is not None for descr in field_descriptions):
            # Sometimes Pydantic models have field documentation as descriptions as metadata on the
            # field instead of in the docstring. If detected, construct docstring and add.
            out += "\nAttributes:\n"
            field_defaults = [field.field.field_info.default for field in self.fields]
            for field, descr, default in zip(self.fields, field_descriptions, field_defaults):
                if descr is not None:
                    line = f"{field.name} ({field.type_name}): {descr}"
                    if (
                        not isinstance(default, pydantic.v1.fields.UndefinedType)
                        and default is not ...
                    ):
                        if not line.strip().endswith("."):
                            line = line.rstrip() + ". "
                        else:
                            line = line.rstrip() + " "
                        if isinstance(default, str):
                            line += f"Default is '{default}'."
                        else:
                            line += f"Default is {default}."
                    out += "    " + line.strip() + "\n"

        return out
