"""
TLDR.tech Collector

Fetches tech news from TLDR newsletter RSS feed.
RSS feeds available for different topics.
"""

import asyncio
import logging
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional
import re
import hashlib

import httpx

from collectors.base import BaseCollector, BaseItem

logger = logging.getLogger(__name__)

# Configuration
TLDR_FETCH_COUNT = int(os.getenv("TLDR_FETCH_COUNT", "15"))
REQUEST_TIMEOUT = 15.0

# TLDR RSS feeds
TLDR_FEEDS = {
    "tech": "https://tldr.tech/api/rss/tech",
    "ai": "https://tldr.tech/api/rss/ai",
    "webdev": "https://tldr.tech/api/rss/webdev",
}


@dataclass
class TLDRItem(BaseItem):
    """Represents a TLDR news item."""
    category: Optional[str] = None
    source: str = "tldr"

    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion."""
        return {
            "source": self.source,
            "external_id": self.external_id,
            "title": self.title,
            "url": self.url,
        }


class TLDRCollector(BaseCollector):
    """Collector for TLDR newsletter."""

    source_name = "TLDR"

    async def fetch_items(self, count: int = TLDR_FETCH_COUNT) -> list[TLDRItem]:
        """Fetch news from TLDR."""
        return await fetch_tldr_news(count)


def generate_id(title: str, url: str) -> str:
    """Generate unique ID from title and URL."""
    content = f"{title}:{url}"
    return hashlib.md5(content.encode()).hexdigest()[:16]


async def fetch_feed(client: httpx.AsyncClient, feed_url: str, category: str, limit: int) -> list[TLDRItem]:
    """Fetch items from a single RSS feed."""
    try:
        response = await client.get(
            feed_url,
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
        )
        response.raise_for_status()

        root = ET.fromstring(response.text)
        items: list[TLDRItem] = []

        for item in root.findall('.//item'):
            if len(items) >= limit:
                break

            title_elem = item.find('title')
            link_elem = item.find('link')

            if title_elem is None or link_elem is None:
                continue

            title = title_elem.text or ""
            url = link_elem.text or ""

            if not title or not url:
                continue

            external_id = generate_id(title, url)

            items.append(TLDRItem(
                external_id=external_id,
                title=title,
                url=url,
                category=category,
            ))

        return items

    except (httpx.HTTPError, ET.ParseError) as e:
        logger.warning(f"Failed to fetch TLDR {category} feed: {e}")
        return []


async def fetch_tldr_news(count: int = TLDR_FETCH_COUNT) -> list[TLDRItem]:
    """
    Fetch news from TLDR RSS feeds.

    Args:
        count: Total number of items to fetch

    Returns:
        List of TLDRItem objects
    """
    logger.info(f"Fetching up to {count} items from TLDR...")

    async with httpx.AsyncClient() as client:
        all_items: list[TLDRItem] = []
        seen_ids: set[str] = set()

        # Fetch from each feed
        per_feed = max(5, count // len(TLDR_FEEDS))

        for category, feed_url in TLDR_FEEDS.items():
            if len(all_items) >= count:
                break

            feed_items = await fetch_feed(client, feed_url, category, per_feed)

            for item in feed_items:
                if item.external_id not in seen_ids:
                    all_items.append(item)
                    seen_ids.add(item.external_id)

                    if len(all_items) >= count:
                        break

            # Small delay between feeds
            await asyncio.sleep(0.2)

        logger.info(f"Successfully fetched {len(all_items)} items from TLDR")
        return all_items[:count]


async def collect_and_save(count: int = TLDR_FETCH_COUNT) -> dict:
    """
    Fetch TLDR news and save to database.

    Args:
        count: Number of items to fetch

    Returns:
        Dict with collection results
    """
    collector = TLDRCollector()
    result = await collector.collect_and_save(count)

    return {
        "fetched": result.fetched,
        "inserted": result.inserted,
        "skipped": result.skipped,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    async def main():
        print("Testing fetch_tldr_news...")
        items = await fetch_tldr_news(15)
        for item in items:
            print(f"[{item.category}] {item.title[:60]}")

    asyncio.run(main())
