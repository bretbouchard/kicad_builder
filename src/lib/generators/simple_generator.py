from __future__ import annotations

from pathlib import Path
from typing import Any

from src.lib.base_generator import BaseGenerator


class SimpleGenerator(BaseGenerator):
    """A minimal generator used for testing: writes a placeholder file."""

    def __init__(self) -> None:
        super().__init__(name="simple")

    def generate(self, config: Any, out_dir: Path) -> Path:
        out = out_dir / "simple.txt"
        out.write_text(f"project: {getattr(config, 'project_name', 'unknown')}\n")
        return out

    def validate(self, config: Any) -> bool:
        return bool(getattr(config, "project_name", None))


# Export a module-level GENERATOR value so auto-registration can pick it up.
GENERATOR = SimpleGenerator()
