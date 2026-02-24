"""Basic usage of polypandas with dataclasses.

See the project README for full docs: decorator, factory class, nested structs (PyArrow),
testing utilities, and I/O.

Run with: python examples/basic_usage.py

Example output (sample run; data varies):
-----------------------------------------
Generated dicts (first 2): [{'id': 5794, 'name': 'FAzDefKOpYGSwvowbttu', 'email': 'dmFqxuGeHyRnkYIlImuM'}, {'id': 7251, 'name': 'rPwDCYEejBFEGdrVobLg', 'email': 'RjSJmnHPPrRmklPkfTGz'}]

DataFrame shape: (100, 5)

First 3 rows:
   product_id                  name  ...           description in_stock
0        5664  aOLpLfAKrUlgjUzSZhso  ...  ShsQZozAZtPmJqGHwfcm     True
1        5673  bZfTDNycbuWDwXCJcbov  ...  eEmXXenKOYVPYUCoNRXa     True
2        1716  fnMoLyjGwigUyCwjGWPn  ...  owCcYWWbAMGjLvmKmDgd    False

[3 rows x 5 columns]

Dtypes: {'product_id': dtype('int64'), 'name': dtype('O'), 'price': dtype('float64'), 'description': dtype('O'), 'in_stock': dtype('bool')}
"""

from dataclasses import dataclass
from typing import Optional

from polypandas import pandas_factory


@pandas_factory
@dataclass
class User:
    id: int
    name: str
    email: str


@pandas_factory
@dataclass
class Product:
    product_id: int
    name: str
    price: float
    description: Optional[str] = None
    in_stock: bool = True


def main():
    dicts = User.build_dicts(size=5)
    print("Generated dicts (first 2):", dicts[:2])

    df = Product.build_dataframe(size=100)
    print("\nDataFrame shape:", df.shape)
    print("\nFirst 3 rows:")
    print(df.head(3))
    print("\nDtypes:", df.dtypes.to_dict())


if __name__ == "__main__":
    main()
