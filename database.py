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
        # ANALYTICS TABLES (v2.1)
        # ============================================

        # Events log - all user actions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                user_uuid TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_uuid) REFERENCES users(uuid)
            )
        """)

        # Daily stats - aggregated metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                unique_users INTEGER DEFAULT 0,
                pageviews INTEGER DEFAULT 0,
                collects INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                skips INTEGER DEFAULT 0,
                rate_limit_hits INTEGER DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_type_date
            ON events(event_type, created_at)
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


def expire_old_items(user_uuid: str, days: int = 3) -> int:
    """
    Expire items older than specified days.

    Changes status from 'new' to 'expired' for old items.

    Args:
        user_uuid: User UUID
        days: Number of days before expiration (default 3)

    Returns:
        Number of items expired
    """
    from datetime import timedelta

    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_items
            SET status = 'expired'
            WHERE user_uuid = ?
              AND status = 'new'
              AND item_id IN (
                  SELECT id FROM items WHERE collected_at < ?
              )
        """, (user_uuid, cutoff_date))

        expired_count = cursor.rowcount
        if expired_count > 0:
            logger.info(f"Expired {expired_count} old items for user {user_uuid[:8]}...")

        return expired_count


def get_for_you_items(user_uuid: str, min_score: int = 3, limit: int = 20) -> list[dict]:
    """
    Get personalized "For You" items based on tag preferences.

    Only returns items with preference score >= min_score.

    Args:
        user_uuid: User UUID
        min_score: Minimum total preference score (default 3)
        limit: Maximum items to return

    Returns:
        List of items with calculated scores
    """
    # Get user preferences
    preferences = get_user_preferences(user_uuid)

    if not preferences:
        # No preferences yet, return empty
        return []

    # Get new items
    items = get_user_items(user_uuid, status="new", limit=200)

    # Calculate score for each item
    scored_items = []
    for item in items:
        tags_json = item.get("tags")
        if not tags_json:
            continue

        try:
            tags = json.loads(tags_json) if isinstance(tags_json, str) else tags_json
        except json.JSONDecodeError:
            continue

        # Calculate total score
        total_score = sum(preferences.get(tag, 0) for tag in tags)

        if total_score >= min_score:
            item["preference_score"] = total_score
            scored_items.append(item)

    # Sort by score (highest first)
    scored_items.sort(key=lambda x: x.get("preference_score", 0), reverse=True)

    return scored_items[:limit]


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
    """
    Get items that need summarization.

    Includes:
    - Items with no summary (NULL)
    - Items where summary equals title (failed summarization fallback)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM items
            WHERE summary IS NULL
               OR summary = title
               OR title_ko IS NULL
               OR title_ko = title
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


# ============================================
# ANALYTICS FUNCTIONS (v2.1)
# ============================================

def log_event(user_uuid: str, event_type: str, event_data: dict | None = None) -> None:
    """
    Log an analytics event.

    Event types:
    - pageview: {page: '/', '/liked', '/stats'}
    - collect: {hn: N, reddit: N, github: N}
    - like: {item_id: N, source: 'hn'}
    - skip: {item_id: N, source: 'hn'}
    - rate_limit_hit: {action: 'collect'}
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (user_uuid, event_type, event_data, created_at)
                VALUES (?, ?, ?, ?)
            """, (user_uuid, event_type, json.dumps(event_data) if event_data else None,
                  datetime.now().isoformat()))

            # Update daily stats
            _update_daily_stats(cursor, event_type)

    except sqlite3.Error as e:
        logger.warning(f"Failed to log event: {e}")


def _update_daily_stats(cursor: sqlite3.Cursor, event_type: str) -> None:
    """Update daily aggregated stats."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Map event type to column
    column_map = {
        "pageview": "pageviews",
        "collect": "collects",
        "like": "likes",
        "skip": "skips",
        "rate_limit_hit": "rate_limit_hits",
    }

    column = column_map.get(event_type)
    if not column:
        return

    cursor.execute(f"""
        INSERT INTO daily_stats (date, {column}, updated_at)
        VALUES (?, 1, ?)
        ON CONFLICT(date) DO UPDATE SET
            {column} = {column} + 1,
            updated_at = ?
    """, (today, datetime.now().isoformat(), datetime.now().isoformat()))


def update_daily_unique_users() -> None:
    """Update unique users count for today (call once per user session)."""
    today = datetime.now().strftime("%Y-%m-%d")

    with get_db() as conn:
        cursor = conn.cursor()

        # Count unique users from events today
        cursor.execute("""
            SELECT COUNT(DISTINCT user_uuid) FROM events
            WHERE DATE(created_at) = ?
        """, (today,))
        unique_count = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO daily_stats (date, unique_users, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                unique_users = ?,
                updated_at = ?
        """, (today, unique_count, datetime.now().isoformat(),
              unique_count, datetime.now().isoformat()))


def get_analytics(days: int = 7) -> dict:
    """
    Get analytics data for dashboard.

    Returns:
        {
            "summary": {total_users, total_items, total_likes, hit_rate},
            "daily": [{date, users, pageviews, likes, skips, hit_rate}, ...],
            "sources": {hn: N, reddit: N, github: N},
            "top_tags": [{tag, likes, skips}, ...],
            "retention": {d1, d7}
        }
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Summary stats
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM items")
        total_items = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM user_items WHERE status = 'liked'")
        total_likes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM user_items WHERE status = 'skipped'")
        total_skips = cursor.fetchone()[0]

        total_reviews = total_likes + total_skips
        hit_rate = round((total_likes / total_reviews * 100), 1) if total_reviews > 0 else 0

        # Daily stats
        cursor.execute("""
            SELECT date, unique_users, pageviews, likes, skips, collects, rate_limit_hits
            FROM daily_stats
            ORDER BY date DESC
            LIMIT ?
        """, (days,))
        daily = []
        for row in cursor.fetchall():
            day_likes = row[3] or 0
            day_skips = row[4] or 0
            day_total = day_likes + day_skips
            day_hit_rate = round((day_likes / day_total * 100), 1) if day_total > 0 else 0
            daily.append({
                "date": row[0],
                "users": row[1] or 0,
                "pageviews": row[2] or 0,
                "likes": day_likes,
                "skips": day_skips,
                "collects": row[5] or 0,
                "rate_limit_hits": row[6] or 0,
                "hit_rate": day_hit_rate,
            })

        # Source preference
        cursor.execute("""
            SELECT i.source,
                   SUM(CASE WHEN ui.status = 'liked' THEN 1 ELSE 0 END) as likes,
                   SUM(CASE WHEN ui.status = 'skipped' THEN 1 ELSE 0 END) as skips
            FROM items i
            JOIN user_items ui ON i.id = ui.item_id
            GROUP BY i.source
        """)
        sources = {}
        for row in cursor.fetchall():
            source_likes = row[1] or 0
            source_skips = row[2] or 0
            source_total = source_likes + source_skips
            sources[row[0]] = {
                "likes": source_likes,
                "skips": source_skips,
                "hit_rate": round((source_likes / source_total * 100), 1) if source_total > 0 else 0
            }

        # Top tags by engagement (try user_preferences first, fallback to preferences)
        try:
            cursor.execute("""
                SELECT tag, SUM(score) as total_score
                FROM user_preferences
                GROUP BY tag
                ORDER BY total_score DESC
                LIMIT 10
            """)
            top_tags = [{"tag": row[0], "score": row[1]} for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Fallback to legacy preferences table
            try:
                cursor.execute("""
                    SELECT tag, score FROM preferences
                    ORDER BY score DESC
                    LIMIT 10
                """)
                top_tags = [{"tag": row[0], "score": row[1]} for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                top_tags = []

        # Retention (D1)
        today = datetime.now().strftime("%Y-%m-%d")
        d1_retention = 0

        try:
            cursor.execute("""
                SELECT COUNT(DISTINCT uuid) FROM users
                WHERE DATE(created_at) = DATE(?, '-1 day')
            """, (today,))
            yesterday_new = cursor.fetchone()[0]

            if yesterday_new > 0:
                cursor.execute("""
                    SELECT COUNT(DISTINCT e.user_uuid) FROM events e
                    JOIN users u ON e.user_uuid = u.uuid
                    WHERE DATE(u.created_at) = DATE(?, '-1 day')
                      AND DATE(e.created_at) = ?
                """, (today, today))
                d1_returned = cursor.fetchone()[0]
                d1_retention = round((d1_returned / yesterday_new * 100), 1)
        except sqlite3.OperationalError:
            # events table may not exist yet
            pass

        return {
            "summary": {
                "total_users": total_users,
                "total_items": total_items,
                "total_likes": total_likes,
                "total_skips": total_skips,
                "hit_rate": hit_rate,
            },
            "daily": daily,
            "sources": sources,
            "top_tags": top_tags,
            "retention": {
                "d1": d1_retention,
            }
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    print("Database initialized.")
