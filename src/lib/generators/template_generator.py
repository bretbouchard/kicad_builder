from __future__ import annotations

from pathlib import Path
from typing import Any

from ..base_generator import BaseGenerator


class TemplateGenerator(BaseGenerator):
    """A minimal template generator showing the required contract.

    Export an instance named `GENERATOR` to auto-register.
    """

    def __init__(self) -> None:
        super().__init__(name="template")

    def generate(self, config: Any, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = out_dir / "template.txt"
        stamp.write_text("template generated\n", encoding="utf8")
        return out_dir

    def validate(self, config: Any) -> bool:
        # Always valid for the template.
        return True


# Export the instance required by the auto-registerer.
GENERATOR = TemplateGenerator()
