from typing import List, Optional

from pydantic import BaseModel, Field


class Generator(BaseModel):
    name: str = Field(..., description="Generator name (unique)")
    version: Optional[str] = None
    description: Optional[str] = None
    entrypoint: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)

    model_config = {"extra": "forbid"}
