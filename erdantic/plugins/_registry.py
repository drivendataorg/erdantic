import importlib.metadata
import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Protocol, Tuple, TypeGuard

from erdantic.typing import ModelType

if TYPE_CHECKING:
    from erdantic.core import FieldInfo

logger = logging.getLogger(__name__)


def load_plugins():
    entry_points = importlib.metadata.entry_points(group="erdantic")
    for entry_point in entry_points:
        logger.debug("Loading plugin: %s", entry_point.name)
        entry_point.load()


class ModelPredicate(Protocol[ModelType]):
    """"""

    def __call__(self, obj: Any) -> TypeGuard[ModelType]:
        """"""


class ModelFieldExtractor(Protocol[ModelType]):
    """"""

    def __call__(self, model: ModelType) -> Dict[str, "FieldInfo"]:
        """"""


class Registry:
    _dict: Dict[str, Tuple[ModelPredicate, ModelFieldExtractor]]

    def __init__(self) -> None:
        self._dict = {}

    def __getitem__(self, key: str):
        return self._dict[key]

    def keys(self):
        return list(self._dict.keys())

    def register(self, key: str, predicate_fn: ModelPredicate, get_fields_fn: ModelFieldExtractor):
        if key in self._dict:
            logger.warn("Overwriting existing implementation for key '%s'", key)
        self._dict[key] = (predicate_fn, get_fields_fn)

    def get_field_extractor_fn(
        self, tp: type, limit_types_to=None
    ) -> Optional[ModelFieldExtractor]:
        for key, (predicate_fn, get_fields_fn) in self._dict.items():
            if limit_types_to and key not in limit_types_to:
                continue
            if predicate_fn(tp):
                return get_fields_fn
        return None


registry = Registry()
