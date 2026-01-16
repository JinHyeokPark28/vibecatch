"""
Base Collector Module

Abstract base class for all collectors with common functionality.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class BaseItem:
    """Base class for collected items."""
    external_id: str
    title: str
    url: Optional[str]
    source: str

    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion."""
        return {
            "source": self.source,
            "external_id": self.external_id,
            "title": self.title,
            "url": self.url,
        }


@dataclass
class CollectResult:
    """Result of collection operation."""
    fetched: int
    inserted: int
    skipped: int


class BaseCollector(ABC):
    """Abstract base class for collectors."""

    source_name: str = "unknown"

    @abstractmethod
    async def fetch_items(self, count: int) -> list[BaseItem]:
        """
        Fetch items from the source.

        Args:
            count: Number of items to fetch

        Returns:
            List of BaseItem objects
        """
        pass

    async def collect_and_save(self, count: int) -> CollectResult:
        """
        Fetch items and save to database.

        Args:
            count: Number of items to fetch

        Returns:
            CollectResult with collection statistics
        """
        from database import save_items

        items = await self.fetch_items(count)

        if not items:
            logger.warning(f"No items fetched from {self.source_name}")
            return CollectResult(fetched=0, inserted=0, skipped=0)

        item_dicts = [item.to_dict() for item in items]
        result = save_items(item_dicts)

        return CollectResult(
            fetched=len(items),
            inserted=result.inserted,
            skipped=result.skipped,
        )
