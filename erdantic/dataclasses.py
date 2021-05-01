import collections.abc
import dataclasses
import inspect
import typing_inspect

from typing import Any, Callable, List, Union


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


@dataclasses.dataclass
class Edge:
    edge_name: str
    edge_func: Callable


class DataClassEdge(DataClassField):
    """Concrete field adapter class for fquery edges

    Attributes:
        edge (Edge): The fquery edge instance that is associated with this
            adapter instance
    """

    def __init__(self, edge: Edge):
        if not isinstance(edge, Edge):
            raise ValueError(f"edge must be of type Edge. Got: {type(edge)}")

        ret = inspect.signature(edge.edge_func._old)
        globalns = getattr(edge.edge_func._old, "__globals__", {})

        def recursive_eval(arg, globalns):
            ret = eval(arg, globalns)
            if typing_inspect.is_generic_type(ret):
                ret.__args__ = tuple(
                    [
                        r._evaluate(globalns, localns=None) if hasattr(r, "_evaluate") else r
                        for r in ret.__args__
                    ]
                )
            return ret

        # Use https://bugs.python.org/issue43817 when it's available
        return_type = recursive_eval(ret.return_annotation, globalns)

        tmp = dataclasses.make_dataclass("tmp", [(f"{edge.edge_name}", return_type)])
        field = dataclasses.fields(tmp)[0]
        super().__init__(field=field)

    def __hash__(self):
        return hash(self.name) ^ hash(self.type_name)


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
        members = inspect.getmembers(self.model, predicate=inspect.isfunction)
        edges = [
            DataClassEdge(Edge(ename, efunc))
            for ename, efunc in members
            if hasattr(efunc, "_edge")
        ]
        return [DataClassField(field=f) for f in dataclasses.fields(self.model)] + edges
