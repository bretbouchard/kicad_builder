from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List


class BaseGenerator(ABC):
    """Abstract base class for generators.

    Concrete generators should subclass this and implement generate() and
    validate(). The registry accepts either classes or instances.
    """

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def generate(self, config: Any, out_dir: Path) -> Path:
        """Generate project artifacts and return the output path."""

    @abstractmethod
    def validate(self, config: Any) -> bool:
        """Validate the provided config for this generator."""

    def get_dependencies(self) -> List[str]:
        """Return a list of dependency names (other generators or libs)."""
        return []
