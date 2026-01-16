"""
Tests for main.py routes.
"""

import os
import pytest
from fastapi.testclient import TestClient

# Set test database before importing main
os.environ["DATABASE_PATH"] = ":memory:"

from main import app, calculate_priority
from database import init_db, save_items, update_item_summary, review_item


@pytest.fixture
def client():
    """Create test client with fresh database."""
    init_db()
    return TestClient(app)


@pytest.fixture
def client_with_items():
    """Create test client with sample items."""
    init_db()

    # Add sample items
    items = [
        {
            "source": "hn",
            "external_id": "test1",
            "title": "Test AI Tool for Developers",
            "url": "https://example.com/1",
        },
        {
            "source": "hn",
            "external_id": "test2",
            "title": "Show HN: My Vibe Coding Project",
            "url": "https://example.com/2",
        },
        {
            "source": "reddit",
            "external_id": "test3",
            "title": "Best SaaS Tools 2026",
            "url": "https://example.com/3",
        },
    ]
    save_items(items)

    return TestClient(app)


class TestHealthCheck:
    """Tests for /health endpoint."""

    def test_health_check(self, client):
        """Test health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "vibecatch"


class TestIndexRoute:
    """Tests for GET / endpoint."""

    def test_index_empty(self, client):
        """Test index with no items shows empty state."""
        response = client.get("/")
        assert response.status_code == 200
        assert "리뷰할 항목이 없습니다" in response.text
        assert "0개 리뷰 대기" in response.text

    def test_index_with_items(self, client_with_items):
        """Test index shows items."""
        response = client_with_items.get("/")
        assert response.status_code == 200
        assert "3개 리뷰 대기" in response.text
        assert "Test AI Tool for Developers" in response.text
        assert "Show HN: My Vibe Coding Project" in response.text
        assert "Best SaaS Tools 2026" in response.text

    def test_index_shows_source_badges(self, client_with_items):
        """Test index shows source badges."""
        response = client_with_items.get("/")
        assert response.status_code == 200
        assert "source-hn" in response.text
        assert "source-reddit" in response.text

    def test_index_has_action_buttons(self, client_with_items):
        """Test index has Like and Skip buttons."""
        response = client_with_items.get("/")
        assert response.status_code == 200
        assert "btn-like" in response.text
        assert "btn-skip" in response.text
        assert "좋아요" in response.text
        assert "건너뛰기" in response.text


class TestCollectRoute:
    """Tests for POST /collect endpoint."""

    def test_collect_returns_result(self, client):
        """Test collect returns structured result."""
        response = client.post("/collect")
        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "collected" in data
        assert "summarized" in data
        assert "fetched" in data["collected"]
        assert "inserted" in data["collected"]
        assert "skipped" in data["collected"]


class TestReviewRoute:
    """Tests for POST /review/{id} endpoint."""

    def test_review_like_success(self, client_with_items):
        """Test successful like action."""
        response = client_with_items.post(
            "/review/1",
            json={"action": "like"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["action"] == "like"

    def test_review_skip_success(self, client_with_items):
        """Test successful skip action."""
        response = client_with_items.post(
            "/review/2",
            json={"action": "skip"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["action"] == "skip"

    def test_review_invalid_action(self, client_with_items):
        """Test invalid action returns error."""
        response = client_with_items.post(
            "/review/1",
            json={"action": "invalid"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Invalid action" in data["error"]

    def test_review_nonexistent_item(self, client):
        """Test review of non-existent item."""
        response = client.post(
            "/review/999",
            json={"action": "like"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False


class TestPrioritySort:
    """Tests for F005 priority sorting."""

    def test_calculate_priority_with_preferences(self):
        """Test priority calculation with preferences."""
        preferences = {"ai": 3, "startup": 2, "llm": 1}
        item = {"tags": ["ai", "startup"]}

        priority = calculate_priority(item, preferences)
        assert priority == 5  # 3 + 2

    def test_calculate_priority_no_matching_tags(self):
        """Test priority calculation with no matching tags."""
        preferences = {"ai": 3}
        item = {"tags": ["web", "mobile"]}

        priority = calculate_priority(item, preferences)
        assert priority == 0

    def test_calculate_priority_empty_tags(self):
        """Test priority calculation with empty tags."""
        preferences = {"ai": 3}
        item = {"tags": []}

        priority = calculate_priority(item, preferences)
        assert priority == 0

    def test_items_sorted_by_preference(self):
        """Test that items are sorted by preference score."""
        init_db()

        # Create items with different tags
        save_items([
            {"source": "hn", "external_id": "low", "title": "Low Priority", "url": "https://test.com/1"},
            {"source": "hn", "external_id": "high", "title": "High Priority", "url": "https://test.com/2"},
        ])

        # Add tags
        update_item_summary(1, "낮은 우선순위", "Low summary", ["web"])
        update_item_summary(2, "높은 우선순위", "High summary", ["ai"])

        # Like an item with 'ai' tag to boost ai preference
        review_item(2, "like")

        # Restore item to 'new' status for testing
        import database
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE items SET status = 'new'")

        # Get items - should be sorted by preference
        client = TestClient(app)
        response = client.get("/")

        # High priority item (with ai tag) should come first
        assert response.text.index("높은 우선순위") < response.text.index("낮은 우선순위")
