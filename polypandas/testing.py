"""Testing utilities for pandas DataFrames."""

from typing import Any, Dict, List, Optional

from polypandas.exceptions import PolypandasError
from polypandas.protocols import is_pandas_available


class DataFrameComparisonError(PolypandasError):
    """Raised when DataFrame comparison fails."""

    pass


def assert_dataframe_equal(
    df1: Any,
    df2: Any,
    check_order: bool = False,
    rtol: float = 1e-5,
    atol: float = 1e-8,
    check_dtypes: bool = True,
    check_column_order: bool = False,
) -> None:
    """Assert that two pandas DataFrames are equal.

    Args:
        df1: First DataFrame to compare.
        df2: Second DataFrame to compare.
        check_order: If True, row order must match. If False, DataFrames are sorted.
        rtol: Relative tolerance for floating point comparisons.
        atol: Absolute tolerance for floating point comparisons.
        check_dtypes: If True, check that dtypes match.
        check_column_order: If True, column order must match.

    Raises:
        DataFrameComparisonError: If DataFrames are not equal.
    """
    if not is_pandas_available():
        raise DataFrameComparisonError(
            "pandas is required for DataFrame comparison. Install it with: pip install pandas"
        )

    import pandas as pd

    if not isinstance(df1, pd.DataFrame) or not isinstance(df2, pd.DataFrame):
        raise DataFrameComparisonError("Both arguments must be pandas DataFrames")

    if len(df1) != len(df2):
        raise DataFrameComparisonError(
            f"DataFrame row counts don't match: {len(df1)} != {len(df2)}"
        )

    if set(df1.columns) != set(df2.columns):
        raise DataFrameComparisonError(
            f"DataFrame columns don't match: {set(df1.columns)} != {set(df2.columns)}"
        )

    if check_column_order and list(df1.columns) != list(df2.columns):
        raise DataFrameComparisonError("Column order does not match")

    if not check_column_order:
        df2 = df2[df1.columns]

    if not check_order and len(df1) > 0:
        df1 = df1.sort_values(by=list(df1.columns)).reset_index(drop=True)
        df2 = df2.sort_values(by=list(df2.columns)).reset_index(drop=True)

    try:
        pd.testing.assert_frame_equal(
            df1,
            df2,
            check_dtype=check_dtypes,
            rtol=rtol,
            atol=atol,
        )
    except AssertionError as e:
        raise DataFrameComparisonError(str(e)) from e


def assert_schema_equal(
    df1: Any,
    df2: Any,
    check_order: bool = False,
) -> None:
    """Assert that two DataFrames have the same dtypes (schema). Alias for assert_dtypes_equal."""
    assert_dtypes_equal(df1, df2, check_order=check_order)


def assert_dtypes_equal(
    df1: Any,
    df2: Any,
    check_order: bool = False,
) -> None:
    """Assert that two DataFrames have the same dtypes.

    Args:
        df1: First DataFrame.
        df2: Second DataFrame.
        check_order: If True, column order must match.

    Raises:
        DataFrameComparisonError: If dtypes are not equal.
    """
    if not is_pandas_available():
        raise DataFrameComparisonError("pandas is required")

    import pandas as pd

    dtypes1 = df1.dtypes
    dtypes2 = df2.dtypes

    if set(dtypes1.index) != set(dtypes2.index):
        raise DataFrameComparisonError("DataFrames have different columns")

    if not check_order:
        dtypes2 = dtypes2[dtypes1.index]

    for col in dtypes1.index:
        if dtypes1[col] != dtypes2[col]:
            raise DataFrameComparisonError(
                f"Column '{col}' has different dtypes: {dtypes1[col]} != {dtypes2[col]}"
            )


def assert_approx_count(
    df: Any, expected_count: int, tolerance: float = 0.1
) -> None:
    """Assert that DataFrame row count is approximately equal to expected."""
    if not is_pandas_available():
        raise DataFrameComparisonError("pandas is required")

    import pandas as pd

    actual_count = len(df)
    min_count = int(expected_count * (1 - tolerance))
    max_count = int(expected_count * (1 + tolerance))

    if not (min_count <= actual_count <= max_count):
        raise DataFrameComparisonError(
            f"DataFrame count {actual_count} is not within {tolerance * 100:.1f}% "
            f"of expected {expected_count}. Expected range: [{min_count}, {max_count}]"
        )


def get_column_stats(df: Any, column: str) -> Dict[str, Any]:
    """Get basic statistics for a column."""
    if not is_pandas_available():
        raise DataFrameComparisonError("pandas is required")

    import pandas as pd

    s = df[column]
    stats = {
        "count": int(s.count()),
        "null_count": int(s.isna().sum()),
        "distinct_count": int(s.nunique()),
    }

    if pd.api.types.is_numeric_dtype(s):
        stats["min"] = float(s.min()) if s.count() else None
        stats["max"] = float(s.max()) if s.count() else None
        stats["mean"] = float(s.mean()) if s.count() else None
        stats["std"] = float(s.std()) if s.count() else None

    return stats


def assert_column_exists(df: Any, *columns: str) -> None:
    """Assert that specified columns exist in DataFrame."""
    df_columns = set(df.columns)
    missing = [c for c in columns if c not in df_columns]

    if missing:
        raise DataFrameComparisonError(
            f"Columns missing from DataFrame: {missing}. "
            f"Available columns: {sorted(df_columns)}"
        )


def assert_no_duplicates(
    df: Any, columns: Optional[List[str]] = None
) -> None:
    """Assert that DataFrame has no duplicate rows."""
    if not is_pandas_available():
        raise DataFrameComparisonError("pandas is required")

    import pandas as pd

    total_count = len(df)
    if columns is None:
        unique_count = len(df.drop_duplicates())
    else:
        unique_count = len(df.drop_duplicates(subset=columns))

    if unique_count != total_count:
        raise DataFrameComparisonError(
            f"DataFrame contains {total_count - unique_count} duplicate row(s). "
            f"Total rows: {total_count}, Unique rows: {unique_count}"
        )
