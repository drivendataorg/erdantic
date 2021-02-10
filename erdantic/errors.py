from typing import Optional


class UnknownModelTypeError(ValueError):
    """Raised when a given model does not match known supported class types."""

    def __init__(self, model: type, message: Optional[str] = None):
        if message is None:
            display = getattr(model, "__mro__", str(model))
            message = f"Given model does not match any supported types. Model MRO: {display}"
        self.model = model
        self.message = message
        super().__init__(message)
