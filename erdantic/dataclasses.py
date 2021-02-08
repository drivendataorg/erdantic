import collections.abc
import dataclasses
import inspect
from typing import Any, List, Set, Union


from erdantic.base import DiagramFactory, Field, Model, register_factory
from erdantic.erd import Edge, EntityRelationshipDiagram
from erdantic.typing import GenericAlias, get_args, get_origin


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


class DataClassModel(Model):
    dataclass: type

    def __init__(self, dataclass: type):
        if not is_dataclass(dataclass):
            raise ValueError(f"Argument dataclass must be a dataclass. Got {dataclass}")
        self.dataclass = dataclass

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


@register_factory("dataclasses")
class DataClassDiagramFactory(DiagramFactory):
    @staticmethod
    def is_type(model: type) -> bool:
        return is_dataclass(model)

    @staticmethod
    def create(*models: type) -> EntityRelationshipDiagram:
        seen_models: Set[DataClassModel] = set()
        seen_edges: Set[Edge] = set()
        for model in models:
            search_composition_graph(model, seen_models, seen_edges)
        return EntityRelationshipDiagram(models=list(seen_models), edges=list(seen_edges))


def is_dataclass(obj: Any) -> bool:
    return isinstance(obj, type) and dataclasses.is_dataclass(obj)


def search_composition_graph(
    dataclass: type, seen_models: Set[DataClassModel], seen_edges: Set[Edge]
) -> DataClassModel:
    model = DataClassModel(dataclass=dataclass)
    if model not in seen_models:
        seen_models.add(model)
        for field in model.fields:
            # field is a dataclass
            if is_dataclass(field.type_obj):
                field_model = search_composition_graph(field.type_obj, seen_models, seen_edges)
                seen_edges.add(Edge(source=model, source_field=field, target=field_model))
            # field is a generic, check if it contains a dataclass
            if (
                isinstance(field.type_obj, GenericAlias)
                or getattr(field.type_obj, "__origin__", None) is Union  # Python 3.6 compat
            ):
                for arg in get_args(field.type_obj):
                    if is_dataclass(arg):
                        field_model = search_composition_graph(arg, seen_models, seen_edges)
                        seen_edges.add(Edge(source=model, source_field=field, target=field_model))
    return model
