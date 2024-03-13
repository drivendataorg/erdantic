import importlib.metadata
import logging
from typing import TYPE_CHECKING, Any, List, Optional, Protocol, Sequence, TypeGuard, TypeVar

from typenames import typenames

if TYPE_CHECKING:
    from erdantic.core import FieldInfo

logger = logging.getLogger(__name__)

CORE_PLUGINS = ("pydantic", "attrs", "dataclasses")

_ModelType = TypeVar("_ModelType", bound=type)
_ModelType_co = TypeVar("_ModelType_co", bound=type, covariant=True)
_ModelType_contra = TypeVar("_ModelType_contra", bound=type, contravariant=True)


def load_plugins():
    for plugin in CORE_PLUGINS:
        logger.debug("Loading plugin: %s", plugin)
        importlib.import_module(f"erdantic.plugins.{plugin}")


class ModelPredicate(Protocol[_ModelType_co]):
    """"""

    def __call__(self, obj: Any) -> TypeGuard[_ModelType_co]:
        """"""


class ModelFieldExtractor(Protocol[_ModelType_contra]):
    """"""

    def __call__(self, model: _ModelType_contra) -> Sequence["FieldInfo"]:
        """"""


_dict = {}


def register_plugin(
    key: str,
    predicate_fn: ModelPredicate[_ModelType],
    get_fields_fn: ModelFieldExtractor[_ModelType],
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
    for key, (predicate_fn, get_fields_fn) in _dict.items():
        if predicate_fn(tp):
            logger.debug("Identified '%s' as a '%s' model.", typenames(tp), key)
            return get_fields_fn
    return None
