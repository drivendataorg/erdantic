from typing import Optional


class ModelTypeMismatchError(ValueError):
    """Raised when multiple models are given but they do not all match the detected type of the
    first model.
    """

    def __init__(
        self,
        mismatched_model: type,
        first_model: type,
        expected: str,
        message: Optional[str] = None,
    ):
        if message is None:
            message = (
                f"Additional model does not match detected type of first model. "
                f"Expected: {expected}; "
                f"Mismatched model MRO: {mismatched_model.__mro__}"
            )
        self.mismatched_model = mismatched_model
        self.first_model = first_model
        self.expected = expected
        self.message = message
        super().__init__(message)


class UnknownModelTypeError(ValueError):
    """Raised when a given model does not match known supported class types."""

    def __init__(self, model: type, message: Optional[str] = None):
        if message is None:
            message = f"Given model does not match any supported types. Model MRO: {model.__mro__}"
        self.model = model
        self.message = message
        super().__init__(message)
