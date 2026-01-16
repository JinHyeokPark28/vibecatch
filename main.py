"""
VibeCatch - Trend Collector for Vibe Coders

FastAPI application for collecting and reviewing HN/Reddit/GitHub trends.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from database import init_db, get_items_by_status, get_preferences, get_item_by_id, review_item
from utils import parse_tags_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Scheduler configuration
COLLECT_INTERVAL_HOURS = int(os.getenv("COLLECT_INTERVAL_HOURS", "6"))
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"

# Global scheduler instance
scheduler: AsyncIOScheduler | None = None


async def scheduled_collect():
    """Scheduled collection job."""
    logger.info("Running scheduled collection...")
    try:
        from collectors.hackernews import collect_and_save as collect_hn
        from collectors.reddit import collect_and_save as collect_reddit
        from collectors.github import collect_and_save as collect_github
        from summarizer import summarize_new_items

        hn_result = await collect_hn()
        reddit_result = await collect_reddit()
        github_result = await collect_github()
        summary_result = await summarize_new_items(limit=10)

        logger.info(
            f"Scheduled collection complete: "
            f"HN={hn_result['inserted']}, "
            f"Reddit={reddit_result['inserted']}, "
            f"GitHub={github_result['inserted']}, "
            f"Summarized={summary_result.summarized}"
        )
    except Exception as e:
        logger.error(f"Scheduled collection failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global scheduler

    # Startup
    logger.info("Starting VibeCatch...")
    init_db()
    logger.info("Database initialized")

    # Start scheduler if enabled
    if SCHEDULER_ENABLED:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            scheduled_collect,
            trigger=IntervalTrigger(hours=COLLECT_INTERVAL_HOURS),
            id="collect_job",
            name="Collect from HN/Reddit/GitHub",
            replace_existing=True,
        )
        scheduler.start()
        logger.info(f"Scheduler started (interval: {COLLECT_INTERVAL_HOURS}h)")
    else:
        logger.info("Scheduler disabled (SCHEDULER_ENABLED=false)")

    yield

    # Shutdown
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
    logger.info("Shutting down VibeCatch...")


# Create FastAPI app
app = FastAPI(
    title="VibeCatch",
    description="Trend collector for vibe coders with AI summary and preference learning",
    version="0.1.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "vibecatch"}


@app.post("/collect")
async def collect_items():
    """
    Manual collection trigger.

    Collects items from HN, Reddit, and GitHub, then summarizes using Claude API.
    """
    from collectors.hackernews import collect_and_save as collect_hn
    from collectors.reddit import collect_and_save as collect_reddit
    from collectors.github import collect_and_save as collect_github
    from summarizer import summarize_new_items

    # Step 1: Collect from HN
    logger.info("Collecting from Hacker News...")
    hn_result = await collect_hn()

    # Step 2: Collect from Reddit
    logger.info("Collecting from Reddit...")
    reddit_result = await collect_reddit()

    # Step 3: Collect from GitHub
    logger.info("Collecting from GitHub...")
    github_result = await collect_github()

    # Step 4: Summarize new items
    logger.info("Starting summarization...")
    summary_result = await summarize_new_items(limit=10)

    return {
        "collected": {
            "hn": {
                "fetched": hn_result["fetched"],
                "inserted": hn_result["inserted"],
                "skipped": hn_result["skipped"],
            },
            "reddit": {
                "fetched": reddit_result["fetched"],
                "inserted": reddit_result["inserted"],
                "skipped": reddit_result["skipped"],
            },
            "github": {
                "fetched": github_result["fetched"],
                "inserted": github_result["inserted"],
                "skipped": github_result["skipped"],
            },
        },
        "summarized": {
            "total": summary_result.total,
            "summarized": summary_result.summarized,
            "failed": summary_result.failed,
        }
    }


def calculate_priority(item: dict, preferences: dict[str, int]) -> int:
    """Calculate item priority based on tag preferences."""
    tags = parse_tags_json(item.get("tags"))
    return sum(preferences.get(tag, 0) for tag in tags)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Card review UI - displays items for review.

    Shows items with status='new', sorted by preference score (F005).
    """
    items = get_items_by_status(status="new", limit=50)
    preferences = get_preferences()

    # Parse tags JSON for each item
    for item in items:
        item["tags"] = parse_tags_json(item.get("tags"))

    # Sort by preference score (F005)
    items.sort(key=lambda x: calculate_priority(x, preferences), reverse=True)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "items": items,
            "total_count": len(items),
        }
    )


class ReviewRequest(BaseModel):
    """Request body for review endpoint."""
    action: str  # 'like' or 'skip'


@app.post("/review/{item_id}")
async def review(item_id: int, request: ReviewRequest):
    """
    Review an item (like or skip).

    Updates item status and adjusts tag preference scores.
    """
    if request.action not in ("like", "skip"):
        return {"success": False, "error": "Invalid action. Use 'like' or 'skip'."}

    success = review_item(item_id, request.action)

    if success:
        return {"success": True, "item_id": item_id, "action": request.action}
    else:
        return {"success": False, "error": "Item not found or update failed."}


@app.get("/item/{item_id}")
async def get_item_detail(item_id: int):
    """
    Get item detail for card expansion.

    Returns item info including summary for display.
    """
    item = get_item_by_id(item_id)

    if not item:
        return {"success": False, "error": "Item not found"}

    # Parse tags
    tags = parse_tags_json(item.get("tags"))

    return {
        "success": True,
        "item": {
            "id": item["id"],
            "source": item["source"],
            "title": item["title"],
            "title_ko": item.get("title_ko"),
            "url": item.get("url"),
            "summary": item.get("summary"),
            "tags": tags,
            "collected_at": item.get("collected_at"),
        }
    }


@app.get("/liked", response_class=HTMLResponse)
async def liked_items(request: Request):
    """
    Liked items list.

    Shows items with status='liked'.
    """
    items = get_items_by_status(status="liked", limit=100)

    # Parse tags JSON for each item
    for item in items:
        item["tags"] = parse_tags_json(item.get("tags"))

    return templates.TemplateResponse(
        "liked.html",
        {
            "request": request,
            "items": items,
            "total_count": len(items),
        }
    )


@app.get("/stats", response_class=HTMLResponse)
async def stats(request: Request):
    """
    Preference statistics.

    Shows tag scores based on like/skip history.
    """
    preferences = get_preferences()

    # Sort by score (highest first)
    sorted_prefs = sorted(preferences.items(), key=lambda x: x[1], reverse=True)

    # Separate positive, negative, neutral
    positive_tags = [(tag, score) for tag, score in sorted_prefs if score > 0]
    negative_tags = [(tag, score) for tag, score in sorted_prefs if score < 0]
    neutral_tags = [(tag, score) for tag, score in sorted_prefs if score == 0]

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "positive_tags": positive_tags,
            "negative_tags": negative_tags,
            "neutral_tags": neutral_tags,
            "total_tags": len(preferences),
        }
    )


@app.get("/scheduler/status")
async def scheduler_status():
    """
    Get scheduler status.

    Returns current scheduler state and next run time.
    """
    if not scheduler:
        return {
            "enabled": False,
            "running": False,
            "message": "Scheduler not initialized",
        }

    job = scheduler.get_job("collect_job")
    next_run = None
    if job and job.next_run_time:
        next_run = job.next_run_time.isoformat()

    return {
        "enabled": SCHEDULER_ENABLED,
        "running": scheduler.running,
        "interval_hours": COLLECT_INTERVAL_HOURS,
        "next_run": next_run,
    }


@app.post("/scheduler/trigger")
async def scheduler_trigger():
    """
    Manually trigger scheduled collection.

    Runs the collection job immediately without waiting for the next interval.
    """
    if not scheduler or not scheduler.running:
        return {"success": False, "error": "Scheduler not running"}

    # Run collection in background
    asyncio.create_task(scheduled_collect())

    return {
        "success": True,
        "message": "Collection triggered in background",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
