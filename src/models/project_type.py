from pydantic import BaseModel, Field


class ProjectType(BaseModel):
    id: str = Field(..., description="Unique id for project type")
    name: str = Field(..., description="Human-readable name")
    description: str = Field("", description="Optional description")

    def json_schema(self) -> dict:
        return self.model_dump()
