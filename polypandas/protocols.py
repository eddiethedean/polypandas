"""Protocol definitions and runtime checks for polypandas."""


def is_pandas_available() -> bool:
    """Check if pandas is available at runtime.

    Returns:
        True if pandas can be imported, False otherwise.
    """
    try:
        import pandas  # noqa: F401
        return True
    except ImportError:
        return False


def is_pyarrow_available() -> bool:
    """Check if PyArrow is available at runtime.

    Returns:
        True if pyarrow can be imported, False otherwise.
    """
    try:
        import pyarrow  # noqa: F401
        return True
    except ImportError:
        return False
