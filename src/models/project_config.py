from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    project_name: str = Field(..., description="Project name")
    project_type: str = Field(..., description="Project type id/name")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=lambda: {})

    # pydantic v2: model_config is a class attribute controlling behavior
    # keep un-annotated to avoid overriding BaseModel's ConfigDict typing
    model_config = {"extra": "allow"}

    def as_dict(self) -> Dict[str, Any]:
        """Return a plain dict representation of the config."""
        return self.model_dump()
