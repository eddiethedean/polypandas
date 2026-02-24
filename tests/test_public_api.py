"""Guard test: all public API symbols can be imported from polypandas."""

import polypandas


def test_public_api_imports():
    """Every name in __all__ is importable and matches the exported value."""
    for name in polypandas.__all__:
        assert hasattr(polypandas, name), f"Missing export: {name}"
