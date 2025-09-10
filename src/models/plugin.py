from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Plugin(BaseModel):
    name: str = Field(...)
    module: str = Field(...)
    config: Optional[Dict[str, Any]] = None

    model_config = {"extra": "forbid"}
