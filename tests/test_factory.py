"""Tests for polypandas factory and decorator."""

import pytest
from dataclasses import dataclass
from typing import Optional
from unittest.mock import patch

from polypandas import (
    PandasFactory,
    build_pandas_dataframe,
    pandas_factory,
)
from polypandas.exceptions import PandasNotAvailableError

from conftest import UserFactory


@dataclass
class Product:
    product_id: int
    name: str
    price: float
    description: Optional[str] = None
    in_stock: bool = True


@pandas_factory
@dataclass
class DecoratedUser:
    id: int
    name: str


def test_build_dicts():
    """build_dicts works without pandas."""
    dicts = UserFactory.build_dicts(size=5)
    assert len(dicts) == 5
    for d in dicts:
        assert "id" in d and "name" in d and "email" in d
        assert isinstance(d["id"], int)
        assert isinstance(d["name"], str)
        assert isinstance(d["email"], str)


def test_build_dicts_decorated():
    dicts = DecoratedUser.build_dicts(size=3)
    assert len(dicts) == 3
    for d in dicts:
        assert "id" in d and "name" in d


def test_build_dataframe_requires_pandas():
    """When pandas is not available, build_dataframe raises."""
    with patch("polypandas.factory.is_pandas_available", return_value=False):
        with pytest.raises(PandasNotAvailableError):
            UserFactory.build_dataframe(size=5)


def test_build_dataframe():
    import pandas as pd

    df = UserFactory.build_dataframe(size=10)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 10
    assert list(df.columns) == ["id", "name", "email"]
    assert df["id"].dtype.kind == "i"
    assert df["name"].dtype == object or df["name"].dtype.name == "object"


def test_build_dataframe_decorated():
    import pandas as pd

    df = DecoratedUser.build_dataframe(size=7)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 7
    assert list(df.columns) == ["id", "name"]


def test_build_pandas_dataframe_convenience():
    import pandas as pd

    df = build_pandas_dataframe(Product, size=20)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 20
    assert "product_id" in df.columns and "price" in df.columns


def test_create_dataframe_from_dicts():
    import pandas as pd

    dicts = UserFactory.build_dicts(size=5)
    df = UserFactory.create_dataframe_from_dicts(dicts)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    assert list(df.columns) == ["id", "name", "email"]


def test_build_dataframe_with_explicit_schema():
    """Explicit schema dict overrides inferred dtypes when not using PyArrow."""
    import pandas as pd

    df = UserFactory.build_dataframe(
        size=5, schema={"id": "float64", "name": "object", "email": "object"}
    )
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    assert str(df["id"].dtype) == "float64"


@dataclass
class NestedAddress:
    street: str
    city: str


@dataclass
class PersonWithAddress:
    id: int
    name: str
    address: NestedAddress


def test_build_dataframe_use_pyarrow_none_nested():
    """build_dataframe with use_pyarrow=None on nested model succeeds and returns correct shape."""
    import pandas as pd

    class PersonFactory(PandasFactory[PersonWithAddress]):
        __model__ = PersonWithAddress

    df = PersonFactory.build_dataframe(size=2, use_pyarrow=None)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["id", "name", "address"]
    assert isinstance(df["address"].iloc[0], dict)


@pytest.mark.skipif(
    __import__("sys").modules.get("pydantic") is None,
    reason="pydantic not installed",
)
def test_pydantic_pandas_factory_build_dicts_and_dataframe():
    """Pydantic model with @pandas_factory: build_dicts and build_dataframe work when pydantic available."""
    from pydantic import BaseModel

    @pandas_factory
    class Order(BaseModel):
        order_id: int
        amount: float

    dicts = Order.build_dicts(size=3)
    assert len(dicts) == 3
    assert set(dicts[0].keys()) == {"order_id", "amount"}

    import pandas as pd

    df = Order.build_dataframe(size=3)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert list(df.columns) == ["order_id", "amount"]
