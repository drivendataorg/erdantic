import sys
from typing import (
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    from erdantic.core import FullyQualifiedName


def _to_full_name(obj: Any) -> str:
    """Convenience function to return fully qualified name of object as string."""
    return f"{obj.__module__}.{obj.__qualname__}"


class ErdanticException(Exception):
    """Base class for all exceptions from erdantic library."""


class PluginNotFoundError(KeyError, ErdanticException):
    """Raised when specified plugin key does not match a registered plugin."""

    def __init__(self, *args: object, key: str) -> None:
        self.key = key
        message = f"Specified plugin not found: '{key}'"
        super().__init__(*args, message)


class ModelOrModuleNotFoundError(ImportError, ErdanticException):
    """Raised when specified fully qualified name of model class or module cannot be imported."""


class UnresolvableForwardRefError(NameError, ErdanticException):
    def __init__(
        self,
        *args: object,
        name: str,
    ) -> None:
        if sys.version_info >= (3, 10):
            super().__init__(*args, name=name)
        else:
            super().__init__(*args)
            self.name = name


class UnevaluatedForwardRefError(ErdanticException):
    """Raised when a field's type declaration has an unevaluated forward reference."""

    def __init__(
        self,
        *args: object,
        model_full_name: "FullyQualifiedName",
        field_name: str,
        forward_ref: str,
    ) -> None:
        self.model_full_name = model_full_name
        self.field_name = field_name
        self.forward_ref = forward_ref
        message = (
            f"Unevaluated forward reference '{forward_ref}' "
            f"for field '{field_name}' on model '{model_full_name}'. "
            "Normally, erdantic plugins try to resolve forward references, and this error "
            "indicates that this didn't happen. If you are using a built-in plugin, please report "
            "this as a bug. If you are using a custom or third-party plugin, then that plugin "
            "needs to add support for resolving forward references. "
        )
        super().__init__(*args, message)


class _UnevaluatedForwardRefError(ErdanticException):
    """Internal exception for unevaluated forward references that is caught and raised instead
    as UnevaluatedForwardRefError."""

    def __init__(self, *args, forward_ref: str) -> None:
        self.forward_ref = forward_ref
        super().__init__(*args, "Unexpected error while flagging unevaluated forward reference.")


class FieldNotFoundError(AttributeError, ErdanticException):
    """Raised trying to access a field name that does not match any fields returned by the
    field extractor function for a model."""

    def __init__(self, *args, name: str, obj: object, model_full_name: "FullyQualifiedName"):
        self.model_full_name = model_full_name
        msg = f"Model '{self.model_full_name}' has no field '{self.name}'."
        if sys.version_info >= (3, 10):
            super().__init__(*args, msg, name=name, obj=obj)
        else:
            self.name = name
            self.obj = obj
            super().__init__(*args, msg)


class UnknownModelTypeError(ValueError, ErdanticException):
    """Raised when a given model does not match known supported class types."""

    def __init__(self, *args, model: type):
        display = getattr(model, "__mro__", str(model))
        message = f"Given model does not match any supported types. Model MRO: {display}"
        self.model = model
        super().__init__(*args, message)
