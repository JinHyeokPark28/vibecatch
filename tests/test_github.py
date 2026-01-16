"""
Tests for GitHub collector.
"""

import os
import tempfile
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

import database
from database import init_db
from collectors.github import (
    GitHubItem,
    search_trending_repos,
    collect_and_save,
    TOPICS,
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


class TestGitHubItem:
    """Tests for GitHubItem dataclass."""

    def test_to_dict(self):
        """Test conversion to dict."""
        item = GitHubItem(
            external_id="12345",
            title="owner/repo",
            url="https://github.com/owner/repo",
            description="A cool project",
            stars=100,
            language="Python",
        )

        result = item.to_dict()

        assert result["source"] == "github"
        assert result["external_id"] == "12345"
        assert result["title"] == "owner/repo: A cool project"
        assert result["url"] == "https://github.com/owner/repo"

    def test_to_dict_without_description(self):
        """Test conversion without description."""
        item = GitHubItem(
            external_id="12345",
            title="owner/repo",
            url="https://github.com/owner/repo",
            description=None,
            stars=100,
            language="Python",
        )

        result = item.to_dict()

        assert result["title"] == "owner/repo"

    def test_to_dict_long_description_truncated(self):
        """Test that long descriptions are truncated."""
        long_desc = "A" * 200
        item = GitHubItem(
            external_id="12345",
            title="owner/repo",
            url="https://github.com/owner/repo",
            description=long_desc,
            stars=100,
            language="Python",
        )

        result = item.to_dict()

        # Title should be truncated: "owner/repo: " + 100 chars
        assert len(result["title"]) <= 112  # "owner/repo: " (12) + 100


class TestSearchTrendingRepos:
    """Tests for search_trending_repos function."""

    @pytest.mark.asyncio
    async def test_search_success(self):
        """Test successful search from GitHub."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": 12345,
                    "full_name": "owner/repo1",
                    "html_url": "https://github.com/owner/repo1",
                    "description": "Cool repo",
                    "stargazers_count": 500,
                    "language": "Python",
                },
                {
                    "id": 67890,
                    "full_name": "owner/repo2",
                    "html_url": "https://github.com/owner/repo2",
                    "description": "Another repo",
                    "stargazers_count": 300,
                    "language": "JavaScript",
                },
            ]
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        items = await search_trending_repos(mock_client, limit=10)

        assert len(items) == 2
        assert items[0].external_id == "12345"
        assert items[0].title == "owner/repo1"
        assert items[0].stars == 500
        assert items[1].title == "owner/repo2"

    @pytest.mark.asyncio
    async def test_search_with_topic(self):
        """Test search with topic filter."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        await search_trending_repos(mock_client, topic="ai", limit=5)

        # Verify topic was included in query
        call_args = mock_client.get.call_args
        params = call_args.kwargs.get("params", {})
        assert "topic:ai" in params.get("q", "")

    @pytest.mark.asyncio
    async def test_search_empty_response(self):
        """Test handling of empty response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        items = await search_trending_repos(mock_client, limit=10)

        assert len(items) == 0


class TestCollectAndSave:
    """Tests for collect_and_save function."""

    @pytest.mark.asyncio
    async def test_save_items(self, test_db):
        """Test saving GitHub items to database."""
        mock_items = [
            GitHubItem(
                external_id="12345",
                title="owner/repo",
                url="https://github.com/owner/repo",
                description="Cool project",
                stars=100,
                language="Python",
            ),
        ]

        with patch("collectors.github.fetch_trending_repos", return_value=mock_items):
            result = await collect_and_save(10)

            assert result["fetched"] == 1
            assert result["inserted"] == 1
            assert result["skipped"] == 0

    @pytest.mark.asyncio
    async def test_empty_fetch(self, test_db):
        """Test handling of empty fetch result."""
        with patch("collectors.github.fetch_trending_repos", return_value=[]):
            result = await collect_and_save(10)

            assert result["fetched"] == 0
            assert result["inserted"] == 0


class TestTopics:
    """Tests for topics configuration."""

    def test_topics_not_empty(self):
        """Test that TOPICS list is not empty."""
        assert len(TOPICS) > 0

    def test_topics_contains_ai(self):
        """Test that ai topic is included."""
        assert "ai" in TOPICS
