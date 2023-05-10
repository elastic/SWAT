
from functools import cache
from typing import Any, Optional, Type, TypeVar

import marshmallow_dataclass
from marshmallow import Schema

T = TypeVar('T')
ClassT = TypeVar('ClassT')


def _strip_none_from_dict(obj: T) -> T:
    """Strip none values from a dict recursively."""
    if isinstance(obj, dict):
        return {key: _strip_none_from_dict(value) for key, value in obj.items() if value is not None}
    if isinstance(obj, list):
        return [_strip_none_from_dict(o) for o in obj]
    if isinstance(obj, tuple):
        return tuple(_strip_none_from_dict(list(obj)))
    return obj


class MarshmallowDataclassMixin:
    """Mixin class for marshmallow serialization."""

    @classmethod
    @cache
    def __schema(cls: ClassT) -> Schema:
        """Get the marshmallow schema for the data class"""
        return marshmallow_dataclass.class_schema(cls)()

    def get(self, key: str, default: Optional[Any] = None):
        """Get a key from the query data without raising attribute errors."""
        return getattr(self, key, default)

    @classmethod
    def from_dict(cls: Type[ClassT], obj: dict) -> ClassT:
        """Deserialize and validate a dataclass from a dict using marshmallow."""
        schema = cls.__schema()
        return schema.load(obj)

    def to_dict(self, strip_none_values=True) -> dict:
        """Serialize a dataclass to a dictionary using marshmallow."""
        schema = self.__schema()
        serialized: dict = schema.dump(self)

        if strip_none_values:
            serialized = _strip_none_from_dict(serialized)

        return serialized
