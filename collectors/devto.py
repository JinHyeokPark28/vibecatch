"""
Dev.to Collector

Fetches trending/latest articles from Dev.to API.
API Documentation: https://developers.forem.com/api/v1

No authentication required for public endpoints.
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Optional

import httpx

from collectors.base import BaseCollector, BaseItem

logger = logging.getLogger(__name__)

# Configuration
DEVTO_FETCH_COUNT = int(os.getenv("DEVTO_FETCH_COUNT", "20"))
REQUEST_TIMEOUT = 15.0

# Dev.to API base URL
DEVTO_API_BASE = "https://dev.to/api"


@dataclass
class DevtoItem(BaseItem):
    """Represents a Dev.to article."""
    description: Optional[str] = None
    reactions: int = 0
    comments: int = 0
    source: str = "devto"

    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion."""
        return {
            "source": self.source,
            "external_id": self.external_id,
            "title": self.title,
            "url": self.url,
        }


class DevtoCollector(BaseCollector):
    """Collector for Dev.to articles."""

    source_name = "Dev.to"

    async def fetch_items(self, count: int = DEVTO_FETCH_COUNT) -> list[DevtoItem]:
        """Fetch trending articles from Dev.to."""
        return await fetch_devto_articles(count)


async def fetch_devto_articles(count: int = DEVTO_FETCH_COUNT) -> list[DevtoItem]:
    """
    Fetch trending/top articles from Dev.to.

    Args:
        count: Number of articles to fetch

    Returns:
        List of DevtoItem objects
    """
    logger.info(f"Fetching up to {count} articles from Dev.to...")

    async with httpx.AsyncClient() as client:
        all_items: list[DevtoItem] = []
        seen_ids: set[str] = set()

        # Fetch top articles (by reactions)
        try:
            response = await client.get(
                f"{DEVTO_API_BASE}/articles",
                params={
                    "per_page": min(count, 30),
                    "top": 7,  # Top from last 7 days
                },
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            articles = response.json()

            for article in articles:
                article_id = str(article.get("id", ""))
                if article_id and article_id not in seen_ids:
                    all_items.append(DevtoItem(
                        external_id=article_id,
                        title=article.get("title", ""),
                        url=article.get("url"),
                        description=article.get("description"),
                        reactions=article.get("public_reactions_count", 0),
                        comments=article.get("comments_count", 0),
                    ))
                    seen_ids.add(article_id)

        except httpx.HTTPError as e:
            logger.warning(f"Failed to fetch Dev.to top articles: {e}")

        # If we need more, fetch latest
        if len(all_items) < count:
            try:
                await asyncio.sleep(0.3)  # Rate limit respect
                response = await client.get(
                    f"{DEVTO_API_BASE}/articles",
                    params={
                        "per_page": count - len(all_items),
                        "tag": "programming",
                    },
                    timeout=REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                articles = response.json()

                for article in articles:
                    article_id = str(article.get("id", ""))
                    if article_id and article_id not in seen_ids:
                        all_items.append(DevtoItem(
                            external_id=article_id,
                            title=article.get("title", ""),
                            url=article.get("url"),
                            description=article.get("description"),
                            reactions=article.get("public_reactions_count", 0),
                            comments=article.get("comments_count", 0),
                        ))
                        seen_ids.add(article_id)

                        if len(all_items) >= count:
                            break

            except httpx.HTTPError as e:
                logger.warning(f"Failed to fetch Dev.to latest articles: {e}")

        # Sort by reactions
        all_items.sort(key=lambda x: x.reactions, reverse=True)
        all_items = all_items[:count]

        logger.info(f"Successfully fetched {len(all_items)} articles from Dev.to")
        return all_items


async def collect_and_save(count: int = DEVTO_FETCH_COUNT) -> dict:
    """
    Fetch Dev.to articles and save to database.

    Args:
        count: Number of articles to fetch

    Returns:
        Dict with collection results
    """
    collector = DevtoCollector()
    result = await collector.collect_and_save(count)

    return {
        "fetched": result.fetched,
        "inserted": result.inserted,
        "skipped": result.skipped,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    async def main():
        print("Testing fetch_devto_articles...")
        items = await fetch_devto_articles(10)
        for item in items:
            print(f"[{item.reactions}❤] {item.title[:60]}")

    asyncio.run(main())
