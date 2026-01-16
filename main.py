"""
VibeCatch - Trend Collector for Vibe Coders

FastAPI application for collecting and reviewing HN/Reddit/GitHub trends.
"""

import logging
from contextlib import asynccontextmanager

import json

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

from database import init_db, get_items_by_status, review_item

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting VibeCatch...")
    init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
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

    Collects items from HN and summarizes them using Claude API.
    """
    from collectors.hackernews import collect_and_save
    from summarizer import summarize_new_items

    # Step 1: Collect from HN
    logger.info("Starting collection...")
    collect_result = await collect_and_save()

    # Step 2: Summarize new items
    logger.info("Starting summarization...")
    summary_result = await summarize_new_items(limit=10)

    return {
        "collected": {
            "fetched": collect_result["fetched"],
            "inserted": collect_result["inserted"],
            "skipped": collect_result["skipped"],
        },
        "summarized": {
            "total": summary_result.total,
            "summarized": summary_result.summarized,
            "failed": summary_result.failed,
        }
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Card review UI - displays items for review.

    Shows items with status='new', sorted by collected_at (newest first).
    Priority sorting will be added in F005.
    """
    items = get_items_by_status(status="new", limit=50)

    # Parse tags JSON for each item
    for item in items:
        if item.get("tags"):
            try:
                item["tags"] = json.loads(item["tags"])
            except json.JSONDecodeError:
                item["tags"] = []
        else:
            item["tags"] = []

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


# Routes to be added:
# - GET /liked : Liked items list
# - GET /stats : Preference statistics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
