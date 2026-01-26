from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal


class SourceCreate(BaseModel):
    type: Literal["site", "tg"]
    name: str
    url: str
    enabled: bool = True


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    enabled: Optional[bool] = None


class SourceOut(BaseModel):
    id: int
    type: str
    name: str
    url: str
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class KeywordCreate(BaseModel):
    word: str = Field(min_length=1, max_length=128)


class KeywordOut(BaseModel):
    id: int
    word: str

    class Config:
        from_attributes = True


class NewsOut(BaseModel):
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
    id: int
    news_id: int
    generated_text: Optional[str]
    published_at: Optional[datetime]
    status: str
    error: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

