import enum
from datetime import datetime
from sqlalchemy import (
    String, DateTime, Boolean, Enum, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class SourceType(str, enum.Enum):
    site = "site"
    tg = "tg"


class PostStatus(str, enum.Enum):
    new = "new"
    generated = "generated"
    published = "published"
    failed = "failed"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)  # site url or tg username/link
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    word: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)


class NewsItem(Base):
    __tablename__ = "news_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    source: Mapped[str] = mapped_column(String(255), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)  # sha256
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("fingerprint", name="uq_news_fingerprint"),
    )

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="news")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    news_id: Mapped[int] = mapped_column(
        ForeignKey("news_items.id"),
        nullable=False,
        unique=True,
    )

    generated_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    status: Mapped[PostStatus] = mapped_column(Enum(PostStatus), default=PostStatus.new, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    news: Mapped["NewsItem"] = relationship("NewsItem", back_populates="posts")
