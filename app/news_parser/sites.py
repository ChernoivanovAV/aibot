"""Routing for site-specific news parsers."""

from __future__ import annotations

from app.models import Source
from app.news_parser.habr import fetch_news_list as habr_news_list


def parse_site_source(source: Source) -> list[dict]:
    """Parse a site source into normalized news items."""
    if "habr.com" in source.url.lower():
        return habr_news_list()
    # TODO: add RBC/VC/Tproger parsers
    return []
