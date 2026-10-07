from pydantic import BaseModel, Field


class AIQueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
