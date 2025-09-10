from __future__ import annotations
from pathlib import Path
from types import ModuleType
from typing import List
import importlib.util
import sys


def discover(plugins_dir: Path) -> List[Path]:
    """Return python files in the plugins_dir (non-recursive)."""
    if not plugins_dir.exists():
        return []
    files = []
    for p in plugins_dir.iterdir():
        if p.suffix == ".py" and p.is_file():
            files.append(p)
    return files


def load(path: Path) -> ModuleType:
    """Dynamically load a plugin module from a python file path."""
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot create spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    loader = spec.loader
    assert loader is not None
    loader.exec_module(mod)
    # Ensure module is importable by name in sys.modules
    sys.modules[mod.__name__] = mod
    return mod


def register(module: ModuleType) -> None:
    """Placeholder hook to register plugins into runtime registries.

    For now this is a no-op; real implementations will call into generator
    registries to register available generators.
    """
    return None
