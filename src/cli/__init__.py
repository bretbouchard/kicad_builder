from __future__ import annotations

"""CLI entry point package. Exposes submodules for legacy imports."""

from importlib import import_module


def _load(name: str):
    try:
        return import_module(f"src.cli.{name}")
    except Exception:
        return None


generate = _load("generate")
validate = _load("validate")

# Auto-register generators when the CLI package is imported so the
# `kb-generate` command finds available generators without extra wiring.
from src.services.auto_register import auto_register_generators

auto_register_generators()

__all__ = ["generate", "validate"]
