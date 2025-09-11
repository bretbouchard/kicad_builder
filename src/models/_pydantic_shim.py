"""Pydantic import wrapper (no-shim policy).

This module intentionally imports the real `pydantic` package directly.
The project policy is: do not provide a runtime shim for pydantic. If
pydantic is not installed, importing this module will raise ImportError
and the developer/CI should install the dependency.
"""

from __future__ import annotations

try:
    from pydantic import BaseModel, Field
except Exception as e:  # pragma: no cover - explicit failure if pydantic missing
    raise ImportError("pydantic is required by the project. Please install it " "(e.g. 'pip install pydantic')") from e

# Re-export names for consumers
__all__ = ["BaseModel", "Field"]
