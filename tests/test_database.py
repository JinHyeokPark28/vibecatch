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
    # v2.0: User-specific functions
    get_or_create_user,
    get_user,
    sync_items_for_user,
    get_user_items,
    get_user_preferences,
    review_item_for_user,
    check_rate_limit,
    increment_rate_limit,
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
        update_item_summary(1, "테스트 1", "Summary 1", ["ai"])

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

        result = update_item_summary(1, "테스트 제목", "This is a summary", ["ai", "startup"])

        assert result is True

        # Verify update
        items = get_items_by_status("new")
        assert len(items) == 1
        assert items[0]["title_ko"] == "테스트 제목"
        assert items[0]["summary"] == "This is a summary"
        assert json.loads(items[0]["tags"]) == ["ai", "startup"]

    def test_update_nonexistent_item(self, test_db):
        """Test update for non-existent item."""
        result = update_item_summary(999, "제목", "Summary", [])

        assert result is False

    def test_update_empty_tags(self, test_db):
        """Test update with empty tags."""
        save_items([
            {"source": "hn", "external_id": "001", "title": "Test 1", "url": "https://test.com/1"},
        ])

        result = update_item_summary(1, "테스트", "Summary", [])

        assert result is True

        items = get_items_by_status("new")
        assert json.loads(items[0]["tags"]) == []


# ============================================================
# v2.0: User-specific tests
# ============================================================


class TestUserManagement:
    """Tests for v2.0 user management functions."""

    def test_create_new_user(self, test_db):
        """Test creating a new user with None UUID."""
        user_uuid = get_or_create_user(None)

        assert user_uuid is not None
        assert len(user_uuid) == 36  # UUID format

        # Verify user exists in DB
        user = get_user(user_uuid)
        assert user is not None
        assert user["tier"] == "free"

    def test_create_user_with_provided_uuid(self, test_db):
        """Test creating a user with a specific UUID."""
        specific_uuid = "test-user-12345678"
        user_uuid = get_or_create_user(specific_uuid)

        assert user_uuid == specific_uuid

        user = get_user(user_uuid)
        assert user is not None

    def test_get_existing_user(self, test_db):
        """Test getting an existing user updates last_seen_at."""
        user_uuid = get_or_create_user(None)

        # Call again - should return same UUID
        returned_uuid = get_or_create_user(user_uuid)

        assert returned_uuid == user_uuid

    def test_get_nonexistent_user(self, test_db):
        """Test getting a non-existent user."""
        user = get_user("nonexistent-uuid")
        assert user is None


class TestSyncItemsForUser:
    """Tests for v2.0 item syncing."""

    def test_sync_new_items(self, test_db):
        """Test syncing new items creates user_items records."""
        user_uuid = get_or_create_user(None)

        # Add items to global items table
        save_items([
            {"source": "hn", "external_id": "001", "title": "Test 1", "url": "https://test.com/1"},
            {"source": "hn", "external_id": "002", "title": "Test 2", "url": "https://test.com/2"},
        ])

        # Sync for user
        synced = sync_items_for_user(user_uuid)

        assert synced == 2

        # Verify user can see items
        user_items = get_user_items(user_uuid, status="new")
        assert len(user_items) == 2

    def test_sync_doesnt_duplicate(self, test_db):
        """Test syncing doesn't create duplicate user_items."""
        user_uuid = get_or_create_user(None)

        save_items([
            {"source": "hn", "external_id": "001", "title": "Test 1", "url": "https://test.com/1"},
        ])

        # Sync twice
        sync_items_for_user(user_uuid)
        synced = sync_items_for_user(user_uuid)

        assert synced == 0  # No new items to sync


class TestUserItems:
    """Tests for v2.0 user-specific item retrieval."""

    def test_get_user_items_by_status(self, test_db):
        """Test getting user items filtered by status."""
        user_uuid = get_or_create_user(None)

        save_items([
            {"source": "hn", "external_id": "001", "title": "Test 1", "url": "https://test.com/1"},
            {"source": "hn", "external_id": "002", "title": "Test 2", "url": "https://test.com/2"},
        ])
        sync_items_for_user(user_uuid)

        # All items should be "new"
        new_items = get_user_items(user_uuid, status="new")
        assert len(new_items) == 2

        liked_items = get_user_items(user_uuid, status="liked")
        assert len(liked_items) == 0

    def test_user_items_isolation(self, test_db):
        """Test that different users have isolated items."""
        user1 = get_or_create_user("user-1")
        user2 = get_or_create_user("user-2")

        save_items([
            {"source": "hn", "external_id": "001", "title": "Test 1", "url": "https://test.com/1"},
        ])

        # Sync for both users
        sync_items_for_user(user1)
        sync_items_for_user(user2)

        # Review as user1
        review_item_for_user(user1, 1, "like")

        # User1 should see it as liked, user2 should see it as new
        user1_liked = get_user_items(user1, status="liked")
        user2_new = get_user_items(user2, status="new")

        assert len(user1_liked) == 1
        assert len(user2_new) == 1


class TestReviewItemForUser:
    """Tests for v2.0 user-specific review."""

    def test_review_like_updates_preferences(self, test_db):
        """Test that liking an item updates user preferences."""
        user_uuid = get_or_create_user(None)

        save_items([
            {"source": "hn", "external_id": "001", "title": "Test 1", "url": "https://test.com/1"},
        ])
        # Update with tags
        update_item_summary(1, "테스트", "Summary", ["ai", "startup"])
        sync_items_for_user(user_uuid)

        # Like the item
        result = review_item_for_user(user_uuid, 1, "like")

        assert result is True

        # Check preferences
        prefs = get_user_preferences(user_uuid)
        assert prefs.get("ai", 0) == 1
        assert prefs.get("startup", 0) == 1

    def test_review_skip_updates_preferences(self, test_db):
        """Test that skipping an item decreases preference scores."""
        user_uuid = get_or_create_user(None)

        save_items([
            {"source": "hn", "external_id": "001", "title": "Test 1", "url": "https://test.com/1"},
        ])
        update_item_summary(1, "테스트", "Summary", ["ai"])
        sync_items_for_user(user_uuid)

        # Skip the item
        result = review_item_for_user(user_uuid, 1, "skip")

        assert result is True

        prefs = get_user_preferences(user_uuid)
        assert prefs.get("ai", 0) == -1

    def test_review_nonexistent_item(self, test_db):
        """Test reviewing a non-existent item."""
        user_uuid = get_or_create_user(None)

        result = review_item_for_user(user_uuid, 999, "like")

        assert result is False


class TestRateLimit:
    """Tests for v2.0 rate limiting."""

    def test_rate_limit_initial_state(self, test_db):
        """Test initial rate limit allows action."""
        user_uuid = get_or_create_user(None)

        allowed, remaining = check_rate_limit(user_uuid, "collect")

        assert allowed is True
        assert remaining == 3  # Free tier default

    def test_rate_limit_after_increment(self, test_db):
        """Test rate limit decreases after increment."""
        user_uuid = get_or_create_user(None)

        increment_rate_limit(user_uuid, "collect")
        allowed, remaining = check_rate_limit(user_uuid, "collect")

        assert allowed is True
        assert remaining == 2

    def test_rate_limit_exceeded(self, test_db):
        """Test rate limit blocks after exceeding limit."""
        user_uuid = get_or_create_user(None)

        # Use up all 3 collects
        for _ in range(3):
            increment_rate_limit(user_uuid, "collect")

        allowed, remaining = check_rate_limit(user_uuid, "collect")

        assert allowed is False
        assert remaining == 0


class TestUserPreferences:
    """Tests for v2.0 user preferences."""

    def test_empty_preferences(self, test_db):
        """Test getting preferences for user with no history."""
        user_uuid = get_or_create_user(None)

        prefs = get_user_preferences(user_uuid)

        assert prefs == {}

    def test_preferences_accumulate(self, test_db):
        """Test preferences accumulate across multiple reviews."""
        user_uuid = get_or_create_user(None)

        # Add and like multiple items with same tag
        for i in range(3):
            save_items([
                {"source": "hn", "external_id": f"00{i}", "title": f"Test {i}", "url": f"https://test.com/{i}"},
            ])
            update_item_summary(i + 1, f"테스트 {i}", "Summary", ["ai"])

        sync_items_for_user(user_uuid)

        # Like all items
        for i in range(1, 4):
            review_item_for_user(user_uuid, i, "like")

        prefs = get_user_preferences(user_uuid)
        assert prefs.get("ai", 0) == 3
