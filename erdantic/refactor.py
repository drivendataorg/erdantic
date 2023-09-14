from enum import Enum
from dataclasses import dataclass
from typing import Callable, Generic, Iterator, List, Optional, Tuple, TypeVar, Union

from erdantic.typing import is_nullable_type, is_collection_type, TypeAnnotation
from erdantic.exceptions import (
    _StringForwardRefError,
    _UnevaluatedForwardRefError,
    StringForwardRefError,
    UnevaluatedForwardRefError,
)


class Cardinality(Enum):
    ONE = "one"
    MANY = "many"


class Modality(Enum):
    ZERO = "zero"
    ONE = "one"


@dataclass
class FieldInfo:
    name: str
    type_obj: TypeAnnotation
    type_name: str

    @property
    def is_collection(self) -> bool:
        return is_collection_type(self.type_obj)

    @property
    def is_nullable(self) -> bool:
        return is_nullable_type(self.type_obj)


ModelType = TypeVar("ModelType")


@dataclass
class ModelInfo(Generic[ModelType]):
    raw: ModelType
    name: str
    fields: List[FieldInfo]
    docstring: str


@dataclass
class Edge:
    source_field: FieldInfo
    target_model: ModelInfo
    target_cardinality: Cardinality
    target_modality: Modality
    source_cardinality: Optional[Cardinality] = None
    source_modality: Optional[Modality] = None


# Steps
# Create FieldInfo for all fields
# Create ModelInfo
# Create Edges
# Recurse Edge targets

ModelAnalyzer: Callable[[ModelType], ModelInfo[ModelType]]
ModelPredicate: Callable[[type], TypeGuard]


def analyze_dataclass_model(model: ModelType) -> ModelInfo[ModelType]:
    pass


def is_dataclass(obj):
    return True


@dataclass
class Graph:
    models: Dict[type, ModelInfo]
    edges: List[Edge]

    @property
    def nodes(self):
        return tuple(self.models.values())

    @classmethod
    def from_models(cls, models: type):
        pass

    def search(self, model):
        if model not in self.models:
            model_info = analyze_model(model)
            self.models[model] = model_info
            for field_info in model_info.fields:
                try:
                    for arg in get_recursive_args(field_info.type_obj):
                        try:
                            field_model = self.search(arg)
                            self.edges.add(
                                Edge(
                                    source_field=field_info,
                                    target_model=field_model,
                                    target_cardinality=0,
                                    target_modality=0,
                                )
                            )
                        except UnknownModelTypeError:
                            pass
                except _UnevaluatedForwardRefError as e:
                    raise UnevaluatedForwardRefError(
                        model=model, field=field_info, forward_ref=e.forward_ref
                    ) from None
                except _StringForwardRefError as e:
                    raise StringForwardRefError(
                        model=model, field=field_info, forward_ref=e.forward_ref
                    ) from None
        return model_info
