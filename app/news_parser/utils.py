"""Utility helpers for parsers."""

from datetime import datetime, timezone

from bs4 import BeautifulSoup


def get_full_url(link_tag, base_url: str) -> str | None:
    """Return a full URL from a link tag, resolving relative URLs."""
    if link_tag is None:
        return None
    href = link_tag.get("href")
    if not href:
        return None
    if href.startswith(("http://", "https://")):
        return href
    return f"{base_url}{href}"


def strip_html(html: str) -> str:
    """Strip HTML tags and return plain text."""
    s = BeautifulSoup(html, "html.parser")
    return s.get_text(strip=True)


def parse_date(pub: str) -> datetime:
    """Parse ISO-like timestamp into naive UTC datetime."""
    if not pub:
        return datetime.now()
    try:
        if pub.endswith("Z"):
            pub = pub.replace("Z", "+00:00")
        dt = datetime.fromisoformat(pub)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    except Exception:
        return datetime.now()
