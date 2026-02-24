"""Tests for schema inference."""

import pytest
from dataclasses import dataclass
from typing import Dict, List, Optional

from polypandas.schema import (
    infer_schema,
    python_type_to_pandas_dtype,
)
from polypandas.exceptions import SchemaInferenceError, UnsupportedTypeError


@dataclass
class Simple:
    a: int
    b: str
    c: float
    d: bool


def test_python_type_to_pandas_dtype():
    assert python_type_to_pandas_dtype(int) == "int64"
    assert python_type_to_pandas_dtype(str) == "object"
    assert python_type_to_pandas_dtype(float) == "float64"
    assert python_type_to_pandas_dtype(bool) == "bool"


def test_python_type_optional():
    assert python_type_to_pandas_dtype(Optional[str]) == "object"
    assert python_type_to_pandas_dtype(Optional[int]) == "int64"


def test_infer_schema_dataclass():
    schema = infer_schema(Simple)
    assert schema == {
        "a": "int64",
        "b": "object",
        "c": "float64",
        "d": "bool",
    }


def test_infer_schema_explicit_override():
    schema = infer_schema(Simple, schema={"a": "float64", "b": "object"})
    assert schema["a"] == "float64"
