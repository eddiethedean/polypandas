"""Tests for polypandas I/O utilities."""

import pytest

from polypandas import (
    DataIOError,
    load_and_validate,
    load_csv,
    load_dicts_from_json,
    load_json,
    load_parquet,
    save_as_csv,
    save_as_json,
    save_as_parquet,
    save_dicts_as_json,
)
from polypandas.schema import infer_schema

from conftest import User, UserFactory


def test_save_load_parquet_round_trip(tmp_path):
    """Save DataFrame as Parquet and load back; assert shape and columns match."""
    df = UserFactory.build_dataframe(size=5)
    path = tmp_path / "users.parquet"
    save_as_parquet(df, str(path))
    loaded = load_parquet(str(path))
    assert loaded.shape == df.shape
    assert list(loaded.columns) == list(df.columns)


def test_save_load_json_round_trip(tmp_path):
    """Save DataFrame as JSON and load back; assert shape and columns match."""
    df = UserFactory.build_dataframe(size=5)
    path = tmp_path / "users.json"
    save_as_json(df, str(path))
    loaded = load_json(str(path))
    assert loaded.shape == df.shape
    assert set(loaded.columns) == set(df.columns)


def test_save_load_csv_round_trip(tmp_path):
    """Save DataFrame as CSV and load back; assert shape and columns match."""
    df = UserFactory.build_dataframe(size=5)
    path = tmp_path / "users.csv"
    save_as_csv(df, str(path), header=True, index=False)
    loaded = load_csv(str(path), header=0)
    assert loaded.shape == df.shape
    assert list(loaded.columns) == list(df.columns)


def test_save_as_parquet_non_dataframe_raises():
    """Passing a non-DataFrame to save_as_parquet raises DataIOError."""
    with pytest.raises(DataIOError, match="Expected a pandas DataFrame"):
        save_as_parquet([1, 2, 3], "/tmp/out.parquet")


def test_load_parquet_missing_file_raises(tmp_path):
    """Loading a non-existent Parquet file raises DataIOError."""
    with pytest.raises(DataIOError, match="Failed to load"):
        load_parquet(str(tmp_path / "nonexistent.parquet"))


def test_save_dicts_as_json_load_round_trip(tmp_path):
    """save_dicts_as_json then load_dicts_from_json returns same length and keys."""
    dicts = UserFactory.build_dicts(size=5)
    path = tmp_path / "data.jsonl"
    save_dicts_as_json(dicts, str(path))
    loaded = load_dicts_from_json(str(path))
    assert len(loaded) == 5
    assert set(loaded[0].keys()) == {"id", "name", "email"}


def test_load_dicts_from_json_missing_file_raises():
    """Loading a non-existent JSONL file raises DataIOError."""
    with pytest.raises(DataIOError, match="File not found"):
        load_dicts_from_json("/nonexistent/path/data.jsonl")


def test_load_and_validate_parquet(tmp_path):
    """load_and_validate with expected_schema succeeds and returns correct columns."""
    df = UserFactory.build_dataframe(size=3)
    path = tmp_path / "users.parquet"
    save_as_parquet(df, str(path))
    expected_schema = infer_schema(User)
    loaded = load_and_validate(str(path), expected_schema=expected_schema, validate_schema=True)
    assert list(loaded.columns) == list(expected_schema.keys())
    assert len(loaded) == 3


def test_load_and_validate_unsupported_format_raises(tmp_path):
    """load_and_validate with unsupported extension raises DataIOError."""
    path = tmp_path / "file.xyz"
    path.touch()
    with pytest.raises(DataIOError, match="Unsupported file format"):
        load_and_validate(str(path))
