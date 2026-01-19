from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.database import get_db
from app.models import Source, Keyword, NewsItem, Post
from app.api.schemas import (
    SourceCreate, SourceUpdate, SourceOut,
    KeywordCreate, KeywordOut,
    NewsOut, PostOut,
    GenerateRequest, PublishRequest
)
from app.tasks import generate_post_task, publish_post_task, run_pipeline_task

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


# ---- Sources CRUD
@router.post("/sources/", response_model=SourceOut)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    src = Source(**payload.model_dump())
    db.add(src)
    db.commit()
    db.refresh(src)
    return src


@router.get("/sources/", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.execute(select(Source).order_by(desc(Source.id))).scalars().all()


@router.patch("/sources/{source_id}", response_model=SourceOut)
def update_source(source_id: int, payload: SourceUpdate, db: Session = Depends(get_db)):
    src = db.get(Source, source_id)
    if not src:
        raise HTTPException(404, "Source not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(src, k, v)

    db.commit()
    db.refresh(src)
    return src


@router.delete("/sources/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    src = db.get(Source, source_id)
    if not src:
        raise HTTPException(404, "Source not found")
    db.delete(src)
    db.commit()
    return {"deleted": True}


# ---- Keywords CRUD
@router.post("/keywords/", response_model=KeywordOut)
def create_keyword(payload: KeywordCreate, db: Session = Depends(get_db)):
    kw = Keyword(word=payload.word.strip())
    db.add(kw)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(400, "Keyword already exists or invalid")
    db.refresh(kw)
    return kw


@router.get("/keywords/", response_model=list[KeywordOut])
def list_keywords(db: Session = Depends(get_db)):
    return db.execute(select(Keyword).order_by(desc(Keyword.id))).scalars().all()


@router.delete("/keywords/{keyword_id}")
def delete_keyword(keyword_id: int, db: Session = Depends(get_db)):
    kw = db.get(Keyword, keyword_id)
    if not kw:
        raise HTTPException(404, "Keyword not found")
    db.delete(kw)
    db.commit()
    return {"deleted": True}


# ---- News / Posts
@router.get("/news/", response_model=list[NewsOut])
def list_news(limit: int = 50, db: Session = Depends(get_db)):
    return db.execute(select(NewsItem).order_by(desc(NewsItem.published_at)).limit(limit)).scalars().all()


@router.get("/posts/", response_model=list[PostOut])
def list_posts(limit: int = 50, db: Session = Depends(get_db)):
    return db.execute(select(Post).order_by(desc(Post.id)).limit(limit)).scalars().all()


# ---- Manual triggers (Celery)
@router.post("/pipeline/run")
def run_pipeline():
    task = run_pipeline_task.delay()
    return {"task_id": task.id}


@router.post("/generate/")
def generate_manual(payload: GenerateRequest):
    task = generate_post_task.delay(payload.news_id)
    return {"task_id": task.id}


@router.post("/publish/")
def publish_manual(payload: PublishRequest):
    task = publish_post_task.delay(payload.post_id)
    return {"task_id": task.id}
