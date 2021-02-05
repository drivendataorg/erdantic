import collections.abc
import dataclasses
from typing import Any, List, Set, Union, _GenericAlias as GenericAlias

try:
    from typing import get_args, get_origin
except ImportError:
    from typing_extensions import get_args, get_origin

from erdantic.erd import (
    Edge,
    EntityRelationshipDiagram,
    Field,
    Model,
    register_constructor,
    register_type_checker,
)


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
    def type_name(self) -> str:
        if hasattr(self.type_obj, "__name__"):
            return self.type_obj.__name__
        return str(self.type_obj).replace("typing.", "").replace("__main__.", "")

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

    def __repr__(self) -> str:
        return f"DataClassField(dataclass_field={self.dataclass_field})"


class DataClassModel(Model):
    dataclass: type

    def __init__(self, dataclass: type):
        if not is_dataclass(dataclass):
            raise ValueError(f"input must be a dataclass. Got {dataclass}")
        self.dataclass = dataclass

    @property
    def name(self) -> str:
        return self.dataclass.__name__

    @property
    def fields(self) -> List[Field]:
        return [DataClassField(dataclass_field=f) for f in dataclasses.fields(self.dataclass)]

    def __hash__(self) -> int:
        return id(self.dataclass)

    def __repr__(self) -> str:
        return f"DataClassModel(dataclass={self.dataclass})"


@register_type_checker("dataclass")
def is_dataclass(obj: Any) -> bool:
    return isinstance(obj, type) and dataclasses.is_dataclass(obj)


@register_constructor("dataclass")
def create_erd(*models: type) -> EntityRelationshipDiagram:
    seen_models: Set[DataClassModel] = set()
    seen_edges: Set[Edge] = set()
    for model in models:
        search_composition_graph(model, seen_models, seen_edges)
    return EntityRelationshipDiagram(models=seen_models, edges=seen_edges)


def search_composition_graph(
    dataclass: type, seen_models: Set[DataClassModel], seen_edges: Set[Edge]
) -> Model:
    model = DataClassModel(dataclass=dataclass)
    if model not in seen_models:
        seen_models.add(model)
        for field in model.fields:
            if is_dataclass(field.type_obj):
                field_model = search_composition_graph(field.type_obj, seen_models, seen_edges)
                seen_edges.add(Edge(source=model, source_field=field, target=field_model))
            if isinstance(field.type_obj, GenericAlias):
                for arg in get_args(field.type_obj):
                    if is_dataclass(arg):
                        field_model = search_composition_graph(arg, seen_models, seen_edges)
                        seen_edges.add(Edge(source=model, source_field=field, target=field_model))
    return model
