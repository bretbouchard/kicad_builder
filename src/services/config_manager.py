from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Union

from src.models.project_config import ProjectConfig


class ConfigManagerError(Exception):
    """Raised for config manager related errors."""


def load(path: Union[str, Path]) -> ProjectConfig:
    """Load a ProjectConfig from a JSON file.

    Currently only JSON is supported. Returns a validated ProjectConfig.
    """
    p = Path(path)
    if not p.exists():
        raise ConfigManagerError(f"config file not found: {p}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ConfigManagerError(f"error reading config file {p}: {exc}") from exc

    return validate(data)


def save(config: Union[ProjectConfig, Dict[str, Any]], path: Union[str, Path]) -> None:
    """Save a ProjectConfig (or raw dict) to a JSON file."""
    p = Path(path)
    if isinstance(config, ProjectConfig):
        payload = _model_dump(config)
    else:
        payload = config
    try:
        p.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        raise ConfigManagerError(f"error writing config file {p}: {exc}") from exc


def validate(data: Union[Dict[str, Any], ProjectConfig]) -> ProjectConfig:
    """Validate and return a ProjectConfig instance.

    Accepts either a dict or an existing ProjectConfig and returns a validated
    ProjectConfig object. Compatible with pydantic v1/v2.
    """
    if isinstance(data, ProjectConfig):
        return data

    try:
        return ProjectConfig.model_validate(data)  # type: ignore[attr-defined]
    except AttributeError:
        return ProjectConfig.parse_obj(data)  # type: ignore[call-arg]


def _model_dump(model: ProjectConfig) -> Dict[str, Any]:
    """Return a serializable dict from a Pydantic model (v2/v1 compatible)."""
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
