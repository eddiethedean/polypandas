"""PandasFactory class for generating pandas DataFrames."""

import functools
from abc import ABC
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Optional, Type, TypeVar

from polyfactory.factories import DataclassFactory

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = None  # type: ignore[assignment, misc]

from polypandas.exceptions import PandasNotAvailableError
from polypandas.protocols import is_pandas_available, is_pyarrow_available
from polypandas.schema import has_nested_structs, infer_pyarrow_schema, infer_schema

T = TypeVar("T")


def _instances_to_dicts(instances: List[Any]) -> List[Dict[str, Any]]:
    """Convert a list of model instances to list of dicts."""
    dicts = []
    for instance in instances:
        if is_dataclass(instance):
            dicts.append(asdict(instance))  # type: ignore[arg-type]
        elif BaseModel is not None and isinstance(instance, BaseModel):
            dicts.append(instance.model_dump())
        elif isinstance(instance, dict):
            dicts.append(instance)
        else:
            try:
                dicts.append(dict(instance))  # type: ignore[call-overload]
            except (TypeError, ValueError):
                dicts.append(instance.__dict__)
    return dicts


class PandasFactory(DataclassFactory[T], ABC):
    """Factory for generating pandas DataFrames from models.

    Works with dataclasses, Pydantic models, and TypedDicts.

    Example:
        ```python
        from dataclasses import dataclass
        from polypandas import PandasFactory

        @dataclass
        class User:
            id: int
            name: str
            email: str

        class UserFactory(PandasFactory[User]):
            __model__ = User

        df = UserFactory.build_dataframe(size=100)
        ```
    """

    __is_base_factory__ = True

    @classmethod
    def build_dataframe(
        cls,
        size: int = 10,
        schema: Optional[Dict[str, Any]] = None,
        use_pyarrow: Optional[bool] = None,
        **kwargs: Any,
    ) -> Any:
        """Build a pandas DataFrame with generated data.

        When PyArrow is installed (pip install polypandas[pyarrow]) and the model
        has nested structs, the DataFrame uses PyArrow-backed dtypes for proper
        nested columns. Set use_pyarrow=False to always use the standard path.

        Args:
            size: Number of rows to generate.
            schema: Optional explicit dtype dict (column name -> dtype). If None, inferred from model.
                Ignored when use_pyarrow is True and PyArrow schema is used.
            use_pyarrow: If None, use PyArrow when available and model has nested structs.
                If True, use PyArrow when available. If False, never use PyArrow.
            **kwargs: Additional keyword arguments passed to the factory.

        Returns:
            A pandas DataFrame with generated data.

        Raises:
            PandasNotAvailableError: If pandas is not installed.
        """
        if not is_pandas_available():
            raise PandasNotAvailableError()

        import pandas as pd

        model = cls.__model__
        data = cls.build_dicts(size=size, **kwargs)

        if use_pyarrow is None:
            use_pyarrow = is_pyarrow_available() and has_nested_structs(model)

        if use_pyarrow and is_pyarrow_available():
            pa_schema = infer_pyarrow_schema(model)
            if pa_schema is not None:
                import pyarrow as pa

                table = pa.Table.from_pylist(data, schema=pa_schema)
                if hasattr(pd, "ArrowDtype"):
                    return table.to_pandas(types_mapper=pd.ArrowDtype)
                return table.to_pandas()

        dtypes = infer_schema(model, schema)
        df = pd.DataFrame(data)
        if dtypes:
            df = df.astype(dtypes)
        return df

    @classmethod
    def build_dicts(
        cls,
        size: int = 10,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Build a list of dictionaries with generated data.

        Does not require pandas. Use create_dataframe_from_dicts() later to convert to DataFrame.

        Args:
            size: Number of records to generate.
            **kwargs: Additional keyword arguments passed to the factory.

        Returns:
            A list of dictionaries with generated data.
        """
        instances = cls.batch(size=size, **kwargs)
        return _instances_to_dicts(instances)

    @classmethod
    def create_dataframe_from_dicts(
        cls,
        data: List[Dict[str, Any]],
        schema: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Convert pre-generated dictionary data to a pandas DataFrame.

        Args:
            data: List of dictionaries to convert.
            schema: Optional explicit dtype dict.

        Returns:
            A pandas DataFrame.

        Raises:
            PandasNotAvailableError: If pandas is not installed.
        """
        if not is_pandas_available():
            raise PandasNotAvailableError()

        import pandas as pd

        dtypes = infer_schema(cls.__model__, schema)
        return pd.DataFrame(data, dtype=object).astype(dtypes)


def build_pandas_dataframe(
    model: Type[T],
    size: int = 10,
    schema: Optional[Dict[str, Any]] = None,
    use_pyarrow: Optional[bool] = None,
    **kwargs: Any,
) -> Any:
    """Convenience function to build a DataFrame without creating a factory class.

    Args:
        model: The model type (dataclass, Pydantic, TypedDict).
        size: Number of rows to generate.
        schema: Optional explicit dtype dict.
        use_pyarrow: If None, use PyArrow when available and model has nested structs.
            If True/False, use or skip PyArrow. See PandasFactory.build_dataframe.
        **kwargs: Additional keyword arguments for data generation.

    Returns:
        A pandas DataFrame with generated data.
    """
    factory_class = type(
        f"{model.__name__}Factory",
        (PandasFactory,),
        {"__model__": model, "__is_base_factory__": False},
    )
    return factory_class.build_dataframe(  # type: ignore[attr-defined]
        size=size, schema=schema, use_pyarrow=use_pyarrow, **kwargs
    )


def pandas_factory(cls: Type[T]) -> Type[T]:
    """Decorator to add factory methods directly to a model class.

    Adds classmethods: build_dataframe, build_dicts, create_dataframe_from_dicts.

    Example:
        ```python
        from dataclasses import dataclass
        from polypandas import pandas_factory

        @pandas_factory
        @dataclass
        class User:
            id: int
            name: str
            email: str

        df = User.build_dataframe(size=100)
        dicts = User.build_dicts(size=50)
        ```
    """
    if BaseModel is not None and isinstance(cls, type) and issubclass(cls, BaseModel):
        try:
            from polyfactory.factories.pydantic_factory import ModelFactory as PydanticModelFactory

            class _PydanticPandasFactory(PydanticModelFactory):
                __is_base_factory__ = True

                @classmethod
                def build_dataframe(cls, *args: Any, **kwargs: Any) -> Any:
                    return PandasFactory.build_dataframe.__func__(cls, *args, **kwargs)  # type: ignore[attr-defined]

                @classmethod
                def build_dicts(cls, *args: Any, **kwargs: Any) -> Any:
                    return PandasFactory.build_dicts.__func__(cls, *args, **kwargs)  # type: ignore[attr-defined]

                @classmethod
                def create_dataframe_from_dicts(cls, *args: Any, **kwargs: Any) -> Any:
                    return PandasFactory.create_dataframe_from_dicts.__func__(cls, *args, **kwargs)  # type: ignore[attr-defined]

            factory_class = type(
                f"_{cls.__name__}Factory",
                (_PydanticPandasFactory,),
                {"__model__": cls, "__is_base_factory__": False},
            )
        except ImportError:
            factory_class = type(
                f"_{cls.__name__}Factory",
                (PandasFactory,),
                {"__model__": cls, "__is_base_factory__": False},
            )
    else:
        factory_class = type(
            f"_{cls.__name__}Factory",
            (PandasFactory,),
            {"__model__": cls, "__is_base_factory__": False},
        )

    @classmethod  # type: ignore[misc]
    @functools.wraps(PandasFactory.build_dataframe)
    def build_dataframe(
        model_cls: Type[T],
        size: int = 10,
        schema: Optional[Dict[str, Any]] = None,
        use_pyarrow: Optional[bool] = None,
        **kwargs: Any,
    ) -> Any:
        return factory_class.build_dataframe(  # type: ignore[attr-defined]
            size=size, schema=schema, use_pyarrow=use_pyarrow, **kwargs
        )

    @classmethod  # type: ignore[misc]
    @functools.wraps(PandasFactory.build_dicts)
    def build_dicts(
        model_cls: Type[T],
        size: int = 10,
        **kwargs: Any,
    ) -> Any:
        return factory_class.build_dicts(size=size, **kwargs)  # type: ignore[attr-defined]

    @classmethod  # type: ignore[misc]
    @functools.wraps(PandasFactory.create_dataframe_from_dicts)
    def create_dataframe_from_dicts(
        model_cls: Type[T],
        data: List[Dict[str, Any]],
        schema: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return factory_class.create_dataframe_from_dicts(data, schema=schema)  # type: ignore[attr-defined]

    cls.build_dataframe = build_dataframe  # type: ignore[attr-defined]
    cls.build_dicts = build_dicts  # type: ignore[attr-defined]
    cls.create_dataframe_from_dicts = create_dataframe_from_dicts  # type: ignore[attr-defined]
    cls._polypandas_factory = factory_class  # type: ignore[attr-defined]

    return cls
