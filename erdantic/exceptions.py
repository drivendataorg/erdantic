from typing import Optional, TYPE_CHECKING

try:
    from typing import ForwardRef  # type: ignore # Python >= 3.7.4
except ImportError:
    from typing import _ForwardRef as ForwardRef  # type: ignore # Python < 3.7.4


if TYPE_CHECKING:
    from erdantic.base import Model, Field


class ErdanticException(Exception):
    """Base class for all exceptions from erdantic library."""


class InvalidModelError(ValueError, ErdanticException):
    """Raised when an invalid model object is passed to a model adapter."""


class InvalidModelAdapterError(ValueError, ErdanticException):
    """Raised when trying to register a model adapter that is not subclassing Model."""


class InvalidFieldError(ValueError, ErdanticException):
    """Raised when an invalid field object is passed to a field adapter."""


class NotATypeError(ValueError, ErdanticException):
    pass


class UnevaluatedForwardRefError(ErdanticException):
    """Raised when a field's type declaration has an unevaluated forward reference."""

    def __init__(self, model: "Model", field: "Field", forward_ref: ForwardRef) -> None:
        message = (
            f"Unevaluated forward reference '{forward_ref.__forward_arg__}' "
            f"for field {field.name} on model {model.name}."
        )
        if model.forward_ref_help:
            message += " " + model.forward_ref_help
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
