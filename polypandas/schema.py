"""Schema inference and dtype conversion for pandas."""

from dataclasses import fields as dataclass_fields
from dataclasses import is_dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional, Type, Union, get_args, get_origin

from typing_extensions import get_type_hints

from polypandas.exceptions import SchemaInferenceError, UnsupportedTypeError


def is_optional(type_hint: Type) -> bool:
    """Check if a type hint is Optional (Union with None)."""
    origin = get_origin(type_hint)
    if origin is Union:
        args = get_args(type_hint)
        return type(None) in args
    return False


def unwrap_optional(type_hint: Type) -> Type:
    """Unwrap Optional type to get the inner type."""
    if is_optional(type_hint):
        args = get_args(type_hint)
        non_none_args = [arg for arg in args if arg is not type(None)]
        if non_none_args:
            return non_none_args[0]
    return type_hint


def infer_literal_type(literal_type: Type) -> Type:
    """Infer the base type from a Literal type."""
    origin = get_origin(literal_type)
    if origin is not Literal:
        return literal_type

    args = get_args(literal_type)
    if not args:
        raise SchemaInferenceError(f"Empty Literal type: {literal_type}")

    value_types = [type(arg) for arg in args]
    if len(set(value_types)) == 1:
        return value_types[0]

    if all(t in (int, float) for t in value_types):
        return float if float in value_types else int
    if all(t is str for t in value_types):
        return str
    if all(t is bool for t in value_types):
        return bool

    raise SchemaInferenceError(
        f"Cannot infer unified type from Literal with mixed types: {literal_type}"
    )


def python_type_to_pandas_dtype(python_type: Type) -> Any:
    """Convert a Python type to a pandas dtype (string or dtype).

    Returns a string like 'int64', 'float64', 'object', 'bool', 'datetime64[ns]'
    when pandas is not available; otherwise can return actual numpy/pandas dtypes.

    Args:
        python_type: The Python type to convert.

    Returns:
        A string or dtype suitable for pandas DataFrame.

    Raises:
        UnsupportedTypeError: If the type cannot be converted.
    """
    if is_optional(python_type):
        python_type = unwrap_optional(python_type)

    origin = get_origin(python_type)
    if origin is Literal:
        python_type = infer_literal_type(python_type)

    origin = get_origin(python_type)
    args = get_args(python_type)

    type_mapping = {
        str: "object",
        int: "int64",
        float: "float64",
        bool: "bool",
        bytes: "object",
        bytearray: "object",
        date: "datetime64[ns]",
        datetime: "datetime64[ns]",
        Decimal: "object",
    }

    if python_type in type_mapping:
        return type_mapping[python_type]

    if origin in (list, List):
        if not args:
            raise SchemaInferenceError(f"Cannot infer array element type from {python_type}")
        return "object"  # pandas object dtype for list columns

    if origin in (dict, Dict):
        return "object"  # pandas object dtype for dict columns

    if is_dataclass(python_type):
        return "object"  # nested struct as object

    if hasattr(python_type, "model_fields"):
        return "object"

    if hasattr(python_type, "__annotations__"):
        return "object"

    raise UnsupportedTypeError(f"Cannot convert type {python_type} to pandas dtype")


def _get_model_field_types(model: Type) -> Dict[str, Type]:
    """Get field name -> type mapping from a model."""
    if is_dataclass(model):
        type_hints = get_type_hints(model)
        return {f.name: type_hints.get(f.name, f.type) for f in dataclass_fields(model)}
    if hasattr(model, "model_fields"):
        return {name: info.annotation for name, info in model.model_fields.items()}
    if hasattr(model, "__annotations__"):
        return dict(model.__annotations__)
    raise SchemaInferenceError(f"Cannot infer schema from {model}")


def infer_schema(
    model: Type,
    schema: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Infer a pandas dtype dict from a model type.

    Args:
        model: The model type (dataclass, Pydantic, TypedDict).
        schema: Optional explicit dtype dict (column name -> dtype). If provided, returned as-is.

    Returns:
        A dict mapping column names to pandas dtypes (strings or dtypes).

    Raises:
        SchemaInferenceError: If schema cannot be inferred.
    """
    if schema is not None and isinstance(schema, dict):
        return schema

    try:
        field_types = _get_model_field_types(model)
    except Exception as e:
        raise SchemaInferenceError(f"Cannot infer schema from {model}: {e}") from e

    result = {}
    for field_name, field_type in field_types.items():
        try:
            result[field_name] = python_type_to_pandas_dtype(field_type)
        except UnsupportedTypeError as e:
            raise SchemaInferenceError(f"Cannot infer type for field {field_name}: {e}") from e

    return result


def infer_dtypes_for_dataframe(model: Type) -> Optional[Dict[str, Any]]:
    """Infer dtypes dict suitable for pd.DataFrame(..., dtype=...).

    Returns None if pandas is not available (caller can omit dtype and let inference happen).
    """
    return infer_schema(model)


def _is_struct_like(type_hint: Type) -> bool:
    """True if the type is a dataclass, Pydantic model, or TypedDict (nested struct)."""
    if is_dataclass(type_hint):
        return True
    if get_origin(type_hint) in (list, List):
        args = get_args(type_hint)
        if args and (is_dataclass(args[0]) or hasattr(args[0], "model_fields")):
            return True
    if hasattr(type_hint, "model_fields"):
        return True
    if hasattr(type_hint, "__annotations__") and get_origin(type_hint) not in (list, List, dict, Dict):
        return True
    return False


def has_nested_structs(model: Type) -> bool:
    """Return True if the model has any field that is a nested struct (dataclass, Pydantic, etc.) or list of structs."""
    try:
        field_types = _get_model_field_types(model)
    except Exception:
        return False
    for field_type in field_types.values():
        t = unwrap_optional(field_type)
        if _is_struct_like(t):
            return True
        if get_origin(t) in (list, List):
            args = get_args(t)
            if args and _is_struct_like(args[0]):
                return True
    return False


def infer_pyarrow_schema(model: Type) -> Optional[Any]:
    """Infer a PyArrow Schema from the model type.

    Returns None if PyArrow is not installed or schema cannot be inferred.
    Requires the optional dependency: pip install polypandas[pyarrow]
    """
    try:
        import pyarrow as pa
    except ImportError:
        return None

    def python_type_to_pa(python_type: Type, nullable: bool = True) -> Any:
        if is_optional(python_type):
            python_type = unwrap_optional(python_type)
            nullable = True
        origin = get_origin(python_type)
        if origin is Literal:
            python_type = infer_literal_type(python_type)
            origin = None
        args = get_args(python_type) if origin else ()

        if python_type in (str, int, float, bool):
            type_map = {str: pa.string(), int: pa.int64(), float: pa.float64(), bool: pa.bool_()}
            return type_map[python_type]
        if python_type is bytes or python_type is bytearray:
            return pa.binary()
        if python_type is date:
            return pa.date32()
        if python_type is datetime:
            return pa.timestamp("us")
        if python_type is Decimal:
            return pa.decimal128(38, 9)

        if origin in (list, List) and args:
            inner = python_type_to_pa(args[0], nullable=True)
            return pa.list_(inner)
        if origin in (dict, Dict) and len(args) >= 2:
            k = python_type_to_pa(args[0], nullable=False)
            v = python_type_to_pa(args[1], nullable=True)
            return pa.map_(k, v)

        if is_dataclass(python_type):
            fields = []
            type_hints = get_type_hints(python_type)
            for f in dataclass_fields(python_type):
                ft = type_hints.get(f.name, f.type)
                n = is_optional(ft)
                pa_type = python_type_to_pa(ft, nullable=n)
                fields.append(pa.field(f.name, pa_type, nullable=n))
            return pa.struct(fields)

        if hasattr(python_type, "model_fields"):
            fields = []
            for name, info in python_type.model_fields.items():
                ft = info.annotation
                n = not info.is_required() or is_optional(ft)
                pa_type = python_type_to_pa(ft, nullable=n)
                fields.append(pa.field(name, pa_type, nullable=n))
            return pa.struct(fields)

        if hasattr(python_type, "__annotations__"):
            required = getattr(python_type, "__required_keys__", set())
            fields = []
            for name, ft in python_type.__annotations__.items():
                n = name not in required or is_optional(ft)
                pa_type = python_type_to_pa(ft, nullable=n)
                fields.append(pa.field(name, pa_type, nullable=n))
            return pa.struct(fields)

        return None

    try:
        field_types = _get_model_field_types(model)
    except Exception:
        return None

    pa_fields = []
    for field_name, field_type in field_types.items():
        nullable = is_optional(field_type)
        pa_type = python_type_to_pa(field_type, nullable=nullable)
        if pa_type is None:
            return None
        pa_fields.append(pa.field(field_name, pa_type, nullable=nullable))

    return pa.schema(pa_fields)
