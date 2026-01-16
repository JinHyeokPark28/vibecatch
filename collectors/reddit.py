"""
Reddit Collector

Fetches hot posts from programming-related subreddits using Reddit's JSON API.
No authentication required for public subreddits.
"""

import asyncio
import logging
import os
from dataclasses import dataclass
import httpx

from collectors.base import BaseCollector, BaseItem

logger = logging.getLogger(__name__)

# Configuration
REDDIT_FETCH_COUNT = int(os.getenv("REDDIT_FETCH_COUNT", "20"))
REQUEST_TIMEOUT = 10.0  # seconds

# Subreddits relevant to vibe coders
SUBREDDITS = [
    "programming",
    "webdev",
    "SideProject",
    "indiehackers",
    "MachineLearning",
]

# User-Agent required by Reddit API
USER_AGENT = "VibeCatch/1.0 (Trend Collector for Vibe Coders)"


@dataclass
class RedditItem(BaseItem):
    """Represents a Reddit post."""
    subreddit: str = ""
    source: str = "reddit"


class RedditCollector(BaseCollector):
    """Collector for Reddit hot posts."""

    source_name = "Reddit"

    async def fetch_items(self, count: int = REDDIT_FETCH_COUNT) -> list[RedditItem]:
        """Fetch hot posts from Reddit."""
        return await fetch_hot_posts(count)


async def fetch_subreddit_posts(
    client: httpx.AsyncClient,
    subreddit: str,
    limit: int = 10
) -> list[RedditItem]:
    """Fetch hot posts from a subreddit."""
    try:
        response = await client.get(
            f"https://www.reddit.com/r/{subreddit}/hot.json",
            params={"limit": limit},
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
        )
        response.raise_for_status()
        data = response.json()

        items = []
        for post in data.get("data", {}).get("children", []):
            post_data = post.get("data", {})

            # Skip stickied/pinned posts
            if post_data.get("stickied"):
                continue

            # Get the actual URL (external link or reddit post)
            url = post_data.get("url")
            if url and url.startswith("/r/"):
                url = f"https://www.reddit.com{url}"

            items.append(RedditItem(
                external_id=post_data.get("id", ""),
                title=post_data.get("title", ""),
                url=url,
                subreddit=subreddit,
            ))

        return items

    except httpx.HTTPError as e:
        logger.warning(f"Failed to fetch r/{subreddit}: {e}")
        return []


async def fetch_hot_posts(count: int = REDDIT_FETCH_COUNT) -> list[RedditItem]:
    """
    Fetch hot posts from multiple subreddits.

    Args:
        count: Total number of posts to fetch (distributed across subreddits)

    Returns:
        List of RedditItem objects
    """
    logger.info(f"Fetching up to {count} posts from Reddit...")

    # Calculate posts per subreddit
    per_subreddit = max(5, count // len(SUBREDDITS))

    async with httpx.AsyncClient() as client:
        # Fetch from all subreddits in parallel
        tasks = [
            fetch_subreddit_posts(client, sub, per_subreddit)
            for sub in SUBREDDITS
        ]
        results = await asyncio.gather(*tasks)

        # Flatten results
        all_items = []
        for items in results:
            all_items.extend(items)

        # Limit to requested count
        all_items = all_items[:count]

        logger.info(f"Successfully fetched {len(all_items)} items from Reddit")
        return all_items


async def collect_and_save(count: int = REDDIT_FETCH_COUNT) -> dict:
    """
    Fetch hot posts and save to database.

    Args:
        count: Number of posts to fetch

    Returns:
        Dict with collection results (for backward compatibility)
    """
    collector = RedditCollector()
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
        print("Testing fetch_hot_posts...")
        items = await fetch_hot_posts(10)
        for item in items:
            print(f"[r/{item.subreddit}] {item.title[:60]}...")

        print("\nTesting collect_and_save...")
        result = await collect_and_save(10)
        print(f"Result: {result}")

    asyncio.run(main())
