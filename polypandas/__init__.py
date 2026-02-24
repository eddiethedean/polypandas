"""Polypandas - Generate pandas DataFrames using polyfactory.

This package provides tools to generate pandas DataFrames for testing and
development using the polyfactory library. It supports dataclasses, Pydantic
models, and TypedDicts. Optional PyArrow (pip install polypandas[pyarrow])
enables proper nested struct columns.
"""

from polypandas.exceptions import (
    PandasNotAvailableError,
    PolypandasError,
    SchemaInferenceError,
    UnsupportedTypeError,
)
from polypandas.io import DataIOError
from polypandas.factory import (
    PandasFactory,
    build_pandas_dataframe,
    pandas_factory,
)
from polypandas.io import (
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
from polypandas.protocols import is_pandas_available, is_pyarrow_available
from polypandas.schema import (
    has_nested_structs,
    infer_pyarrow_schema,
    infer_schema,
    python_type_to_pandas_dtype,
)
from polypandas.testing import (
    DataFrameComparisonError,
    assert_approx_count,
    assert_column_exists,
    assert_dataframe_equal,
    assert_dtypes_equal,
    assert_no_duplicates,
    assert_schema_equal,
    get_column_stats,
)

__version__ = "0.1.0"

__all__ = [
    "PandasFactory",
    "build_pandas_dataframe",
    "pandas_factory",
    "has_nested_structs",
    "infer_pyarrow_schema",
    "infer_schema",
    "python_type_to_pandas_dtype",
    "is_pyarrow_available",
    "assert_dataframe_equal",
    "assert_schema_equal",
    "assert_dtypes_equal",
    "assert_approx_count",
    "assert_column_exists",
    "assert_no_duplicates",
    "get_column_stats",
    "DataFrameComparisonError",
    "save_as_parquet",
    "save_as_json",
    "save_as_csv",
    "load_parquet",
    "load_json",
    "load_csv",
    "load_and_validate",
    "save_dicts_as_json",
    "load_dicts_from_json",
    "DataIOError",
    "is_pandas_available",
    "PolypandasError",
    "PandasNotAvailableError",
    "SchemaInferenceError",
    "UnsupportedTypeError",
]
