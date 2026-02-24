"""Nested structs with optional PyArrow.

Run with: python examples/nested_structs.py

With PyArrow installed (pip install polypandas[pyarrow]), the address column
is a proper struct type. Without PyArrow, it is an object column of dicts.

Example output (sample run with PyArrow; data varies):
------------------------------------------------------
DataFrame shape: (5, 3)
Columns: ['id', 'name', 'address']

First row address (dict or struct):
  {'street': 'FThIBkuoGBLpiJArLIGF', 'city': 'hcPIAdmvVpmdYCbBqUUy', 'zipcode': 'dtLikzZOjwehoAAEvaGl'}

Dtypes:
id                                            int64[pyarrow]
name                                         string[pyarrow]
address    struct<street: string not null, city: string not null, zipcode: string not null>
dtype: object
"""

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


def main():
    df = Person.build_dataframe(size=5)
    print("DataFrame shape:", df.shape)
    print("Columns:", list(df.columns))
    print("\nFirst row address (dict or struct):")
    print(" ", df["address"].iloc[0])
    print("\nDtypes:")
    print(df.dtypes)


if __name__ == "__main__":
    main()
