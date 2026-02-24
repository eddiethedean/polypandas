"""Data export and import utilities for polypandas."""

from pathlib import Path
from typing import Any, Dict, List

from polypandas.exceptions import PolypandasError
from polypandas.protocols import is_pandas_available


class DataIOError(PolypandasError):
    """Raised when data I/O operations fail."""

    pass


def save_as_parquet(df: Any, path: str, **kwargs: Any) -> None:
    """Save DataFrame as Parquet file.

    Args:
        df: pandas DataFrame to save.
        path: Output path for Parquet file.
        **kwargs: Additional arguments for df.to_parquet() (e.g. index=False).

    Raises:
        DataIOError: If save operation fails.
    """
    if not is_pandas_available():
        raise DataIOError("pandas is required for Parquet operations")

    import pandas as pd

    if not isinstance(df, pd.DataFrame):
        raise DataIOError("Expected a pandas DataFrame")

    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path, **kwargs)
    except Exception as e:
        raise DataIOError(f"Failed to save Parquet file: {e}") from e


def save_as_json(df: Any, path: str, **kwargs: Any) -> None:
    """Save DataFrame as JSON file."""
    if not is_pandas_available():
        raise DataIOError("pandas is required for JSON operations")

    import pandas as pd

    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_json(path, **kwargs)
    except Exception as e:
        raise DataIOError(f"Failed to save JSON file: {e}") from e


def save_as_csv(
    df: Any,
    path: str,
    header: bool = True,
    **kwargs: Any,
) -> None:
    """Save DataFrame as CSV file."""
    if not is_pandas_available():
        raise DataIOError("pandas is required for CSV operations")

    import pandas as pd

    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, header=header, **kwargs)
    except Exception as e:
        raise DataIOError(f"Failed to save CSV file: {e}") from e


def load_parquet(path: str, **kwargs: Any) -> Any:
    """Load DataFrame from Parquet file."""
    if not is_pandas_available():
        raise DataIOError("pandas is required for Parquet operations")

    import pandas as pd

    try:
        return pd.read_parquet(path, **kwargs)
    except Exception as e:
        raise DataIOError(f"Failed to load Parquet file: {e}") from e


def load_json(path: str, **kwargs: Any) -> Any:
    """Load DataFrame from JSON file."""
    if not is_pandas_available():
        raise DataIOError("pandas is required for JSON operations")

    import pandas as pd

    try:
        return pd.read_json(path, **kwargs)
    except Exception as e:
        raise DataIOError(f"Failed to load JSON file: {e}") from e


def load_csv(
    path: str,
    header: int = 0,
    **kwargs: Any,
) -> Any:
    """Load DataFrame from CSV file."""
    if not is_pandas_available():
        raise DataIOError("pandas is required for CSV operations")

    import pandas as pd

    try:
        return pd.read_csv(path, header=header, **kwargs)
    except Exception as e:
        raise DataIOError(f"Failed to load CSV file: {e}") from e


def load_and_validate(
    path: str,
    expected_schema: Any = None,
    validate_schema: bool = True,
) -> Any:
    """Load data file and optionally validate against expected dtype dict.

    Args:
        path: Path to data file (.parquet, .json, or .csv).
        expected_schema: Optional dict of column name -> expected dtype (string).
        validate_schema: Whether to validate that columns and dtypes match.

    Returns:
        Loaded pandas DataFrame.
    """
    if not is_pandas_available():
        raise DataIOError("pandas is required for data loading")

    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".parquet":
        df = load_parquet(path)
    elif suffix == ".json":
        df = load_json(path)
    elif suffix in (".csv", ".txt"):
        df = load_csv(path)
    else:
        raise DataIOError(
            f"Unsupported file format: {suffix}. Supported: .parquet, .json, .csv"
        )

    if validate_schema and expected_schema is not None:
        from polypandas.testing import assert_column_exists

        for col in expected_schema:
            assert_column_exists(df, col)
        # Optionally check dtypes
        for col, dtype in expected_schema.items():
            if col in df.columns and str(df[col].dtype) != str(dtype):
                raise DataIOError(
                    f"Column '{col}' has dtype {df[col].dtype}, expected {dtype}"
                )

    return df


def save_dicts_as_json(data: List[Dict[str, Any]], path: str) -> None:
    """Save list of dictionaries as JSON lines file. Works without pandas."""
    import json

    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            for record in data:
                json.dump(record, f, default=str)
                f.write("\n")
    except Exception as e:
        raise DataIOError(f"Failed to save JSON file: {e}") from e


def load_dicts_from_json(path: str) -> List[Dict[str, Any]]:
    """Load list of dictionaries from JSON lines file. Works without pandas."""
    import json

    try:
        file_path = Path(path)
        if not file_path.exists():
            raise DataIOError(f"File not found: {path}")
        data = []
        with open(file_path) as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data
    except DataIOError:
        raise
    except Exception as e:
        raise DataIOError(f"Failed to load JSON file: {e}") from e
