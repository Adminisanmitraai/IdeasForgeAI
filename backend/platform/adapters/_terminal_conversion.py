from __future__ import annotations

import dataclasses
import types
from typing import Any, Mapping, Union, get_args, get_origin, get_type_hints


class TerminalAdapterInputError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def construct_dataclass(model: type[Any], payload: Any) -> Any:
    """Hydrate a legacy dataclass without importing the HTTP adapter."""
    if isinstance(payload, model):
        return payload
    if not isinstance(payload, Mapping):
        raise TerminalAdapterInputError(
            "invalid_legacy_payload",
            f"{model.__name__} requires an object.",
        )

    fields = {item.name: item for item in dataclasses.fields(model)}
    unknown = sorted(set(payload) - set(fields))
    if unknown:
        raise TerminalAdapterInputError(
            "unknown_legacy_fields",
            f"Unknown fields for {model.__name__}: {', '.join(unknown)}",
        )

    hints = get_type_hints(model)
    values: dict[str, Any] = {}
    for name, item in fields.items():
        if name in payload:
            values[name] = hydrate(hints.get(name, item.type), payload[name])
        elif item.default is dataclasses.MISSING and item.default_factory is dataclasses.MISSING:
            raise TerminalAdapterInputError(
                "missing_legacy_field",
                f"Missing required field for {model.__name__}: {name}",
            )
    return model(**values)


def hydrate(annotation: Any, value: Any) -> Any:
    if annotation is Any:
        return value

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin in (Union, types.UnionType):
        if value is None and type(None) in args:
            return None
        for candidate in args:
            if candidate is type(None):
                continue
            try:
                return hydrate(candidate, value)
            except (TypeError, ValueError, TerminalAdapterInputError):
                continue
        return value

    if origin is list:
        if not isinstance(value, list):
            raise TerminalAdapterInputError("invalid_legacy_type", "Expected an array.")
        item_type = args[0] if args else Any
        return [hydrate(item_type, item) for item in value]

    if origin is tuple:
        if not isinstance(value, (list, tuple)):
            raise TerminalAdapterInputError("invalid_legacy_type", "Expected an array.")
        item_type = args[0] if args else Any
        return tuple(hydrate(item_type, item) for item in value)

    if origin in (dict, Mapping):
        if not isinstance(value, Mapping):
            raise TerminalAdapterInputError("invalid_legacy_type", "Expected an object.")
        key_type = args[0] if args else str
        value_type = args[1] if len(args) > 1 else Any
        return {
            hydrate(key_type, key): hydrate(value_type, item)
            for key, item in value.items()
        }

    if isinstance(annotation, type) and dataclasses.is_dataclass(annotation):
        return construct_dataclass(annotation, value)

    if annotation in (str, int, float, bool):
        if annotation is bool and not isinstance(value, bool):
            raise TerminalAdapterInputError("invalid_legacy_type", "Expected a boolean.")
        return annotation(value)

    return value


def metadata_value(metadata: Mapping[str, Any], name: str) -> Any:
    value = metadata.get(name)
    if value is None:
        raise TerminalAdapterInputError(
            "missing_legacy_payload",
            f"Adapter metadata must contain {name}.",
        )
    return value


def jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {key: jsonable(item) for key, item in dataclasses.asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [jsonable(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "__dict__"):
        return {
            str(key): jsonable(item)
            for key, item in vars(value).items()
            if not str(key).startswith("_")
        }
    return str(value)
