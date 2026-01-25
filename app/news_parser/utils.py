from bs4 import BeautifulSoup
from datetime import datetime, timezone


def get_full_url(link_tag, base_url: str) -> str | None:
    """
    Возвращает полный URL из тега <a>.
    Если ссылка относительная — достраивает её.
    """
    if link_tag is None:
        return None
    href = link_tag.get('href')
    if not href:
        return None
    if href.startswith(('http://', 'https://')):
        return href
    return f'{base_url}{href}'


def strip_html(html: str) -> str:
    s = BeautifulSoup(html, "html.parser")
    return s.get_text(strip=True)


def parse_date(pub: str):
    if not pub:
        return datetime.now()
    try:
        if pub.endswith('Z'):
            pub = pub.replace('Z', '+00:00')
        dt = datetime.fromisoformat(pub)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    except Exception:
        return datetime.now()
