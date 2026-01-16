"""
Tests for database module.
"""

import json
import os
import tempfile

import pytest

import database
from database import (
    init_db,
    save_items,
    get_items_by_status,
    get_items_without_summary,
    update_item_summary,
)


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test."""
    test_db_path = tempfile.mktemp(suffix=".db")
    database.DATABASE_PATH = test_db_path

    init_db()

    yield test_db_path

    if os.path.exists(test_db_path):
        os.remove(test_db_path)


class TestGetItemsWithoutSummary:
    """Tests for get_items_without_summary function."""

    def test_returns_items_without_summary(self, test_db):
        """Test that only items without summary are returned."""
        # Insert items
        save_items([
            {"source": "hn", "external_id": "001", "title": "Test 1", "url": "https://test.com/1"},
            {"source": "hn", "external_id": "002", "title": "Test 2", "url": "https://test.com/2"},
        ])

        # Update one with summary
        update_item_summary(1, "Summary 1", ["ai"])

        # Get items without summary
        items = get_items_without_summary()

        assert len(items) == 1
        assert items[0]["external_id"] == "002"

    def test_respects_limit(self, test_db):
        """Test that limit parameter works."""
        save_items([
            {"source": "hn", "external_id": f"00{i}", "title": f"Test {i}", "url": f"https://test.com/{i}"}
            for i in range(5)
        ])

        items = get_items_without_summary(limit=2)

        assert len(items) == 2


class TestUpdateItemSummary:
    """Tests for update_item_summary function."""

    def test_update_success(self, test_db):
        """Test successful summary update."""
        save_items([
            {"source": "hn", "external_id": "001", "title": "Test 1", "url": "https://test.com/1"},
        ])

        result = update_item_summary(1, "This is a summary", ["ai", "startup"])

        assert result is True

        # Verify update
        items = get_items_by_status("new")
        assert len(items) == 1
        assert items[0]["summary"] == "This is a summary"
        assert json.loads(items[0]["tags"]) == ["ai", "startup"]

    def test_update_nonexistent_item(self, test_db):
        """Test update for non-existent item."""
        result = update_item_summary(999, "Summary", [])

        assert result is False

    def test_update_empty_tags(self, test_db):
        """Test update with empty tags."""
        save_items([
            {"source": "hn", "external_id": "001", "title": "Test 1", "url": "https://test.com/1"},
        ])

        result = update_item_summary(1, "Summary", [])

        assert result is True

        items = get_items_by_status("new")
        assert json.loads(items[0]["tags"]) == []
