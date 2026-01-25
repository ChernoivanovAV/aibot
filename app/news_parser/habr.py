import requests
from bs4 import BeautifulSoup
import logging
from app.news_parser.http_client import get
from app.news_parser.utils import get_full_url, parse_date
from app.utils import sha256_hex

BASE_URL = 'https://habr.com'
NEWS_URL = f'{BASE_URL}/ru/news/'
ARTICLE_URL = f'{BASE_URL}/ru/article/'

CARD_SELECTOR = 'article.tm-articles-list__item'
TITLE_SELECTOR = 'a'
TITLE_LINK_SELECTOR = 'tm-title__link'

DEFAULT_HEADERS = {
    'User-Agent': "Mozilla/5.0",
    'Accept': 'text/html',
}

logger = logging.getLogger(__name__)


def parser_list_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, 'html.parser')
    news_items: list[dict] = []

    article_tags = soup.select(CARD_SELECTOR)
    for article_tag in article_tags:

        title_link = article_tag.find(TITLE_SELECTOR, class_=TITLE_LINK_SELECTOR)

        link = get_full_url(title_link, BASE_URL)
        if link is None:
            continue

        logger.info(link)

        published_at = parse_date(article_tag.find("time").get('datetime', ''))
        text_row = article_tag.find("p")

        summary = text_row.get_text(strip=True)[:5000]
        title = title_link.get_text(strip=True)

        fp_base = link or f"{title}|habr|{published_at.isoformat()}"
        fingerprint = sha256_hex(fp_base)

        news_items.append({
            'title': title[:512] or '(no title)',
            'url': (link[:1024] if link else None),
            "summary": summary if summary else title,
            'source': 'habr',
            "published_at": published_at.replace(tzinfo=None),
            "raw_text": None,
            "fingerprint": fingerprint,
        })

    return news_items


def fetch_news_list() -> list[dict[str, str]]:
    raw_items: list[dict[str, str]] = []
    try:
        response = get(url=NEWS_URL, headers=DEFAULT_HEADERS)
    except requests.RequestException as exc:
        logger.warning(f'При парсинге возникла ошибка {exc}')
        return raw_items

    if response.status_code != 200:
        logger.warning(f'При парсинге возник статус код {response.status_code}')
        return raw_items

    raw_items = parser_list_html(response.text)
    return raw_items


if __name__ == '__main__':

    news = fetch_news_list()
    for news_item in news:
        print(f"""{news_item.get('title')}
{news_item.get('url')}
{news_item.get('summary')}
{news_item.get('source')}
{news_item.get('published_at')}
{news_item.get('raw_text')}
{news_item.get('fingerprint')}
""")
