"""Tests for schema inference."""

import pytest
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Literal, Optional, Tuple, TypedDict

from polypandas.exceptions import SchemaInferenceError, UnsupportedTypeError
from polypandas.schema import infer_schema, python_type_to_pandas_dtype


@dataclass
class Simple:
    a: int
    b: str
    c: float
    d: bool


@pytest.mark.parametrize(
    "python_type,expected",
    [
        (int, "int64"),
        (str, "object"),
        (float, "float64"),
        (bool, "bool"),
    ],
)
def test_python_type_to_pandas_dtype(python_type, expected):
    """Basic types map to expected pandas dtype strings."""
    assert python_type_to_pandas_dtype(python_type) == expected


def test_python_type_optional():
    """Optional unwraps to inner type for dtype."""
    assert python_type_to_pandas_dtype(Optional[str]) == "object"
    assert python_type_to_pandas_dtype(Optional[int]) == "int64"


def test_python_type_literal_str():
    """Literal of strings maps to object."""
    assert python_type_to_pandas_dtype(Literal["a", "b"]) == "object"


def test_python_type_literal_int():
    """Literal of ints maps to int64."""
    assert python_type_to_pandas_dtype(Literal[1, 2]) == "int64"


def test_python_type_literal_mixed_types_raises():
    """Literal with mixed incompatible types raises SchemaInferenceError."""
    with pytest.raises(SchemaInferenceError):
        python_type_to_pandas_dtype(Literal[1, "a"])


def test_python_type_list_str():
    """List[str] maps to object."""
    assert python_type_to_pandas_dtype(List[str]) == "object"


def test_python_type_dict_str_int():
    """Dict[str, int] maps to object."""
    assert python_type_to_pandas_dtype(Dict[str, int]) == "object"


@dataclass
class WithComplexTypes:
    tags: List[str]
    counts: Dict[str, int]


def test_infer_schema_dataclass_with_list_and_dict():
    """infer_schema on dataclass with List/Dict fields does not raise."""
    schema = infer_schema(WithComplexTypes)
    assert schema["tags"] == "object"
    assert schema["counts"] == "object"


@dataclass
class WithDateDatetimeDecimal:
    d: date
    dt: datetime
    dec: Decimal


def test_infer_schema_date_datetime_decimal():
    """date, datetime, Decimal get expected dtype strings."""
    schema = infer_schema(WithDateDatetimeDecimal)
    assert schema["d"] == "datetime64[ns]"
    assert schema["dt"] == "datetime64[ns]"
    assert schema["dec"] == "object"


class SimpleTypedDict(TypedDict):
    x: int
    y: str


def test_infer_schema_typed_dict():
    """infer_schema on TypedDict returns expected dtypes."""
    schema = infer_schema(SimpleTypedDict)
    assert schema["x"] == "int64"
    assert schema["y"] == "object"


@pytest.mark.skipif(
    __import__("sys").modules.get("pydantic") is None,
    reason="pydantic not installed",
)
def test_infer_schema_pydantic_model():
    """infer_schema on Pydantic BaseModel returns expected dtypes when pydantic available."""
    from pydantic import BaseModel

    class SmallModel(BaseModel):
        id: int
        name: str

    schema = infer_schema(SmallModel)
    assert schema["id"] == "int64"
    assert schema["name"] == "object"


def test_python_type_unsupported_raises():
    """Unsupported type (e.g. Tuple) raises UnsupportedTypeError."""
    with pytest.raises(UnsupportedTypeError):
        python_type_to_pandas_dtype(Tuple[str, int])


def test_infer_schema_dataclass():
    """infer_schema on dataclass returns dtype dict."""
    schema = infer_schema(Simple)
    assert schema == {
        "a": "int64",
        "b": "object",
        "c": "float64",
        "d": "bool",
    }


def test_infer_schema_explicit_override():
    """Explicit schema override is returned as-is."""
    schema = infer_schema(Simple, schema={"a": "float64", "b": "object"})
    assert schema["a"] == "float64"
