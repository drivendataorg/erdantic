from typing import (
    TYPE_CHECKING,
    ForwardRef,  # docs claim Python >= 3.7.4 but actually it's in Python 3.7.0+
    Optional,
)

if TYPE_CHECKING:
    from erdantic.core import FullyQualifiedName


class ErdanticException(Exception):
    """Base class for all exceptions from erdantic library."""


class InvalidModelError(ValueError, ErdanticException):
    """Raised when an invalid model object is passed to a model adapter."""


class InvalidModelAdapterError(ValueError, ErdanticException):
    """Raised when a model adapter is expected but input is not subclassing Model."""


class InvalidFieldError(ValueError, ErdanticException):
    """Raised when an invalid field object is passed to a field adapter."""


class ModelAdapterNotFoundError(KeyError, ErdanticException):
    """Raised when specified key does not match a registered model adapter."""


class ModelOrModuleNotFoundError(ImportError, ErdanticException):
    """Raised when specified fully qualified name of model class or module cannot be found."""


class NotATypeError(ValueError, ErdanticException):
    pass


class UnresolvableForwardRefError(ErdanticException):
    ...


class UnevaluatedForwardRefError(ErdanticException):
    """Raised when a field's type declaration has an unevaluated forward reference."""

    def __init__(
        self,
        model_full_name: "FullyQualifiedName",
        field_name: str,
        forward_ref: ForwardRef,
    ) -> None:
        message = (
            f"Unevaluated forward reference '{forward_ref}' "
            f"for field '{field_name}' on model '{model_full_name}'. "
            "Normally, erdantic plugins try to resolve forward references, and this error "
            "indicates that this didn't happen. If you are using a built-in plugin, please report "
            "this as a bug. If you are using a custom or third-party plugin, then that plugin "
            "needs to add support for resolving forward references. "
        )
        super().__init__(message)


class _UnevaluatedForwardRefError(ErdanticException):
    """Internal exception for unevaluated forward references that is caught and raised instead
    as UnevaluatedForwardRefError."""

    def __init__(self, forward_ref: ForwardRef) -> None:
        self.forward_ref = forward_ref
        super().__init__("Unexpected error while flagging unevaluated forward reference.")


class UnknownFieldError(ValueError, ErdanticException):
    """Raised when specified field does not match a field on specified model."""


class UnknownModelTypeError(ValueError, ErdanticException):
    """Raised when a given model does not match known supported class types."""

    def __init__(self, model: type, message: Optional[str] = None):
        if message is None:
            display = getattr(model, "__mro__", str(model))
            message = f"Given model does not match any supported types. Model MRO: {display}"
        self.model = model
        self.message = message
        super().__init__(message)
