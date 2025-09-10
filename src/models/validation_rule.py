from typing import Any, Dict

from pydantic import BaseModel, Field


class ValidationRule(BaseModel):
    key: str = Field(...)
    rule: Dict[str, Any] = Field(...)

    model_config = {"extra": "allow"}
