from typing import Any
from collections.abc import Callable

SCALARS_PARSE_FUNCTIONS: dict[Any, Callable[[Any], Any]] = {}
SCALARS_SERIALIZE_FUNCTIONS: dict[Any, Callable[[Any], Any]] = {}
