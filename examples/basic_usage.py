"""Basic usage of polypandas with dataclasses."""

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
