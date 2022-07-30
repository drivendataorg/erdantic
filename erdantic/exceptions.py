from typing import Optional, TYPE_CHECKING

from typing import ForwardRef  # docs claim Python >= 3.7.4 but actually it's in Python 3.7.0+

if TYPE_CHECKING:
    from erdantic.base import Model, Field


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


class StringForwardRefError(ErdanticException):
    """Raised when a field's type declaration is stored as a string literal and not transformed
    into a typing.ForwardRef object."""

    def __init__(self, model: "Model", field: "Field", forward_ref: ForwardRef) -> None:
        message = (
            f"Forward reference '{forward_ref}' for field '{field.name}' on model '{model.name}' "
            "is a string literal and not a typing.ForwardRef object. erdantic is unable to handle "
            "forward references that aren't transformed into typing.ForwardRef. Declare "
            f"explicitly with 'typing.ForwardRef(\"{forward_ref}\", is_argument=False)'."
        )
        super().__init__(message)


class _StringForwardRefError(ErdanticException):
    """Internal exception for forward references that are stored as a string literal rather than
    a typing.ForwardRef object."""

    def __init__(self, forward_ref: ForwardRef) -> None:
        self.forward_ref = forward_ref
        super().__init__("Unexpected error while flagging forward reference stored as a string.")


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
