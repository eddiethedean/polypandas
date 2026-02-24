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


@dataclass
class User:
    id: int
    name: str
    email: str


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


class UserFactory(PandasFactory[User]):
    __model__ = User


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
