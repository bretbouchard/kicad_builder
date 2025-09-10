from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    project_name: str = Field(..., description="Project name")
    project_type: str = Field(..., description="Project type id/name")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = {"extra": "allow"}

    def as_dict(self) -> Dict[str, Any]:
        return self.model_dump()
