# Polypandas roadmap

High-level direction and possible future work for polypandas.

---

## Done

- **Core factory** — `PandasFactory`, `@pandas_factory`, `build_dataframe`, `build_dicts`, `create_dataframe_from_dicts`
- **Schema** — Inference from dataclasses, Pydantic v2, TypedDict → pandas dtypes; `infer_schema`, `python_type_to_pandas_dtype`
- **Nested structs (optional PyArrow)** — `pip install polypandas[pyarrow]` for proper struct columns; `has_nested_structs()`, `infer_pyarrow_schema()`, `use_pyarrow` in `build_dataframe()` and `build_pandas_dataframe()`
- **Convenience API** — `build_pandas_dataframe(model, size=..., ...)`
- **Testing** — `assert_dataframe_equal`, `assert_schema_equal`, `assert_dtypes_equal`, `assert_approx_count`, `assert_column_exists`, `assert_no_duplicates`, `get_column_stats`
- **Data I/O** — Parquet, JSON, CSV (DataFrames); `save_dicts_as_json` / `load_dicts_from_json` (dicts)
- **Dependencies** — Pandas required; PyArrow optional

---

## Under consideration

- **CLI** — Export schema, generate sample data, validate files (e.g. polyspark-style CLI)
- **List-of-struct columns** — Clearer handling/docs for `List[SomeDataclass]` with PyArrow
- **Type stubs** — `py.typed` and/or stubs for better editor/IDE support

---

## Future ideas

- **Reproducibility** — Document or helpers for reproducible DataFrames (e.g. polyfactory seed)
- **Performance** — Benchmarks and optional optimizations for large `size` (e.g. chunked generation)
- **Extra I/O** — Excel, Feather, or other formats via pandas

---

*This roadmap is a living doc and may change as the project evolves.*
