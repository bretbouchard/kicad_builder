from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.models.project_config import ProjectConfig

try:
    import jsonschema
except Exception:  # pragma: no cover - optional dependency
    jsonschema = None


class ValidationError(Exception):
    """Raised when validation fails."""


def validate_project_config(config: ProjectConfig, rules: Optional[List[Dict[str, Any]]] = None) -> bool:
    """Validate a ProjectConfig.

    If `rules` (a list of JSON Schema fragments) are provided and `jsonschema` is
    available, validate against them. Otherwise perform basic required-field checks.
    Returns True on success or raises ValidationError on failure.
    """
    # Basic required checks via Pydantic: ensure instance type
    if not isinstance(config, ProjectConfig):
        raise ValidationError("config must be a ProjectConfig instance")

    if not rules:
        # minimal sanity checks
        if not getattr(config, "project_name", None):
            raise ValidationError("project_name is required")
        if not getattr(config, "project_type", None):
            raise ValidationError("project_type is required")
        return True

    if jsonschema is None:
        # Can't run rule-based checks without jsonschema.
        raise ValidationError("jsonschema not available to validate rules")

    # Validate using provided jsonschema rules
    for idx, rule in enumerate(rules):
        try:
            jsonschema.validate(instance=config.model_dump(), schema=rule)
        except Exception as exc:
            raise ValidationError(f"rule {idx} failed: {exc}") from exc

    return True
