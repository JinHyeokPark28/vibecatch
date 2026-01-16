"""
VibeCatch Database Module v2.0

SQLite database connection and table management.
Supports multi-user with UUID-based identification.
"""

import sqlite3
import os
import json
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Generator
from uuid import uuid4

logger = logging.getLogger(__name__)

DATABASE_PATH = os.getenv("DATABASE_PATH", "vibecatch.db")


def _ensure_db_directory():
    """Ensure database directory exists with retry for Volume mount."""
    import time

    db_dir = os.path.dirname(DATABASE_PATH)
    if not db_dir:
        return  # Using filename only, no directory needed

    max_retries = 10
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            if not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            # Test if we can write to the directory
            test_file = os.path.join(db_dir, ".write_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            logger.info(f"Database directory ready: {db_dir}")
            return
        except (OSError, PermissionError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"Waiting for volume mount (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to access database directory after {max_retries} attempts: {e}")
                raise

# Rate limit settings
RATE_LIMIT_FREE_COLLECT = 3  # per day
RATE_LIMIT_FREE_SUMMARIZE = 30  # per day


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
    """Initialize database tables (v2.0 schema)."""
    # v2.0: Ensure directory exists (with retry for Railway Volume mount)
    _ensure_db_directory()

    with get_db() as conn:
        cursor = conn.cursor()

        # ============================================
        # V2.0 TABLES
        # ============================================

        # Users table (UUID-based)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uuid TEXT PRIMARY KEY,
                email TEXT,
                tier TEXT DEFAULT 'free',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen_at DATETIME
            )
        """)

        # Items table - collected content (SHARED)
        # Note: status and reviewed_at are kept for backward compatibility
        # but v2.0 uses user_items table for per-user status
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                source TEXT NOT NULL,
                external_id TEXT NOT NULL,
                title TEXT NOT NULL,
                title_ko TEXT,
                url TEXT,
                summary TEXT,
                tags TEXT,
                status TEXT DEFAULT 'new',
                collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                reviewed_at DATETIME,
                UNIQUE(source, external_id)
            )
        """)

        # User items table - per-user item status
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_items (
                user_uuid TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                status TEXT DEFAULT 'new',
                reviewed_at DATETIME,
                PRIMARY KEY (user_uuid, item_id),
                FOREIGN KEY (user_uuid) REFERENCES users(uuid),
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        """)

        # Preferences table v2 - per-user tag scores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_uuid TEXT NOT NULL,
                tag TEXT NOT NULL,
                score INTEGER DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_uuid, tag),
                FOREIGN KEY (user_uuid) REFERENCES users(uuid)
            )
        """)

        # Rate limits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                user_uuid TEXT NOT NULL,
                date TEXT NOT NULL,
                collect_count INTEGER DEFAULT 0,
                summarize_count INTEGER DEFAULT 0,
                PRIMARY KEY (user_uuid, date),
                FOREIGN KEY (user_uuid) REFERENCES users(uuid)
            )
        """)

        # ============================================
        # INDEXES
        # ============================================
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_source
            ON items(source)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_items_status
            ON user_items(user_uuid, status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_preferences
            ON user_preferences(user_uuid)
        """)

        # ============================================
        # MIGRATION: Handle legacy data
        # ============================================
        _migrate_legacy_data(cursor)

        logger.info("Database v2.0 initialized successfully")


def _migrate_legacy_data(cursor: sqlite3.Cursor) -> None:
    """Migrate data from v1.x schema to v2.0."""
    # Check if legacy 'status' column exists in items
    cursor.execute("PRAGMA table_info(items)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'status' in columns:
        # Check if we have legacy data to migrate
        cursor.execute("SELECT COUNT(*) FROM items WHERE status IS NOT NULL AND status != 'new'")
        legacy_count = cursor.fetchone()[0]

        if legacy_count > 0:
            logger.info(f"Migrating {legacy_count} legacy items...")

            # Create a legacy user for existing data
            legacy_uuid = "legacy-user-migration"
            cursor.execute("""
                INSERT OR IGNORE INTO users (uuid, email, tier, created_at)
                VALUES (?, 'legacy@migration', 'free', ?)
            """, (legacy_uuid, datetime.now().isoformat()))

            # Migrate reviewed items to user_items
            cursor.execute("""
                INSERT OR IGNORE INTO user_items (user_uuid, item_id, status, reviewed_at)
                SELECT ?, id, status, reviewed_at
                FROM items
                WHERE status IS NOT NULL AND status != 'new'
            """, (legacy_uuid,))

            # Migrate preferences to user_preferences
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='preferences'")
            if cursor.fetchone():
                cursor.execute("""
                    INSERT OR IGNORE INTO user_preferences (user_uuid, tag, score, updated_at)
                    SELECT ?, tag, score, updated_at
                    FROM preferences
                """, (legacy_uuid,))

            logger.info(f"Migration complete. Legacy user UUID: {legacy_uuid}")


# ============================================
# USER FUNCTIONS (v2.0)
# ============================================

def get_or_create_user(user_uuid: str | None = None) -> str:
    """
    Get existing user or create new one.

    Args:
        user_uuid: Existing UUID or None to create new

    Returns:
        User UUID
    """
    if not user_uuid:
        user_uuid = str(uuid4())

    with get_db() as conn:
        cursor = conn.cursor()

        # Try to get existing user
        cursor.execute("SELECT uuid FROM users WHERE uuid = ?", (user_uuid,))
        existing = cursor.fetchone()

        if existing:
            # Update last_seen
            cursor.execute("""
                UPDATE users SET last_seen_at = ? WHERE uuid = ?
            """, (datetime.now().isoformat(), user_uuid))
        else:
            # Create new user
            cursor.execute("""
                INSERT INTO users (uuid, created_at, last_seen_at)
                VALUES (?, ?, ?)
            """, (user_uuid, datetime.now().isoformat(), datetime.now().isoformat()))
            logger.info(f"Created new user: {user_uuid[:8]}...")

    return user_uuid


def get_user(user_uuid: str) -> dict | None:
    """Get user by UUID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE uuid = ?", (user_uuid,))
        row = cursor.fetchone()
        return dict(row) if row else None


def sync_items_for_user(user_uuid: str) -> int:
    """
    Sync all items to user_items for a user.
    Creates 'new' status for items the user hasn't seen.

    Returns:
        Number of new items synced
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Insert items that user hasn't seen yet
        cursor.execute("""
            INSERT OR IGNORE INTO user_items (user_uuid, item_id, status)
            SELECT ?, id, 'new'
            FROM items
            WHERE id NOT IN (
                SELECT item_id FROM user_items WHERE user_uuid = ?
            )
        """, (user_uuid, user_uuid))

        synced = cursor.rowcount
        if synced > 0:
            logger.info(f"Synced {synced} new items for user {user_uuid[:8]}...")

        return synced


# ============================================
# RATE LIMIT FUNCTIONS (v2.0)
# ============================================

def check_rate_limit(user_uuid: str, action: str = "collect") -> tuple[bool, int]:
    """
    Check if user has exceeded rate limit.

    Args:
        user_uuid: User UUID
        action: 'collect' or 'summarize'

    Returns:
        Tuple of (allowed: bool, remaining: int)
    """
    # Get user tier
    user = get_user(user_uuid)
    if user and user.get("tier") == "supporter":
        return True, -1  # Unlimited

    today = datetime.now().strftime("%Y-%m-%d")
    limit = RATE_LIMIT_FREE_COLLECT if action == "collect" else RATE_LIMIT_FREE_SUMMARIZE

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT collect_count, summarize_count FROM rate_limits
            WHERE user_uuid = ? AND date = ?
        """, (user_uuid, today))

        row = cursor.fetchone()
        if not row:
            return True, limit

        current = row[0] if action == "collect" else row[1]
        remaining = limit - current

        return remaining > 0, max(0, remaining)


def increment_rate_limit(user_uuid: str, action: str = "collect") -> None:
    """Increment rate limit counter for user."""
    today = datetime.now().strftime("%Y-%m-%d")
    column = "collect_count" if action == "collect" else "summarize_count"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO rate_limits (user_uuid, date, {column})
            VALUES (?, ?, 1)
            ON CONFLICT(user_uuid, date) DO UPDATE SET
                {column} = {column} + 1
        """, (user_uuid, today))


# ============================================
# USER-SPECIFIC DATA FUNCTIONS (v2.0)
# ============================================

def get_user_items(user_uuid: str, status: str = "new", limit: int = 100) -> list[dict]:
    """Get items for a specific user by status."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.*, ui.status as user_status, ui.reviewed_at as user_reviewed_at
            FROM items i
            JOIN user_items ui ON i.id = ui.item_id
            WHERE ui.user_uuid = ? AND ui.status = ?
            ORDER BY i.collected_at DESC
            LIMIT ?
        """, (user_uuid, status, limit))

        return [dict(row) for row in cursor.fetchall()]


def get_user_preferences(user_uuid: str) -> dict[str, int]:
    """Get tag preferences for a specific user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tag, score FROM user_preferences
            WHERE user_uuid = ?
        """, (user_uuid,))

        return {row[0]: row[1] for row in cursor.fetchall()}


def review_item_for_user(user_uuid: str, item_id: int, action: str) -> bool:
    """
    Review an item for a specific user.

    Args:
        user_uuid: User UUID
        item_id: Item ID
        action: 'like' or 'skip'

    Returns:
        True if successful
    """
    if action not in ("like", "skip"):
        logger.error(f"Invalid action: {action}")
        return False

    try:
        with get_db() as conn:
            cursor = conn.cursor()

            # Get item tags
            cursor.execute("SELECT tags FROM items WHERE id = ?", (item_id,))
            row = cursor.fetchone()

            if not row:
                logger.warning(f"Item {item_id} not found")
                return False

            # Update user_items status
            status = "liked" if action == "like" else "skipped"
            cursor.execute("""
                INSERT INTO user_items (user_uuid, item_id, status, reviewed_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_uuid, item_id) DO UPDATE SET
                    status = ?, reviewed_at = ?
            """, (user_uuid, item_id, status, datetime.now().isoformat(),
                  status, datetime.now().isoformat()))

            # Update user preferences
            tags_json = row[0]
            if tags_json:
                tags = json.loads(tags_json)
                score_delta = 1 if action == "like" else -1

                for tag in tags:
                    cursor.execute("""
                        INSERT INTO user_preferences (user_uuid, tag, score, updated_at)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(user_uuid, tag) DO UPDATE SET
                            score = score + ?,
                            updated_at = ?
                    """, (user_uuid, tag, score_delta, datetime.now().isoformat(),
                          score_delta, datetime.now().isoformat()))

            logger.info(f"User {user_uuid[:8]}... reviewed item {item_id} as {status}")
            return True

    except sqlite3.Error as e:
        logger.error(f"Failed to review item {item_id} for user {user_uuid[:8]}...: {e}")
        return False


# ============================================
# LEGACY FUNCTIONS (kept for backward compatibility)
# ============================================

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


def update_item_summary(item_id: int, title_ko: str, summary: str, tags: list[str]) -> bool:
    """
    Update item with Korean title, summary and tags.

    Args:
        item_id: Item ID
        title_ko: Korean translation of title
        summary: AI-generated summary in Korean
        tags: List of tags

    Returns:
        True if successful, False otherwise
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE items
                SET title_ko = ?, summary = ?, tags = ?
                WHERE id = ?
            """, (title_ko, summary, json.dumps(tags), item_id))

            if cursor.rowcount > 0:
                logger.info(f"Updated item {item_id} with Korean title and summary")
                return True
            else:
                logger.warning(f"Item {item_id} not found")
                return False

    except sqlite3.Error as e:
        logger.error(f"Failed to update item {item_id}: {e}")
        return False


def get_item_by_id(item_id: int) -> dict | None:
    """Get a single item by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_preferences() -> dict[str, int]:
    """
    Get all tag preference scores.

    Returns:
        Dict mapping tag names to scores
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tag, score FROM preferences")
        return {row[0]: row[1] for row in cursor.fetchall()}


def review_item(item_id: int, action: str) -> bool:
    """
    Review an item (like or skip).

    Args:
        item_id: Item ID
        action: 'like' or 'skip'

    Returns:
        True if successful, False otherwise
    """
    if action not in ("like", "skip"):
        logger.error(f"Invalid action: {action}")
        return False

    try:
        with get_db() as conn:
            cursor = conn.cursor()

            # Get item tags first
            cursor.execute("SELECT tags FROM items WHERE id = ?", (item_id,))
            row = cursor.fetchone()

            if not row:
                logger.warning(f"Item {item_id} not found")
                return False

            # Update item status
            status = "liked" if action == "like" else "skipped"
            cursor.execute("""
                UPDATE items
                SET status = ?, reviewed_at = ?
                WHERE id = ?
            """, (status, datetime.now().isoformat(), item_id))

            # Update tag preferences
            tags_json = row[0]
            if tags_json:
                tags = json.loads(tags_json)
                score_delta = 1 if action == "like" else -1

                for tag in tags:
                    cursor.execute("""
                        INSERT INTO preferences (tag, score, updated_at)
                        VALUES (?, ?, ?)
                        ON CONFLICT(tag) DO UPDATE SET
                            score = score + ?,
                            updated_at = ?
                    """, (tag, score_delta, datetime.now().isoformat(),
                          score_delta, datetime.now().isoformat()))

            logger.info(f"Item {item_id} marked as {status}")
            return True

    except sqlite3.Error as e:
        logger.error(f"Failed to review item {item_id}: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    print("Database initialized.")
