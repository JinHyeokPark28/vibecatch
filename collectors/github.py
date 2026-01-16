"""
GitHub Trending Collector

Fetches trending repositories from GitHub using the Search API.
Simulates trending by finding recently created repos with high star counts.

API Documentation: https://docs.github.com/en/rest/search/search
Rate Limit: 10 requests/minute (unauthenticated)
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Configuration
GITHUB_FETCH_COUNT = int(os.getenv("GITHUB_FETCH_COUNT", "20"))
REQUEST_TIMEOUT = 15.0  # seconds

# GitHub API base URL
GITHUB_API_BASE = "https://api.github.com"

# User-Agent required by GitHub API
USER_AGENT = "VibeCatch/1.0 (Trend Collector for Vibe Coders)"

# Topics relevant to vibe coders
TOPICS = ["ai", "llm", "machine-learning", "developer-tools", "saas", "cli"]


@dataclass
class GitHubItem:
    """Represents a GitHub repository."""
    external_id: str
    title: str
    url: Optional[str]
    description: Optional[str]
    stars: int
    language: Optional[str]
    source: str = "github"

    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion."""
        # Title format: "owner/repo - description"
        title = self.title
        if self.description:
            title = f"{self.title}: {self.description[:100]}"

        return {
            "source": self.source,
            "external_id": self.external_id,
            "title": title,
            "url": self.url,
        }


async def search_trending_repos(
    client: httpx.AsyncClient,
    topic: Optional[str] = None,
    days: int = 7,
    min_stars: int = 10,
    limit: int = 10
) -> list[GitHubItem]:
    """
    Search for trending repositories.

    Args:
        client: HTTP client
        topic: Optional topic to filter by
        days: Look back period in days
        min_stars: Minimum star count
        limit: Max results to return

    Returns:
        List of GitHubItem objects
    """
    # Calculate date threshold
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # Build query
    query_parts = [f"created:>{since_date}", f"stars:>{min_stars}"]
    if topic:
        query_parts.append(f"topic:{topic}")

    query = " ".join(query_parts)

    try:
        response = await client.get(
            f"{GITHUB_API_BASE}/search/repositories",
            params={
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": limit,
            },
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        items = []
        for repo in data.get("items", []):
            items.append(GitHubItem(
                external_id=str(repo.get("id", "")),
                title=repo.get("full_name", ""),
                url=repo.get("html_url"),
                description=repo.get("description"),
                stars=repo.get("stargazers_count", 0),
                language=repo.get("language"),
            ))

        return items

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            logger.warning("GitHub API rate limit exceeded")
        else:
            logger.warning(f"GitHub API error: {e}")
        return []
    except httpx.HTTPError as e:
        logger.warning(f"Failed to search GitHub: {e}")
        return []


async def fetch_trending_repos(count: int = GITHUB_FETCH_COUNT) -> list[GitHubItem]:
    """
    Fetch trending repositories from GitHub.

    Searches across multiple topics and general trending.

    Args:
        count: Total number of repos to fetch

    Returns:
        List of GitHubItem objects
    """
    logger.info(f"Fetching up to {count} trending repos from GitHub...")

    async with httpx.AsyncClient() as client:
        all_items: list[GitHubItem] = []
        seen_ids: set[str] = set()

        # First, get general trending (no topic filter)
        general_items = await search_trending_repos(
            client,
            topic=None,
            days=7,
            min_stars=50,
            limit=count // 2
        )

        for item in general_items:
            if item.external_id not in seen_ids:
                all_items.append(item)
                seen_ids.add(item.external_id)

        # Then search by topics
        per_topic = max(3, (count - len(all_items)) // len(TOPICS))

        # Rate limit: wait between requests
        for topic in TOPICS:
            if len(all_items) >= count:
                break

            await asyncio.sleep(0.5)  # Respect rate limits

            topic_items = await search_trending_repos(
                client,
                topic=topic,
                days=14,
                min_stars=10,
                limit=per_topic
            )

            for item in topic_items:
                if item.external_id not in seen_ids:
                    all_items.append(item)
                    seen_ids.add(item.external_id)

                    if len(all_items) >= count:
                        break

        # Sort by stars and limit
        all_items.sort(key=lambda x: x.stars, reverse=True)
        all_items = all_items[:count]

        logger.info(f"Successfully fetched {len(all_items)} items from GitHub")
        return all_items


async def collect_and_save(count: int = GITHUB_FETCH_COUNT) -> dict:
    """
    Fetch trending repos and save to database.

    Args:
        count: Number of repos to fetch

    Returns:
        Dict with collection results
    """
    from database import save_items

    # Fetch repos
    items = await fetch_trending_repos(count)

    if not items:
        logger.warning("No items fetched from GitHub")
        return {"fetched": 0, "inserted": 0, "skipped": 0}

    # Convert to dicts and save
    item_dicts = [item.to_dict() for item in items]
    result = save_items(item_dicts)

    return {
        "fetched": len(items),
        "inserted": result.inserted,
        "skipped": result.skipped,
    }


if __name__ == "__main__":
    # Test the collector
    logging.basicConfig(level=logging.INFO)

    async def main():
        print("Testing fetch_trending_repos...")
        items = await fetch_trending_repos(10)
        for item in items:
            print(f"[{item.stars}*] {item.title}")

        print("\nTesting collect_and_save...")
        result = await collect_and_save(10)
        print(f"Result: {result}")

    asyncio.run(main())
