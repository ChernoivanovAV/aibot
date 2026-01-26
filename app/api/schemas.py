"""Pydantic schemas for API payloads and responses."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class SourceCreate(BaseModel):
    """Payload for creating a new source."""

    type: Literal["site", "tg"]
    name: str
    url: str
    enabled: bool = True


class SourceUpdate(BaseModel):
    """Payload for updating an existing source."""

    name: Optional[str] = None
    url: Optional[str] = None
    enabled: Optional[bool] = None


class SourceOut(BaseModel):
    """Serialized source for API responses."""

    id: int
    type: str
    name: str
    url: str
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class KeywordCreate(BaseModel):
    """Payload for creating a keyword."""

    word: str = Field(min_length=1, max_length=128)


class KeywordOut(BaseModel):
    """Serialized keyword for API responses."""

    id: int
    word: str

    class Config:
        from_attributes = True


class NewsOut(BaseModel):
    """Serialized news item for API responses."""

    id: int
    title: str
    url: Optional[str]
    summary: str
    source: str
    published_at: datetime
    raw_text: Optional[str]
    fingerprint: str
    created_at: datetime

    class Config:
        from_attributes = True


class PostOut(BaseModel):
    """Serialized post for API responses."""

    id: int
    news_id: int
    generated_text: Optional[str]
    published_at: Optional[datetime]
    status: str
    error: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
