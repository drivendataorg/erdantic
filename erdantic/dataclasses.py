import dataclasses
from typing import Any, List, Union


from erdantic.base import Field, Model, register_model_adapter
from erdantic.exceptions import InvalidFieldError, InvalidModelError
from erdantic.typing import GenericAlias, is_many, is_nullable


class DataClassField(Field[dataclasses.Field]):
    """Concrete field adapter class for dataclass fields.

    Attributes:
        field (dataclasses.Field): The dataclass field instance that is associated with this
            adapter instance.
    """

    def __init__(self, field: dataclasses.Field):
        if not isinstance(field, dataclasses.Field):
            raise InvalidFieldError(f"field must be of type dataclasses.Field. Got: {type(field)}")
        super().__init__(field=field)

    @property
    def name(self) -> str:
        return self.field.name

    @property
    def type_obj(self) -> Union[type, GenericAlias]:
        return self.field.type

    def is_many(self) -> bool:
        return is_many(self.type_obj)

    def is_nullable(self) -> bool:
        return is_nullable(self.type_obj)


@register_model_adapter("dataclasses")
class DataClassModel(Model[type]):
    """Concrete model adapter class for a
    [`dataclasses` module](https://docs.python.org/3/library/dataclasses.html) dataclass.

    Attributes:
        model (type): The dataclass that is associated with this adapter instance.
        forward_ref_help (Optional[str]): Instructions for how to resolve an unevaluated forward
            reference in a field's type declaration.
    """

    forward_ref_help = (
        "Call 'typing.get_type_hints' on your dataclass after creating it to resolve."
    )

    def __init__(self, model: type):
        if not self.is_model_type(model):
            raise InvalidModelError(f"Argument model must be a dataclass: {repr(model)}")
        super().__init__(model=model)

    @staticmethod
    def is_model_type(obj: Any) -> bool:
        return isinstance(obj, type) and dataclasses.is_dataclass(obj)

    @property
    def fields(self) -> List[Field]:
        return [DataClassField(field=f) for f in dataclasses.fields(self.model)]
