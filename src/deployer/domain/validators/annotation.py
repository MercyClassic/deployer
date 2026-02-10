from collections.abc import Iterable, Mapping
from typing import Any, Union, get_args, get_origin, get_type_hints


class AnnotationValidator(type):
    @classmethod
    def check_type(cls, value: Any, expected_type: type) -> bool:
        origin = get_origin(expected_type)

        if origin is None:
            return isinstance(value, expected_type)

        if origin is Union:
            return any(cls.check_type(value, t) for t in get_args(expected_type))

        if not isinstance(value, origin):
            return False

        args = get_args(expected_type)
        if not args:
            return True

        if issubclass(origin, Mapping):
            key_type, val_type = args
            return all(
                cls.check_type(k, key_type) and cls.check_type(v, val_type)
                for k, v in value.items()
            )

        if issubclass(origin, Iterable) and not issubclass(origin, (str, bytes)):
            (item_type,) = args
            return all(cls.check_type(v, item_type) for v in value)

        return True

    def __call__(cls, **kwargs) -> None:
        annotations = get_type_hints(cls)
        values = {}

        for field, field_type in annotations.items():
            if field in kwargs:
                value = kwargs[field]
            elif hasattr(cls, field):
                value = getattr(cls, field)
            else:
                raise ValueError(f'Missing field: {field}')

            try:
                is_invalid = not cls.check_type(value, field_type)
            except (ValueError, AttributeError):
                is_invalid = True

            if is_invalid:
                raise ValueError(
                    f'Invalid type for "{field}": '
                    f'expected {field_type}, got {type(value)}',
                )

            values[field] = value

        extra = set(kwargs) - set(annotations)
        if extra:
            raise ValueError(f'Unexpected fields: {extra}')

        obj = super().__call__()
        for k, v in values.items():
            setattr(obj, k, v)

        return obj
