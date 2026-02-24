# Polypandas

**Generate type-safe pandas DataFrames effortlessly using polyfactory**

Inspired by [polyspark](https://github.com/eddiethedean/polyspark).

---

## Table of contents

- [Why Polypandas?](#why-polypandas)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Nested structs (optional PyArrow)](#nested-structs-optional-pyarrow)
- [Key features](#key-features)
- [Type mapping](#type-mapping)
- [API reference](#api-reference)
- [Testing utilities](#testing-utilities)
- [Data I/O](#data-io)
- [License & related](#license--related)

---

## Why Polypandas?

Creating test data for pandas applications is tedious. Polypandas makes it **effortless** by generating realistic test DataFrames from your Python data models, with **automatic schema inference** so columns get the right dtypes even when values are null.

```python
from dataclasses import dataclass
from polypandas import pandas_factory

@pandas_factory
@dataclass
class User:
    id: int
    name: str
    email: str

# Generate 1000 rows instantly
df = User.build_dataframe(size=1000)
```

---

## Installation

**Base install** (pandas + polyfactory):

```bash
pip install polypandas
```

**Optional: PyArrow** for proper nested struct columns (otherwise nested fields are object columns of dicts):

```bash
pip install polypandas[pyarrow]
```

**Development** (tests, lint, type-checking):

```bash
pip install "polypandas[dev]"
```

**Requirements:** Python 3.8+, pandas ≥1.3, polyfactory ≥2.0.

---

## Quick start

### Decorator (recommended)

```python
from dataclasses import dataclass
from typing import Optional
from polypandas import pandas_factory

@pandas_factory
@dataclass
class Product:
    product_id: int
    name: str
    price: float
    description: Optional[str] = None
    in_stock: bool = True

df = Product.build_dataframe(size=100)
print(df.head())
```

### Generate dicts, then convert to DataFrame

```python
dicts = Product.build_dicts(size=1000)
df = Product.create_dataframe_from_dicts(dicts)
```

### Classic factory pattern

```python
from polypandas import PandasFactory

class ProductFactory(PandasFactory[Product]):
    __model__ = Product

df = ProductFactory.build_dataframe(size=100)
```

### Convenience function (no factory class)

```python
from polypandas import build_pandas_dataframe

df = build_pandas_dataframe(Product, size=100)
```

### Pydantic models

```python
from pydantic import BaseModel
from polypandas import pandas_factory

@pandas_factory
class Order(BaseModel):
    order_id: int
    customer_id: int
    total: float

df = Order.build_dataframe(size=500)
```

---

## Nested structs (optional PyArrow)

With `pip install polypandas[pyarrow]`, nested dataclasses become **proper struct columns** (PyArrow-backed). Without PyArrow they are object columns of dicts.

```python
from dataclasses import dataclass
from polypandas import pandas_factory

@dataclass
class Address:
    street: str
    city: str
    zipcode: str

@pandas_factory
@dataclass
class Person:
    id: int
    name: str
    address: Address

# Auto: use PyArrow when available and model has nested structs
df = Person.build_dataframe(size=50)

# Force PyArrow (when installed)
df = Person.build_dataframe(size=50, use_pyarrow=True)

# Force standard path (nested column = object of dicts)
df = Person.build_dataframe(size=50, use_pyarrow=False)
```

**Helpers:**

- `has_nested_structs(Model)` — `True` if the model has any nested struct or list-of-struct field.
- `infer_pyarrow_schema(Model)` — Returns a `pyarrow.Schema` when PyArrow is installed, else `None`.
- `is_pyarrow_available()` — Runtime check for PyArrow.

---

## Key features

- **Factory pattern** — Uses [polyfactory](https://github.com/litestar-org/polyfactory) for data generation.
- **Type-safe schema** — Python types become pandas dtypes automatically.
- **Robust null handling** — Schema from types avoids dtype issues with all-null columns.
- **Nested structs** — Optional PyArrow support for proper struct columns; otherwise object columns of dicts.
- **Complex types** — Lists and dicts as object columns; nested models as structs (with PyArrow) or dicts.
- **Flexible models** — Dataclasses, Pydantic v2 models, TypedDicts.
- **Testing utilities** — `assert_dataframe_equal`, `assert_schema_equal`, `assert_column_exists`, and more.
- **Data I/O** — Save/load Parquet, JSON, CSV; JSON lines for dicts.

---

## Type mapping

| Python type   | Pandas dtype     |
|---------------|------------------|
| `str`         | `object`         |
| `int`         | `int64`          |
| `float`       | `float64`        |
| `bool`        | `bool`           |
| `datetime`    | `datetime64[ns]` |
| `date`        | `datetime64[ns]` |
| `Optional[T]` | same as `T`      |
| `List[T]`     | `object`         |
| `Dict[K, V]`  | `object`         |
| Nested model  | `object` or PyArrow struct (with `[pyarrow]`) |

---

## API reference

### Factory

| API | Description |
|-----|-------------|
| `@pandas_factory` | Decorator: adds `build_dataframe`, `build_dicts`, `create_dataframe_from_dicts` to the model. |
| `PandasFactory[Model]` | Base factory class; set `__model__ = Model`. |
| `build_dataframe(size=10, schema=None, use_pyarrow=None, **kwargs)` | Build a pandas DataFrame. |
| `build_dicts(size=10, **kwargs)` | Build a list of dicts (no DataFrame). |
| `create_dataframe_from_dicts(data, schema=None)` | Turn a list of dicts into a DataFrame. |
| `build_pandas_dataframe(model, size=10, schema=None, use_pyarrow=None, **kwargs)` | One-off build without a factory class. |

### Schema

| API | Description |
|-----|-------------|
| `infer_schema(model, schema=None)` | Infer a dict of column name → pandas dtype. |
| `python_type_to_pandas_dtype(python_type)` | Map a Python type to a pandas dtype string. |
| `has_nested_structs(model)` | Whether the model has nested struct/list-of-struct fields. |
| `infer_pyarrow_schema(model)` | PyArrow schema for the model, or `None` if PyArrow not installed. |

### Runtime

| API | Description |
|-----|-------------|
| `is_pandas_available()` | Whether pandas can be imported. |
| `is_pyarrow_available()` | Whether PyArrow can be imported. |

### Testing

| API | Description |
|-----|-------------|
| `assert_dataframe_equal(df1, df2, ...)` | Compare DataFrames (optional order, dtypes, tolerances). |
| `assert_schema_equal(df1, df2, ...)` | Compare column dtypes. |
| `assert_dtypes_equal(df1, df2, ...)` | Alias for schema/dtype comparison. |
| `assert_approx_count(df, expected_count, tolerance=0.1)` | Assert row count within tolerance. |
| `assert_column_exists(df, *columns)` | Assert columns exist. |
| `assert_no_duplicates(df, columns=None)` | Assert no duplicate rows. |
| `get_column_stats(df, column)` | Basic stats (count, nulls, distinct, min/max/mean for numeric). |

### I/O

| API | Description |
|-----|-------------|
| `save_as_parquet(df, path, **kwargs)` | Save DataFrame as Parquet. |
| `save_as_json(df, path, **kwargs)` | Save as JSON. |
| `save_as_csv(df, path, header=True, **kwargs)` | Save as CSV. |
| `load_parquet(path, **kwargs)` | Load Parquet into DataFrame. |
| `load_json(path, **kwargs)` | Load JSON. |
| `load_csv(path, **kwargs)` | Load CSV. |
| `load_and_validate(path, expected_schema=None, ...)` | Load and optionally validate columns/dtypes. |
| `save_dicts_as_json(data, path)` | Save list of dicts as JSON lines. |
| `load_dicts_from_json(path)` | Load JSON lines into list of dicts. |

### Exceptions

- `PolypandasError` — base
- `PandasNotAvailableError` — pandas required but not installed
- `SchemaInferenceError` — schema cannot be inferred
- `UnsupportedTypeError` — type has no pandas/PyArrow mapping
- `DataIOError` — I/O failure
- `DataFrameComparisonError` — assertion failure in testing helpers

---

## Testing utilities

```python
from polypandas import (
    assert_dataframe_equal,
    assert_schema_equal,
    assert_approx_count,
    assert_column_exists,
    assert_no_duplicates,
    get_column_stats,
)

assert_dataframe_equal(df1, df2, check_order=False, rtol=1e-5)
assert_schema_equal(df1, df2)
assert_column_exists(df, "user_id", "name", "email")
assert_no_duplicates(df, columns=["user_id"])
stats = get_column_stats(df, "amount")
```

---

## Data I/O

**DataFrames:**

```python
from polypandas import (
    save_as_parquet,
    save_as_json,
    save_as_csv,
    load_parquet,
    load_json,
    load_csv,
    load_and_validate,
    infer_schema,
)

save_as_parquet(df, "users.parquet")
save_as_csv(df, "users.csv", header=True)

df = load_parquet("users.parquet")
df = load_and_validate("users.parquet", expected_schema=infer_schema(User))
```

**JSON lines (list of dicts):**

```python
from polypandas import save_dicts_as_json, load_dicts_from_json

dicts = User.build_dicts(size=100)
save_dicts_as_json(dicts, "users.jsonl")
loaded = load_dicts_from_json("users.jsonl")
```

---

## License & related

- **License:** MIT — see [LICENSE](LICENSE).
- **Docs:** [docs/roadmap.md](docs/roadmap.md) for roadmap and ideas.
- **Related:** [polyspark](https://github.com/eddiethedean/polyspark), [polyfactory](https://github.com/litestar-org/polyfactory).
