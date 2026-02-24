# Polypandas documentation

- **Usage, API, and examples** — see the main [README](../README.md) in the project root.
- **Roadmap and future work** — [roadmap.md](roadmap.md).

For a quick start:

```bash
pip install polypandas
pip install polypandas[pyarrow]   # optional: nested struct columns
```

Then use the decorator and generate DataFrames:

```python
from dataclasses import dataclass
from polypandas import pandas_factory

@pandas_factory
@dataclass
class User:
    id: int
    name: str
    email: str

df = User.build_dataframe(size=1000)
```
