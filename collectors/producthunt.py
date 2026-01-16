"""
Product Hunt Collector

Fetches latest product launches from Product Hunt RSS feed.
No API key required.
"""

import asyncio
import logging
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional
import re

import httpx

from collectors.base import BaseCollector, BaseItem

logger = logging.getLogger(__name__)

# Configuration
PH_FETCH_COUNT = int(os.getenv("PH_FETCH_COUNT", "20"))
REQUEST_TIMEOUT = 15.0

# Product Hunt RSS feed
PH_RSS_URL = "https://www.producthunt.com/feed"


@dataclass
class ProductHuntItem(BaseItem):
    """Represents a Product Hunt launch."""
    tagline: Optional[str] = None
    source: str = "producthunt"

    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion."""
        # Include tagline in title for better context
        title = self.title
        if self.tagline:
            title = f"{self.title} - {self.tagline}"

        return {
            "source": self.source,
            "external_id": self.external_id,
            "title": title,
            "url": self.url,
        }


class ProductHuntCollector(BaseCollector):
    """Collector for Product Hunt launches."""

    source_name = "Product Hunt"

    async def fetch_items(self, count: int = PH_FETCH_COUNT) -> list[ProductHuntItem]:
        """Fetch latest launches from Product Hunt."""
        return await fetch_producthunt_launches(count)


def extract_id_from_url(url: str) -> str:
    """Extract product ID/slug from Product Hunt URL."""
    # URL format: https://www.producthunt.com/posts/product-name
    match = re.search(r'/posts/([^/?]+)', url)
    if match:
        return match.group(1)
    return url


async def fetch_producthunt_launches(count: int = PH_FETCH_COUNT) -> list[ProductHuntItem]:
    """
    Fetch latest launches from Product Hunt Atom feed.

    Args:
        count: Number of items to fetch

    Returns:
        List of ProductHuntItem objects
    """
    logger.info(f"Fetching up to {count} launches from Product Hunt...")

    # Atom namespace
    ATOM_NS = {'atom': 'http://www.w3.org/2005/Atom'}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                PH_RSS_URL,
                timeout=REQUEST_TIMEOUT,
                follow_redirects=True,
            )
            response.raise_for_status()

            # Parse Atom XML
            root = ET.fromstring(response.text)

            items: list[ProductHuntItem] = []

            # Find all entries in Atom feed (with namespace)
            entries = root.findall('atom:entry', ATOM_NS)
            if not entries:
                # Try without namespace (fallback)
                entries = root.findall('.//entry')

            for entry in entries:
                if len(items) >= count:
                    break

                # Get title
                title_elem = entry.find('atom:title', ATOM_NS)
                if title_elem is None:
                    title_elem = entry.find('title')

                # Get link (href attribute)
                link_elem = entry.find('atom:link', ATOM_NS)
                if link_elem is None:
                    link_elem = entry.find('link')

                # Get content/description
                content_elem = entry.find('atom:content', ATOM_NS)
                if content_elem is None:
                    content_elem = entry.find('content')

                if title_elem is None or link_elem is None:
                    continue

                title = title_elem.text or ""
                url = link_elem.get('href', '')
                content = content_elem.text if content_elem is not None else None

                # Extract tagline from content (first paragraph)
                tagline = None
                if content:
                    # Clean HTML tags
                    clean_content = re.sub(r'<[^>]+>', '', content)
                    lines = [l.strip() for l in clean_content.strip().split('\n') if l.strip()]
                    if lines:
                        tagline = lines[0][:200]

                external_id = extract_id_from_url(url) or title[:50]

                items.append(ProductHuntItem(
                    external_id=external_id,
                    title=title,
                    url=url,
                    tagline=tagline,
                ))

            logger.info(f"Successfully fetched {len(items)} launches from Product Hunt")
            return items

        except httpx.HTTPError as e:
            logger.warning(f"Failed to fetch Product Hunt feed: {e}")
            return []
        except ET.ParseError as e:
            logger.warning(f"Failed to parse Product Hunt feed: {e}")
            return []


async def collect_and_save(count: int = PH_FETCH_COUNT) -> dict:
    """
    Fetch Product Hunt launches and save to database.

    Args:
        count: Number of items to fetch

    Returns:
        Dict with collection results
    """
    collector = ProductHuntCollector()
    result = await collector.collect_and_save(count)

    return {
        "fetched": result.fetched,
        "inserted": result.inserted,
        "skipped": result.skipped,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    async def main():
        print("Testing fetch_producthunt_launches...")
        items = await fetch_producthunt_launches(10)
        for item in items:
            print(f"🚀 {item.title}")
            if item.tagline:
                print(f"   → {item.tagline[:60]}")

    asyncio.run(main())
