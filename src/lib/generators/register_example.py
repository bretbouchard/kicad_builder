from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from src.lib.base_generator import BaseGenerator


class VendorGenerator(BaseGenerator):
    def __init__(self) -> None:
        super().__init__(name="vendor/example")

    def generate(self, config: Any, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        p = out_dir / "vendor.txt"
        p.write_text("vendor example generated\n", encoding="utf8")
        return out_dir

    def validate(self, config: Any) -> bool:
        return True


def register(registry: Callable[..., None]) -> None:
    # auto_register passes the `register` function from the registry module.
    # Call it directly to register under a vendor namespace.
    registry("example", VendorGenerator(), namespace="vendor")
