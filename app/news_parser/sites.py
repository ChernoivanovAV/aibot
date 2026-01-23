from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import httpx
from bs4 import BeautifulSoup

from app.database import get_db, SessionLocal
from app.models import Source
from app.utils import sha256_hex


def parse_site_source(source: Source) -> list[dict]:
    if "habr.com" in source.url.lower():
        return parse_habr_rss(source)
    # TODO: add RBC/VC/Tproger parsers
    return []


def parse_habr_rss(source: Source) -> list[dict]:
    feed_url = source.url
    items: list[dict] = []

    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        r = client.get(feed_url)
        r.raise_for_status()
        xml = r.text

    soup = BeautifulSoup(xml, "xml")
    for it in soup.find_all("item")[:30]:
        title = (it.title.text or "").strip()
        link = (it.link.text or "").strip() or None
        desc = (it.description.text or "").strip()
        pub = (it.pubDate.text or "").strip()

        published_at = datetime.now(tz=timezone.utc)
        if pub:
            try:
                dt = parsedate_to_datetime(pub)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                published_at = dt.astimezone(timezone.utc)
            except Exception:
                pass

        summary = strip_html(desc)[:5000] if desc else title

        fp_base = link or f"{title}|{source.name}|{published_at.isoformat()}"
        fingerprint = sha256_hex(fp_base)

        items.append({
            "title": title[:512] or "(no title)",
            "url": (link[:1024] if link else None),
            "summary": summary if summary else title,
            "source": source.name,
            "published_at": published_at.replace(tzinfo=None),  # store naive UTC
            "raw_text": None,
            "fingerprint": fingerprint,
        })

    return items


def strip_html(html: str) -> str:
    s = BeautifulSoup(html, "lxml")
    return s.get_text(" ", strip=True)


if __name__ == "__main__":
    db = SessionLocal()
    print("DB URL:", db.bind.url)

    # 🔥 включить echo
    db.bind.echo = True

    try:
        source = db.get(Source, 1)
        print(vars(source))
        news = parse_habr_rss(source)
        print(news)


    finally:
        db.close()
    # news = parse_habr_rss()
    # print(news)
