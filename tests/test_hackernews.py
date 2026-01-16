"""
Tests for Hacker News collector.

Test cases:
- HNItem: Dataclass conversion
- save_items: New item insertion
- save_items: Duplicate item skipping
- Integration: fetch_top_stories (requires network)
"""

import os
import tempfile

import pytest

import database  # noqa: E402
from collectors.hackernews import HNItem, fetch_top_stories  # noqa: E402
from database import init_db, save_items  # noqa: E402


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test."""
    # Create new temp file for this test
    test_db_path = tempfile.mktemp(suffix=".db")
    database.DATABASE_PATH = test_db_path

    # Initialize tables
    init_db()

    yield test_db_path

    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


class TestHNItem:
    """Tests for HNItem dataclass."""

    def test_to_dict(self):
        """Test HNItem.to_dict() conversion."""
        item = HNItem(
            external_id="12345",
            title="Test Title",
            url="https://example.com"
        )
        result = item.to_dict()

        assert result["source"] == "hn"
        assert result["external_id"] == "12345"
        assert result["title"] == "Test Title"
        assert result["url"] == "https://example.com"

    def test_to_dict_without_url(self):
        """Test HNItem.to_dict() with None URL."""
        item = HNItem(
            external_id="12345",
            title="Ask HN: Something",
            url=None
        )
        result = item.to_dict()

        assert result["source"] == "hn"
        assert result["url"] is None


class TestSaveItems:
    """Tests for save_items function."""

    def test_save_items_new(self, test_db):
        """Test saving new items."""
        items = [
            {"source": "hn", "external_id": "001", "title": "Test 1", "url": "https://test.com/1"},
            {"source": "hn", "external_id": "002", "title": "Test 2", "url": "https://test.com/2"},
        ]

        result = save_items(items)

        assert result.total == 2
        assert result.inserted == 2
        assert result.skipped == 0

    def test_save_items_duplicate(self, test_db):
        """Test duplicate item handling."""
        items = [
            {"source": "hn", "external_id": "dup001", "title": "Test 1", "url": "https://test.com/1"},
        ]

        # First save
        result1 = save_items(items)
        assert result1.inserted == 1

        # Second save (should skip)
        result2 = save_items(items)
        assert result2.inserted == 0
        assert result2.skipped == 1

    def test_save_items_empty(self, test_db):
        """Test saving empty list."""
        result = save_items([])

        assert result.total == 0
        assert result.inserted == 0
        assert result.skipped == 0

    def test_save_items_mixed(self, test_db):
        """Test saving mix of new and duplicate items."""
        # Save first item
        save_items([
            {"source": "hn", "external_id": "mix001", "title": "Test 1", "url": "https://test.com/1"},
        ])

        # Save mix of new and existing
        items = [
            {"source": "hn", "external_id": "mix001", "title": "Test 1", "url": "https://test.com/1"},  # Duplicate
            {"source": "hn", "external_id": "mix002", "title": "Test 2", "url": "https://test.com/2"},  # New
        ]

        result = save_items(items)

        assert result.total == 2
        assert result.inserted == 1
        assert result.skipped == 1


class TestFetchTopStories:
    """Integration tests for fetch_top_stories (requires network)."""

    @pytest.mark.asyncio
    async def test_fetch_top_stories_integration(self):
        """Test actual fetch from HN API (integration test)."""
        items = await fetch_top_stories(3)

        # Should get some items (may vary based on API availability)
        assert isinstance(items, list)

        # If we got items, verify structure
        if len(items) > 0:
            assert hasattr(items[0], "external_id")
            assert hasattr(items[0], "title")
            assert items[0].source == "hn"
