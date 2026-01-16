"""
VibeCatch Utility Functions

Common utilities used across the application.
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def parse_tags_json(tags: Any) -> list[str]:
    """
    Parse tags from various formats to a list of strings.

    Handles:
    - JSON string: '["ai", "python"]' -> ["ai", "python"]
    - Already a list: ["ai", "python"] -> ["ai", "python"]
    - None or empty: None -> []
    - Invalid JSON: "invalid" -> []

    Args:
        tags: Tags in various formats

    Returns:
        List of tag strings
    """
    if not tags:
        return []

    if isinstance(tags, list):
        return tags

    if isinstance(tags, str):
        try:
            parsed = json.loads(tags)
            if isinstance(parsed, list):
                return parsed
            return []
        except json.JSONDecodeError:
            logger.debug(f"Failed to parse tags JSON: {tags}")
            return []

    return []
