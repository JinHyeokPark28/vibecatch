"""
Tests for summarizer module.

Uses mocks for Claude API to avoid actual API calls.
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

import database
import summarizer
from database import init_db, save_items
from summarizer import (
    SummaryResult,
    summarize_item,
    summarize_new_items,
    KNOWN_TAGS,
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


class TestSummarizeItem:
    """Tests for summarize_item function."""

    @pytest.mark.asyncio
    async def test_returns_none_without_api_key(self):
        """Test that None is returned when API key is not set."""
        with patch.object(summarizer, 'ANTHROPIC_API_KEY', None):
            result = await summarize_item("Test title", "https://example.com")
            assert result is None

    @pytest.mark.asyncio
    async def test_successful_summarization(self):
        """Test successful summarization with mocked API."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = json.dumps({
            "summary": "This is a test summary",
            "tags": ["ai", "startup"]
        })

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        with patch.object(summarizer, 'ANTHROPIC_API_KEY', 'test-key'):
            with patch.object(summarizer, 'get_client', return_value=mock_client):
                result = await summarize_item("Test title", "https://example.com")

                assert result is not None
                assert result.summary == "This is a test summary"
                assert result.tags == ["ai", "startup"]

    @pytest.mark.asyncio
    async def test_invalid_tags_filtered(self):
        """Test that invalid tags are filtered out."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = json.dumps({
            "summary": "Summary",
            "tags": ["ai", "invalid-tag", "startup", "another-invalid"]
        })

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        with patch.object(summarizer, 'ANTHROPIC_API_KEY', 'test-key'):
            with patch.object(summarizer, 'get_client', return_value=mock_client):
                result = await summarize_item("Test", "https://example.com")

                assert result is not None
                # Only valid tags should remain
                assert result.tags == ["ai", "startup"]
                assert "invalid-tag" not in result.tags

    @pytest.mark.asyncio
    async def test_json_parse_error_fallback(self):
        """Test fallback when JSON parsing fails."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Not valid JSON"

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        with patch.object(summarizer, 'ANTHROPIC_API_KEY', 'test-key'):
            with patch.object(summarizer, 'get_client', return_value=mock_client):
                result = await summarize_item("Original Title", "https://example.com")

                # Should return title as summary with empty tags
                assert result is not None
                assert result.summary == "Original Title"
                assert result.tags == []

    @pytest.mark.asyncio
    async def test_markdown_code_block_handling(self):
        """Test handling of markdown code blocks in response."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = '```json\n{"summary": "Test", "tags": ["ai"]}\n```'

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        with patch.object(summarizer, 'ANTHROPIC_API_KEY', 'test-key'):
            with patch.object(summarizer, 'get_client', return_value=mock_client):
                result = await summarize_item("Test", "https://example.com")

                assert result is not None
                assert result.summary == "Test"
                assert result.tags == ["ai"]


class TestSummarizeNewItems:
    """Tests for summarize_new_items function."""

    @pytest.mark.asyncio
    async def test_no_items_to_summarize(self, test_db):
        """Test when there are no items to summarize."""
        result = await summarize_new_items(limit=10)

        assert result.total == 0
        assert result.summarized == 0
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_batch_summarization(self, test_db):
        """Test batch summarization with mocked API."""
        # Insert items without summary
        save_items([
            {"source": "hn", "external_id": "001", "title": "Test 1", "url": "https://test.com/1"},
            {"source": "hn", "external_id": "002", "title": "Test 2", "url": "https://test.com/2"},
        ])

        # Mock successful summarization
        mock_result = SummaryResult(summary="Mocked summary", tags=["ai"])

        with patch.object(summarizer, 'summarize_item', return_value=mock_result):
            result = await summarize_new_items(limit=10)

            assert result.total == 2
            assert result.summarized == 2
            assert result.failed == 0

    @pytest.mark.asyncio
    async def test_failed_summarization_uses_title(self, test_db):
        """Test that failed summarization uses title as fallback."""
        save_items([
            {"source": "hn", "external_id": "001", "title": "Original Title", "url": "https://test.com/1"},
        ])

        # Mock failed summarization
        with patch.object(summarizer, 'summarize_item', return_value=None):
            result = await summarize_new_items(limit=10)

            assert result.total == 1
            assert result.failed == 1

            # Verify item was updated with title as summary
            from database import get_items_by_status
            items = get_items_by_status("new")
            assert items[0]["summary"] == "Original Title"
            assert json.loads(items[0]["tags"]) == []


class TestKnownTags:
    """Tests for KNOWN_TAGS configuration."""

    def test_known_tags_not_empty(self):
        """Test that KNOWN_TAGS is not empty."""
        assert len(KNOWN_TAGS) > 0

    def test_known_tags_contains_core_tags(self):
        """Test that core tags from PRD are present."""
        core_tags = ["ai", "vibe-code", "solo", "saas", "startup"]
        for tag in core_tags:
            assert tag in KNOWN_TAGS
