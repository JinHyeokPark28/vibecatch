"""
Tests for Reddit collector.
"""

import os
import tempfile
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

import database
from database import init_db
from collectors.reddit import (
    RedditItem,
    fetch_subreddit_posts,
    collect_and_save,
    SUBREDDITS,
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


class TestRedditItem:
    """Tests for RedditItem dataclass."""

    def test_to_dict(self):
        """Test conversion to dict."""
        item = RedditItem(
            external_id="abc123",
            title="Test Post",
            url="https://example.com",
            subreddit="programming",
        )

        result = item.to_dict()

        assert result["source"] == "reddit"
        assert result["external_id"] == "abc123"
        assert result["title"] == "Test Post"
        assert result["url"] == "https://example.com"

    def test_to_dict_without_url(self):
        """Test conversion without URL."""
        item = RedditItem(
            external_id="abc123",
            title="Self Post",
            url=None,
            subreddit="programming",
        )

        result = item.to_dict()

        assert result["url"] is None


class TestFetchSubredditPosts:
    """Tests for fetch_subreddit_posts function."""

    @pytest.mark.asyncio
    async def test_fetch_success(self):
        """Test successful fetch from subreddit."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "children": [
                    {
                        "data": {
                            "id": "post1",
                            "title": "Test Post 1",
                            "url": "https://example.com/1",
                            "stickied": False,
                        }
                    },
                    {
                        "data": {
                            "id": "post2",
                            "title": "Test Post 2",
                            "url": "https://example.com/2",
                            "stickied": False,
                        }
                    },
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        items = await fetch_subreddit_posts(mock_client, "programming", 10)

        assert len(items) == 2
        assert items[0].external_id == "post1"
        assert items[1].title == "Test Post 2"

    @pytest.mark.asyncio
    async def test_skip_stickied_posts(self):
        """Test that stickied posts are skipped."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "children": [
                    {
                        "data": {
                            "id": "sticky",
                            "title": "Stickied Post",
                            "url": "https://example.com",
                            "stickied": True,
                        }
                    },
                    {
                        "data": {
                            "id": "normal",
                            "title": "Normal Post",
                            "url": "https://example.com",
                            "stickied": False,
                        }
                    },
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        items = await fetch_subreddit_posts(mock_client, "programming", 10)

        assert len(items) == 1
        assert items[0].external_id == "normal"


class TestCollectAndSave:
    """Tests for collect_and_save function."""

    @pytest.mark.asyncio
    async def test_save_items(self, test_db):
        """Test saving Reddit items to database."""
        mock_items = [
            RedditItem(
                external_id="r1",
                title="Reddit Post 1",
                url="https://reddit.com/1",
                subreddit="programming",
            ),
        ]

        with patch("collectors.reddit.fetch_hot_posts", return_value=mock_items):
            result = await collect_and_save(10)

            assert result["fetched"] == 1
            assert result["inserted"] == 1
            assert result["skipped"] == 0

    @pytest.mark.asyncio
    async def test_empty_fetch(self, test_db):
        """Test handling of empty fetch result."""
        with patch("collectors.reddit.fetch_hot_posts", return_value=[]):
            result = await collect_and_save(10)

            assert result["fetched"] == 0
            assert result["inserted"] == 0


class TestSubreddits:
    """Tests for subreddit configuration."""

    def test_subreddits_not_empty(self):
        """Test that SUBREDDITS list is not empty."""
        assert len(SUBREDDITS) > 0

    def test_subreddits_contains_programming(self):
        """Test that programming subreddit is included."""
        assert "programming" in SUBREDDITS
