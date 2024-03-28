import sys
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from erdantic.core import FullyQualifiedName


class ErdanticException(Exception):
    """Base class for all exceptions from erdantic library."""


class PluginNotFoundError(KeyError, ErdanticException):
    """Raised when specified plugin key does not match a registered plugin.

    Attributes:
        key (str): The plugin key that was not found.
    """

    def __init__(self, *args: object, key: str) -> None:
        self.key = key
        message = f"Specified plugin not found: '{key}'"
        super().__init__(*args, message)


class ModelOrModuleNotFoundError(ImportError, ErdanticException):
    """Raised when specified fully qualified name of model class or module cannot be imported."""


class UnresolvableForwardRefError(NameError, ErdanticException):
    """Raised when a forward reference in a type annotation cannot be resolved automatically.

    Attributes:
        name (str): The string representation of the unresolvable forward reference.
    """

    def __init__(
        self,
        *args: object,
        name: str,
        model_full_name: "FullyQualifiedName",
    ) -> None:
        self.model_full_name = model_full_name
        if sys.version_info >= (3, 10):
            # typeshed is wrong; NameError does have keyword argument 'name'
            super().__init__(*args, name=name)  # type: ignore [call-arg]
        else:
            super().__init__(*args)
            self.name = name


class UnevaluatedForwardRefError(ErdanticException):
    """Raised when a field's type declaration has an unevaluated forward reference.

    Attributes:
        model_full_name (FullyQualifiedName): The fully qualified name of the model with the field
            with the unevaluated forward reference.
        field_name (str): The name of the field with the unevaluated forward reference.
        forward_ref (str): The string representation of the unevaluated forward reference.
    """

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
            "Normally, erdantic plugins try to resolve forward references automatically, and this "
            "error indicates that this didn't happen. If you are using a built-in plugin, please "
            "report this as a bug. If you are using a custom or third-party plugin, then that "
            "plugin needs to add support for automatically resolving forward references. "
        )
        super().__init__(*args, message)


class _UnevaluatedForwardRefError(ErdanticException):
    """Internal exception for unevaluated forward references that is caught and raised instead
    as UnevaluatedForwardRefError."""

    def __init__(self, *args, forward_ref: str) -> None:
        self.forward_ref = forward_ref
        msg = (
            "Unexpected error while flagging unevaluated forward reference. "
            "If you see this error, something is wrong. Please report this as a bug."
        )
        super().__init__(*args, msg)


class FieldNotFoundError(AttributeError, ErdanticException):
    """Raised trying to access a field name that does not match any fields returned by the
    field extractor function for a model.

    Attributes:
        name (str): The name of the field that was not found.
        obj (object): The model object that the field was being accessed on.
        model_full_name (FullyQualifiedName): The fully qualified name of the model.
    """

    def __init__(self, *args, name: str, obj: object, model_full_name: "FullyQualifiedName"):
        self.model_full_name = model_full_name
        msg = f"Model '{model_full_name}' has no field '{name}'."
        if sys.version_info >= (3, 10):
            super().__init__(*args, msg, name=name, obj=obj)
        else:
            self.name = name
            self.obj = obj
            super().__init__(*args, msg)


class UnknownModelTypeError(ValueError, ErdanticException):
    """Raised when a given model does not match known model types from loaded plugins.

    Attributes:
        model (type): The model class that was not recognized.
        available_plugins (List[str]): List of plugin keys that were available.
    """

    def __init__(self, *args, model: type, available_plugins: List[str]):
        mro = getattr(model, "__mro__", str(model))
        message = (
            "Given model does not match any supported types. "
            f"Available plugins: {available_plugins}. "
            f"Model MRO: {mro}"
        )
        self.model = model
        self.available_plugins = available_plugins
        super().__init__(*args, message)
