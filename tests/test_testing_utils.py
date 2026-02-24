"""Tests for polypandas testing utilities."""

import pytest
from unittest.mock import patch

import pandas as pd

from polypandas import (
    DataFrameComparisonError,
    assert_approx_count,
    assert_column_exists,
    assert_dataframe_equal,
    assert_dtypes_equal,
    assert_no_duplicates,
    assert_schema_equal,
    get_column_stats,
)


def test_assert_dataframe_equal_identical():
    """Two identical DataFrames pass assert_dataframe_equal."""
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    assert_dataframe_equal(df, df.copy())


def test_assert_dataframe_equal_different_row_count_raises():
    """Different row counts raise DataFrameComparisonError."""
    df1 = pd.DataFrame({"a": [1], "b": [2]})
    df2 = pd.DataFrame({"a": [1, 2], "b": [2, 3]})
    with pytest.raises(DataFrameComparisonError, match="row counts"):
        assert_dataframe_equal(df1, df2)


def test_assert_dataframe_equal_different_columns_raises():
    """Different columns raise DataFrameComparisonError."""
    df1 = pd.DataFrame({"a": [1], "b": [2]})
    df2 = pd.DataFrame({"a": [1], "c": [2]})
    with pytest.raises(DataFrameComparisonError, match="columns"):
        assert_dataframe_equal(df1, df2)


def test_assert_dataframe_equal_check_order_false_passes():
    """With check_order=False, different row order still passes after internal sort."""
    df1 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    df2 = pd.DataFrame({"a": [2, 1], "b": [4, 3]})
    assert_dataframe_equal(df1, df2, check_order=False)


def test_assert_dataframe_equal_check_dtypes_false_passes():
    """With check_dtypes=False, different dtypes can pass."""
    df1 = pd.DataFrame({"a": [1, 2]}, dtype="int64")
    df2 = pd.DataFrame({"a": [1.0, 2.0]}, dtype="float64")
    assert_dataframe_equal(df1, df2, check_dtypes=False)


def test_assert_dataframe_equal_pandas_not_available_raises():
    """When pandas is not available, assert_dataframe_equal raises."""
    with patch("polypandas.testing.is_pandas_available", return_value=False):
        df = pd.DataFrame({"a": [1]})
        with pytest.raises(DataFrameComparisonError, match="pandas is required"):
            assert_dataframe_equal(df, df)


def test_assert_schema_equal_same_dtypes_passes():
    """Two DataFrames with same dtypes pass assert_schema_equal."""
    df1 = pd.DataFrame({"a": [1], "b": ["x"]})
    df2 = pd.DataFrame({"a": [2], "b": ["y"]})
    assert_schema_equal(df1, df2)


def test_assert_dtypes_equal_different_dtype_raises():
    """Different dtype for a column raises DataFrameComparisonError."""
    df1 = pd.DataFrame({"a": [1]}, dtype="int64")
    df2 = pd.DataFrame({"a": [1]}, dtype="float64")
    with pytest.raises(DataFrameComparisonError, match="different dtypes"):
        assert_dtypes_equal(df1, df2)


def test_assert_approx_count_within_tolerance_passes():
    """Row count within tolerance passes."""
    df = pd.DataFrame({"a": range(95)})
    assert_approx_count(df, 100, tolerance=0.1)


def test_assert_approx_count_outside_tolerance_raises():
    """Row count outside tolerance raises DataFrameComparisonError."""
    df = pd.DataFrame({"a": range(50)})
    with pytest.raises(DataFrameComparisonError, match="not within"):
        assert_approx_count(df, 100, tolerance=0.1)


def test_assert_column_exists_present_passes():
    """All requested columns present passes."""
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
    assert_column_exists(df, "a", "b", "c")


def test_assert_column_exists_missing_raises():
    """Missing column raises DataFrameComparisonError."""
    df = pd.DataFrame({"a": [1], "b": [2]})
    with pytest.raises(DataFrameComparisonError, match="missing"):
        assert_column_exists(df, "a", "b", "z")


def test_assert_no_duplicates_no_dupes_passes():
    """DataFrame with no duplicates passes."""
    df = pd.DataFrame({"a": [1, 2, 3]})
    assert_no_duplicates(df)


def test_assert_no_duplicates_with_dupes_raises():
    """DataFrame with duplicates in subset raises DataFrameComparisonError."""
    df = pd.DataFrame({"a": [1, 1, 2], "b": [10, 20, 30]})
    with pytest.raises(DataFrameComparisonError, match="duplicate"):
        assert_no_duplicates(df, columns=["a"])


def test_get_column_stats_numeric():
    """get_column_stats returns expected keys and numeric stats for numeric column."""
    df = pd.DataFrame({"amount": [1.0, 2.0, 3.0, 4.0]})
    stats = get_column_stats(df, "amount")
    assert "count" in stats
    assert "null_count" in stats
    assert "distinct_count" in stats
    assert stats["count"] == 4
    assert stats["min"] == 1.0
    assert stats["max"] == 4.0
    assert stats["mean"] == 2.5
    assert "std" in stats
