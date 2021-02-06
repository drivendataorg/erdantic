from typing import Any, List, Set, Type

import pydantic
import pydantic.fields

from erdantic.erd import (
    Edge,
    EntityRelationshipDiagram,
    Field,
    Model,
    register_constructor,
    register_type_checker,
)


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
    def type_name(self) -> str:
        return self.pydantic_field._type_display()

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
                "pydantic_model must be a subclass of pydantic.BaseModel. "
                f"Received: {repr(pydantic_model)}"
            )
        self.pydantic_model = pydantic_model

    @property
    def name(self) -> str:
        return self.pydantic_model.__name__

    @property
    def fields(self) -> List[Field]:
        return [PydanticField(pydantic_field=f) for f in self.pydantic_model.__fields__.values()]

    def __hash__(self) -> int:
        return id(self.pydantic_model)


@register_type_checker("pydantic")
def is_pydantic_model(obj: Any):
    return issubclass(obj, pydantic.BaseModel)


@register_constructor("pydantic")
def create(*models: Type[pydantic.BaseModel]) -> EntityRelationshipDiagram:
    seen_models: Set[PydanticModel] = set()
    seen_edges: Set[Edge] = set()
    for model in models:
        search_composition_graph(model, seen_models, seen_edges)
    return EntityRelationshipDiagram(models=seen_models, edges=seen_edges)


def search_composition_graph(
    pydantic_model: Type[pydantic.BaseModel],
    seen_models: Set[PydanticModel],
    seen_edges: Set[Edge],
) -> Model:
    model = PydanticModel(pydantic_model=pydantic_model)
    if model not in seen_models:
        seen_models.add(model)
        for field in model.fields:
            if issubclass(field.type_obj, pydantic.BaseModel):
                field_model = search_composition_graph(field.type_obj, seen_models, seen_edges)
                seen_edges.add(Edge(source=model, source_field=field, target=field_model))
    return model
