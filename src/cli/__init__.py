from __future__ import annotations

"""CLI entry point package. Exposes submodules for legacy imports."""

# ruff: noqa: E402

from importlib import import_module
from typing import Optional


def _load(name: str) -> Optional[object]:
    try:
        return import_module(f"src.cli.{name}")
    except Exception:
        return None


# Lazy-load CLI submodules; avoid side-effects at import time when possible.
generate = _load("generate")
validate = _load("validate")

# Auto-register generators when the CLI package is explicitly used.
# Keep the call best-effort and isolated so importing `src.cli` in
# test harnesses doesn't immediately mutate global state.
try:
    from src.services.auto_register import auto_register_generators

    try:
        auto_register_generators()
    except Exception:
        # Don't block imports if auto-registration fails in test envs.
        pass
except Exception:
    # If services aren't available at import time, skip auto-registration.
    pass

__all__ = ["generate", "validate"]
