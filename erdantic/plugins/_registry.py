import importlib.metadata
import logging
from typing import TYPE_CHECKING, Any, List, Optional, Protocol, Sequence, TypeGuard

from erdantic.typing_utils import ModelType

if TYPE_CHECKING:
    from erdantic.core import FieldInfo

logger = logging.getLogger(__name__)

CORE_PLUGINS = ("pydantic", "attrs", "dataclasses")


def load_plugins():
    for plugin in CORE_PLUGINS:
        logger.debug("Loading plugin: %s", plugin)
        importlib.import_module(f"erdantic.plugins.{plugin}")


class ModelPredicate(Protocol[ModelType]):
    """"""

    def __call__(self, obj: Any) -> TypeGuard[ModelType]:
        """"""


class ModelFieldExtractor(Protocol[ModelType]):
    """"""

    def __call__(self, model: ModelType) -> Sequence["FieldInfo"]:
        """"""


_dict = {}


def register_plugin(
    key: str,
    predicate_fn: ModelPredicate[ModelType],
    get_fields_fn: ModelFieldExtractor[ModelType],
):
    if key in _dict:
        logger.warn("Overwriting existing implementation for key '%s'", key)
    _dict[key] = (predicate_fn, get_fields_fn)


def list_keys() -> List[str]:
    return list(_dict.keys())


def get_predicate_fn(key: str) -> ModelPredicate:
    return _dict[key][0]


def get_field_extractor_fn(key: str) -> ModelFieldExtractor:
    return _dict[key][1]


def identify_field_extractor_fn(tp: type) -> Optional[ModelFieldExtractor]:
    for predicate_fn, get_fields_fn in _dict.values():
        if predicate_fn(tp):
            return get_fields_fn
    return None
