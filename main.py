"""
VibeCatch - Trend Collector for Vibe Coders

FastAPI application for collecting and reviewing HN/Reddit/GitHub trends.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import init_db

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


# Routes will be added here as features are implemented
# - GET / : Card review UI (F003)
# - POST /review/{id} : Feedback handler (F004)
# - GET /liked : Liked items list
# - GET /stats : Preference statistics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
