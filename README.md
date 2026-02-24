# Polypandas

**Generate type-safe pandas DataFrames effortlessly using polyfactory**

Inspired by [polyspark](https://github.com/eddiethedean/polyspark).

## Why Polypandas?

Creating test data for pandas applications is tedious. Polypandas makes it **effortless** by generating realistic test DataFrames from your Python data models — with **automatic schema inference** so columns have the right dtypes even when values are null.

```python
from dataclasses import dataclass
from polypandas import pandas_factory

@pandas_factory
@dataclass
class User:
    id: int
    name: str
    email: str

# Generate 1000 rows instantly:
df = User.build_dataframe(size=1000)
```

## Installation

```bash
pip install polypandas
```

For development with test and lint tools:

```bash
pip install "polypandas[dev]"
```

## Quick Start

### Using the decorator (recommended)

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

# Generate a DataFrame with 100 rows
df = Product.build_dataframe(size=100)
print(df.head())
```

You can also generate data as lists of dicts:

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

### Convenience function

```python
from polypandas import build_pandas_dataframe

df = build_pandas_dataframe(Product, size=100)
```

## Key features

- **Factory pattern**: Uses [polyfactory](https://github.com/litestar-org/polyfactory) for data generation
- **Type-safe schema**: Python types become pandas dtypes automatically
- **Robust null handling**: Schema from types avoids dtype issues with all-null columns
- **Complex types**: Supports nested structs, lists, dicts (as object columns)
- **Flexible models**: Dataclasses, Pydantic models, TypedDicts
- **Testing utilities**: `assert_dataframe_equal`, `assert_schema_equal`, `assert_column_exists`, etc.
- **Data I/O**: Save/load Parquet, JSON, CSV via thin wrappers

## Type mapping

| Python type   | Pandas dtype     |
|---------------|------------------|
| `str`         | `object`         |
| `int`         | `int64`          |
| `float`       | `float64`        |
| `bool`        | `bool`           |
| `datetime`    | `datetime64[ns]` |
| `Optional[T]` | same as T        |
| `List[T]`     | `object`         |
| `Dict[K,V]`   | `object`         |

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

## Data I/O

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

JSON lines (dicts):

```python
from polypandas import save_dicts_as_json, load_dicts_from_json

dicts = User.build_dicts(size=100)
save_dicts_as_json(dicts, "users.jsonl")
loaded = load_dicts_from_json("users.jsonl")
```

## License

MIT — see [LICENSE](LICENSE).

## Related

- [polyspark](https://github.com/eddiethedean/polyspark) — related project
- [polyfactory](https://github.com/litestar-org/polyfactory) — factory library for mock data
