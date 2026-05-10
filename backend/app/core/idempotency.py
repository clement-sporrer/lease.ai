import time
from typing import Any

_STORE: dict[str, tuple[Any, float]] = {}
_TTL_SECONDS = 86_400  # 24 hours


def get(key: str) -> Any | None:
    entry = _STORE.get(key)
    if entry is None:
        return None
    value, expires_at = entry
    if time.monotonic() > expires_at:
        del _STORE[key]
        return None
    return value


def set_key(key: str, value: Any) -> None:
    _STORE[key] = (value, time.monotonic() + _TTL_SECONDS)
