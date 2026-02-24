"""Shared pytest fixtures for polypandas tests."""

import pytest
from dataclasses import dataclass

from polypandas import PandasFactory


@dataclass
class User:
    """Shared model for tests that need a simple dataclass (e.g. test_io, test_factory)."""

    id: int
    name: str
    email: str


class UserFactory(PandasFactory[User]):
    __model__ = User


@pytest.fixture
def user_model():
    """Return the User dataclass."""
    return User


@pytest.fixture
def user_factory():
    """Return the UserFactory class."""
    return UserFactory
