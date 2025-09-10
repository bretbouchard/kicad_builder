"""Provide a tiny compatibility shim for pydantic BaseModel used in tests.

If the real `pydantic` package is available it will be used. Otherwise a
minimal dataclass-like fallback is provided so import-time behavior doesn't
blow up during lightweight tests.
"""

from __future__ import annotations

try:
    from pydantic import BaseModel, Field  # type: ignore
except Exception:  # pragma: no cover - fallback for environments without pydantic
    # Minimal fallback: simple dataclass-like object with model_validate/model_dump
    from dataclasses import asdict
    from typing import Any

    class Field:  # pragma: no cover - placeholder
        def __init__(self, *args, **kwargs):
            pass

    class BaseModel:  # pragma: no cover - very small compatibility layer
        def __init__(self, **data: Any) -> None:
            for k, v in data.items():
                setattr(self, k, v)

        @classmethod
        def model_validate(cls, data: Any) -> "BaseModel":
            if isinstance(data, cls):
                return data
            if isinstance(data, dict):
                return cls(**data)
            raise TypeError("unsupported data for model_validate")

        def model_dump(self) -> dict:
            # best-effort conversion
            try:
                return asdict(self)  # type: ignore[attr-defined]
            except Exception:
                return {k: getattr(self, k) for k in self.__dict__.keys()}
