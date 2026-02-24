"""Tests for nested structs and optional PyArrow support."""

import pytest
from dataclasses import dataclass

from polypandas import PandasFactory
from polypandas.schema import has_nested_structs, infer_pyarrow_schema
from polypandas.protocols import is_pyarrow_available


@dataclass
class Address:
    street: str
    city: str
    zipcode: str


@dataclass
class Person:
    id: int
    name: str
    address: Address


@dataclass
class Flat:
    a: int
    b: str


def test_has_nested_structs_flat():
    assert has_nested_structs(Flat) is False


def test_has_nested_structs_nested():
    assert has_nested_structs(Person) is True


@pytest.mark.skipif(not is_pyarrow_available(), reason="pyarrow not installed")
def test_infer_pyarrow_schema_flat():
    schema = infer_pyarrow_schema(Flat)
    assert schema is not None
    assert schema.get_field_index("a") >= 0
    assert schema.get_field_index("b") >= 0


@pytest.mark.skipif(not is_pyarrow_available(), reason="pyarrow not installed")
def test_infer_pyarrow_schema_nested():
    schema = infer_pyarrow_schema(Person)
    assert schema is not None
    addr = schema.field("address")
    assert addr.type.num_fields == 3  # street, city, zipcode


@pytest.mark.skipif(not is_pyarrow_available(), reason="pyarrow not installed")
def test_build_dataframe_nested_with_pyarrow():
    import pandas as pd

    class PersonFactory(PandasFactory[Person]):
        __model__ = Person

    df = PersonFactory.build_dataframe(size=5, use_pyarrow=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    assert "id" in df.columns and "name" in df.columns and "address" in df.columns
    # With PyArrow, address column should be struct-like (ArrowDtype in pandas 2.x or object)
    assert df["address"].iloc[0] is not None


def test_build_dataframe_nested_without_pyarrow():
    import pandas as pd

    class PersonFactory(PandasFactory[Person]):
        __model__ = Person

    df = PersonFactory.build_dataframe(size=5, use_pyarrow=False)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    assert list(df.columns) == ["id", "name", "address"]
    # Without PyArrow, address is object column (dicts)
    assert isinstance(df["address"].iloc[0], dict)
    assert "street" in df["address"].iloc[0]
