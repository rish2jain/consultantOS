"""ConsultantOS shared core package.

This package acts as a stable import surface for the upcoming multi-service
architecture. For now it simply re-exports the canonical modules that still
live under the legacy `consultantos` package. That allows new Cloud Run
services to depend on `consultantos_core` immediately without forcing a risky
big-bang move of every file. As we migrate code we can relocate modules into
this package while keeping the same import paths.
"""

from __future__ import annotations

import importlib
import sys
from types import ModuleType
from typing import Dict


def _expose_legacy_module(name: str) -> ModuleType:
    """Load consultantos.<name> and register it under consultantos_core.<name>."""
    try:
        module = importlib.import_module(f"consultantos.{name}")
        alias = f"{__name__}.{name}"
        sys.modules[alias] = module
        return module
    except (ModuleNotFoundError, ImportError) as exc:
        # Create a safe placeholder module that raises the original error when accessed
        alias = f"{__name__}.{name}"
        placeholder = ModuleType(alias)
        placeholder.__all__ = []
        placeholder.__import_error__ = exc
        
        def _raise_import_error(*args, **kwargs):
            raise ImportError(
                f"Failed to import consultantos.{name}: {exc}"
            ) from exc
        
        # Make the placeholder raise on attribute access
        placeholder.__getattr__ = lambda attr: _raise_import_error()
        sys.modules[alias] = placeholder
        return placeholder


_MODULE_NAMES = (
    "models",
    "config",
    "database",
    "storage",
    "auth",
    "user_management",
    "cache",
    "utils",
)

_EXPORTED: Dict[str, ModuleType] = {name: _expose_legacy_module(name) for name in _MODULE_NAMES}

# Re-export modules for `from consultantos_core import models` style imports
globals().update(_EXPORTED)
__all__ = list(_EXPORTED.keys())


def get_settings():
    """Return the global settings object from the legacy config module."""

    return _EXPORTED["config"].settings
