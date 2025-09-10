from typing import Dict, Any, Optional

from pydantic import BaseModel, Field


class Template(BaseModel):
    name: str = Field(...)
    files: Dict[str, Any] = Field(default_factory=dict)
    variables: Optional[Dict[str, Any]] = None

    model_config = {"extra": "forbid"}
