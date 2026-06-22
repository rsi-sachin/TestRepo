"""
TTS Demo Tool - Web Backend
FastAPI application entry point with REST API and WebSocket support
"""

import asyncio
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from pathlib import Path

# Windows-specific fix for asyncio subprocess support
if sys.platform == 'win32' and sys.version_info < (3, 13):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.api import demos, execution, history, oran, test_cases
from app.websockets import demo_output
from app.database import init_db
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup services using FastAPI lifespan hooks."""
    logger.info("TTS Demo Tool Web Backend starting...")

    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    logger.info("Startup complete")

    yield

    logger.info("TTS Demo Tool Web Backend shutting down...")

# Create FastAPI app
app = FastAPI(
    title="TTS Demo Tool API",
    description="REST API and WebSocket server for TTS demonstration scenarios + O-RAN test generation",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_path = Path(__file__).parent.parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

# Include API routers
app.include_router(demos.router, prefix="/api", tags=["Demos"])
app.include_router(execution.router, prefix="/api", tags=["Execution"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(oran.router, prefix="/api/oran", tags=["ORAN"])
app.include_router(test_cases.router, prefix="/api/oran", tags=["Test Cases"])

# Include WebSocket router
app.include_router(demo_output.router, prefix="/ws", tags=["WebSocket"])


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main application page"""
    index_path = frontend_path / "templates" / "index.html"
    if index_path.exists():
        return index_path.read_text()
    return """
    <html>
        <head><title>TTS Demo Tool</title></head>
        <body>
            <h1>TTS Demo Tool - Web Interface</h1>
            <p>Frontend not yet built. API documentation: <a href="/api/docs">/api/docs</a></p>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tts-demo-tool-web",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
