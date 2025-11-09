"""Caching helpers for visualization payloads."""

from __future__ import annotations

import logging
from typing import Any, Optional

from consultantos.cache import get_disk_cache
from consultantos.config import settings

logger = logging.getLogger(__name__)

_NAMESPACE = "viz_json"


def _key(name: str) -> str:
    return f"{_NAMESPACE}:{name}"


def get_cached_figure(name: str) -> Optional[Any]:
    cache = get_disk_cache()
    if cache is None:
        logger.debug(f"Cache unavailable, cache miss for figure: {name}")
        return None
    try:
        result = cache.get(_key(name))
        if result is None:
            logger.debug(f"Cache miss for figure: {name}")
        return result
    except Exception as e:
        logger.error(f"Error retrieving cached figure '{name}': {e}", exc_info=True)
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
