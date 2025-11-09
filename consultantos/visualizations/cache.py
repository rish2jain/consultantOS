"""Caching helpers for visualization payloads."""

from __future__ import annotations

import json
from typing import Any, Optional

from consultantos.cache import get_disk_cache
from consultantos.config import settings

_NAMESPACE = "viz_json"


def _key(name: str) -> str:
    return f"{_NAMESPACE}:{name}"


def get_cached_figure(name: str) -> Optional[Any]:
    cache = get_disk_cache()
    if cache is None:
        return None
    try:
        return cache.get(_key(name))
    except Exception:
        return None


def set_cached_figure(name: str, figure: Any, ttl: Optional[int] = None) -> None:
    cache = get_disk_cache()
    if cache is None:
        return
    ttl_seconds = ttl or settings.cache_ttl_seconds
    try:
        cache.set(_key(name), figure, expire=ttl_seconds)
    except Exception:
        return
