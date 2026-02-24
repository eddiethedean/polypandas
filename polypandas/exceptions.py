"""Custom exceptions for polypandas."""


class PolypandasError(Exception):
    """Base exception for polypandas."""

    pass


class PandasNotAvailableError(PolypandasError):
    """Raised when pandas is required but not installed."""

    def __init__(
        self,
        message: str = "pandas is not installed. Install it with: pip install pandas",
    ):
        super().__init__(message)


class SchemaInferenceError(PolypandasError):
    """Raised when schema cannot be inferred from a type."""

    pass


class UnsupportedTypeError(PolypandasError):
    """Raised when a type is not supported for conversion."""

    pass
