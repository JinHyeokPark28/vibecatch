"""
VibeCatch Database Module

SQLite database connection and table management.
"""

import sqlite3
import os
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator

logger = logging.getLogger(__name__)

DATABASE_PATH = os.getenv("DATABASE_PATH", "vibecatch.db")


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database tables."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Items table - collected content
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                source TEXT NOT NULL,
                external_id TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT,
                summary TEXT,
                tags TEXT,
                status TEXT DEFAULT 'new',
                collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                reviewed_at DATETIME,
                UNIQUE(source, external_id)
            )
        """)

        # Preferences table - tag scores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                tag TEXT PRIMARY KEY,
                score INTEGER DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_status
            ON items(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_source
            ON items(source)
        """)

        logger.info("Database initialized successfully")


@dataclass
class SaveResult:
    """Result of save operation."""
    total: int
    inserted: int
    skipped: int


def save_items(items: list[dict]) -> SaveResult:
    """
    Save items to database with duplicate handling.

    Uses INSERT OR IGNORE to skip duplicates based on (source, external_id).

    Args:
        items: List of item dicts with keys: source, external_id, title, url

    Returns:
        SaveResult with counts of inserted and skipped items
    """
    if not items:
        return SaveResult(total=0, inserted=0, skipped=0)

    inserted = 0
    with get_db() as conn:
        cursor = conn.cursor()

        for item in items:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO items (source, external_id, title, url)
                    VALUES (?, ?, ?, ?)
                """, (
                    item["source"],
                    item["external_id"],
                    item["title"],
                    item.get("url"),
                ))

                if cursor.rowcount > 0:
                    inserted += 1

            except sqlite3.Error as e:
                logger.warning(f"Failed to insert item {item.get('external_id')}: {e}")

    skipped = len(items) - inserted
    result = SaveResult(total=len(items), inserted=inserted, skipped=skipped)

    logger.info(f"Saved items: {inserted} inserted, {skipped} skipped (duplicates)")
    return result


def get_items_by_status(status: str = "new", limit: int = 100) -> list[dict]:
    """Get items by status."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM items
            WHERE status = ?
            ORDER BY collected_at DESC
            LIMIT ?
        """, (status, limit))

        return [dict(row) for row in cursor.fetchall()]


def get_items_without_summary(limit: int = 10) -> list[dict]:
    """Get items that don't have a summary yet."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM items
            WHERE summary IS NULL
            ORDER BY collected_at DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]


def update_item_summary(item_id: int, summary: str, tags: list[str]) -> bool:
    """
    Update item with summary and tags.

    Args:
        item_id: Item ID
        summary: AI-generated summary
        tags: List of tags

    Returns:
        True if successful, False otherwise
    """
    import json

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE items
                SET summary = ?, tags = ?
                WHERE id = ?
            """, (summary, json.dumps(tags), item_id))

            if cursor.rowcount > 0:
                logger.info(f"Updated item {item_id} with summary")
                return True
            else:
                logger.warning(f"Item {item_id} not found")
                return False

    except sqlite3.Error as e:
        logger.error(f"Failed to update item {item_id}: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    print("Database initialized.")
