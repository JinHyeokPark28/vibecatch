"""
Hacker News Collector

Fetches top stories from Hacker News using the official Firebase API.
API Documentation: https://github.com/HackerNews/API
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
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
HN_FETCH_COUNT = int(os.getenv("HN_FETCH_COUNT", "30"))
REQUEST_TIMEOUT = 10.0  # seconds


@dataclass
class HNItem(BaseItem):
    """Represents a Hacker News item."""
    source: str = "hn"


class HackerNewsCollector(BaseCollector):
    """Collector for Hacker News top stories."""

    source_name = "Hacker News"

    async def fetch_items(self, count: int = HN_FETCH_COUNT) -> list[HNItem]:
        """Fetch top stories from Hacker News."""
        return await fetch_top_stories(count)


async def fetch_top_story_ids(client: httpx.AsyncClient) -> list[int]:
    """Fetch top story IDs from HN API."""
    try:
        response = await client.get(
            f"{HN_API_BASE}/topstories.json",
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch top stories: {e}")
        return []


async def fetch_item_detail(client: httpx.AsyncClient, item_id: int) -> Optional[HNItem]:
    """Fetch detail for a single HN item."""
    try:
        response = await client.get(
            f"{HN_API_BASE}/item/{item_id}.json",
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        if not data or data.get("type") != "story":
            return None

        return HNItem(
            external_id=str(item_id),
            title=data.get("title", ""),
            url=data.get("url"),  # May be None for Ask HN, Show HN posts
        )
    except httpx.HTTPError as e:
        logger.warning(f"Failed to fetch item {item_id}: {e}")
        return None


async def fetch_top_stories(count: int = HN_FETCH_COUNT) -> list[HNItem]:
    """
    Fetch top stories from Hacker News.

    Args:
        count: Number of top stories to fetch (default: 30)

    Returns:
        List of HNItem objects
    """
    logger.info(f"Fetching top {count} stories from Hacker News...")

    async with httpx.AsyncClient() as client:
        # Get top story IDs
        story_ids = await fetch_top_story_ids(client)

        if not story_ids:
            logger.warning("No story IDs returned from HN API")
            return []

        # Limit to requested count
        story_ids = story_ids[:count]

        # Fetch items in parallel (with semaphore to avoid overwhelming the API)
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests

        async def fetch_with_semaphore(item_id: int) -> Optional[HNItem]:
            async with semaphore:
                return await fetch_item_detail(client, item_id)

        tasks = [fetch_with_semaphore(sid) for sid in story_ids]
        results = await asyncio.gather(*tasks)

        # Filter out None results
        items = [item for item in results if item is not None]

        logger.info(f"Successfully fetched {len(items)} items from Hacker News")
        return items


async def collect_and_save(count: int = HN_FETCH_COUNT) -> dict:
    """
    Fetch top stories and save to database.

    Args:
        count: Number of stories to fetch

    Returns:
        Dict with collection results (for backward compatibility)
    """
    collector = HackerNewsCollector()
    result = await collector.collect_and_save(count)

    return {
        "fetched": result.fetched,
        "inserted": result.inserted,
        "skipped": result.skipped,
    }


if __name__ == "__main__":
    # Test the collector
    logging.basicConfig(level=logging.INFO)

    async def main():
        print("Testing fetch_top_stories...")
        items = await fetch_top_stories(5)
        for item in items:
            print(f"[{item.external_id}] {item.title}")

        print("\nTesting collect_and_save...")
        result = await collect_and_save(5)
        print(f"Result: {result}")

    asyncio.run(main())
