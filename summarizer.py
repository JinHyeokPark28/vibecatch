"""
VibeCatch AI Summarizer

Uses Claude API to summarize items and extract relevant tags.
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Optional

from anthropic import Anthropic, APIError

logger = logging.getLogger(__name__)

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-20250514"

# Known tags for vibe coders (from PRD)
KNOWN_TAGS = ["ai", "vibe-code", "solo", "saas", "startup", "llm", "python", "javascript", "rust", "go", "web", "mobile", "devtools", "opensource"]

SUMMARIZE_PROMPT = """You are a tech news summarizer for Korean developers.

Given a title and URL, provide:
1. Korean translation of the title (natural, not literal)
2. A 2-3 sentence summary in Korean explaining what this is and why it matters
3. Relevant tags from this list: {tags}

Important rules:
- For GitHub repos (format: "owner/repo" or "owner/repo: description"), explain what the project does
- For Chinese titles, translate to natural Korean
- Always provide a meaningful summary, not just repeating the title
- If URL contains "github.com", focus on what the repository is for

Respond in JSON format only:
{{
  "title_ko": "자연스러운 한글 제목",
  "summary": "2-3문장 한글 요약 (무엇인지, 왜 중요한지)",
  "tags": ["tag1", "tag2"]
}}

Only use tags from the provided list. If no tags match, return empty array.

Title: {title}
URL: {url}
"""


@dataclass
class SummaryResult:
    """Result of summarization."""
    title_ko: str
    summary: str
    tags: list[str]


def get_client() -> Optional[Anthropic]:
    """Get Anthropic client if API key is available."""
    if not ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set")
        return None
    return Anthropic(api_key=ANTHROPIC_API_KEY)


async def summarize_item(title: str, url: Optional[str] = None) -> Optional[SummaryResult]:
    """
    Summarize an item using Claude API.

    Args:
        title: Item title
        url: Item URL (optional)

    Returns:
        SummaryResult with summary and tags, or None if failed
    """
    client = get_client()
    if not client:
        logger.warning("Claude API client not available")
        return None

    try:
        prompt = SUMMARIZE_PROMPT.format(
            tags=", ".join(KNOWN_TAGS),
            title=title,
            url=url or "N/A"
        )

        message = client.messages.create(
            model=MODEL,
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse response
        response_text = message.content[0].text

        # Try to extract JSON from response
        try:
            # Handle potential markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            data = json.loads(response_text.strip())

            title_ko = data.get("title_ko", title)
            summary = data.get("summary", title)
            tags = data.get("tags", [])

            # Validate tags - only keep known tags
            valid_tags = [t for t in tags if t in KNOWN_TAGS]

            return SummaryResult(title_ko=title_ko, summary=summary, tags=valid_tags)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Claude response as JSON: {e}")
            # Return title as fallback with empty tags
            return SummaryResult(title_ko=title, summary=title, tags=[])

    except APIError as e:
        logger.error(f"Claude API error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in summarize_item: {e}")
        return None


@dataclass
class BatchSummaryResult:
    """Result of batch summarization."""
    total: int
    summarized: int
    failed: int


async def summarize_new_items(limit: int = 10) -> BatchSummaryResult:
    """
    Summarize items that don't have summaries yet.

    Args:
        limit: Maximum number of items to process

    Returns:
        BatchSummaryResult with counts
    """
    from database import get_items_without_summary, update_item_summary

    items = get_items_without_summary(limit=limit)

    if not items:
        logger.info("No items to summarize")
        return BatchSummaryResult(total=0, summarized=0, failed=0)

    logger.info(f"Summarizing {len(items)} items...")

    summarized = 0
    failed = 0

    for item in items:
        result = await summarize_item(item["title"], item.get("url"))

        if result:
            success = update_item_summary(
                item["id"],
                result.title_ko,
                result.summary,
                result.tags
            )
            if success:
                summarized += 1
            else:
                failed += 1
        else:
            # API failed - leave as NULL for retry later
            logger.warning(f"Summarization failed for item {item['id']}, will retry later")
            failed += 1

    logger.info(f"Batch summarization complete: {summarized} summarized, {failed} failed")
    return BatchSummaryResult(total=len(items), summarized=summarized, failed=failed)


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)

    async def test():
        result = await summarize_item(
            "Show HN: I built a tool to track HN/Reddit trends",
            "https://example.com"
        )
        if result:
            print(f"Summary: {result.summary}")
            print(f"Tags: {result.tags}")
        else:
            print("Summarization failed")

    asyncio.run(test())
