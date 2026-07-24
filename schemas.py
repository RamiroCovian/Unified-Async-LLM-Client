from pydantic import BaseModel, Field
from typing import Literal


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ModelParams(BaseModel):
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = 1024
    model: str | None = None
    stream: bool = False


class ModelResponse(BaseModel):
    content: str
    model: str
    provider: str
    finish_reason: str | None = None


class ErrorResponse(BaseModel):
    error: str
    error_type: str
