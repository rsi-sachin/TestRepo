"""
TTS Demo Tool - Web Backend
FastAPI application entry point with REST API and WebSocket support
"""

import asyncio
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from pathlib import Path

# Windows-specific fix for asyncio subprocess support
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.api import demos, execution, history, oran
from app.websockets import demo_output

# Create FastAPI app
app = FastAPI(
    title="TTS Demo Tool API",
    description="REST API and WebSocket server for TTS demonstration scenarios + O-RAN test generation",
    version="2.0.0",
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


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("TTS Demo Tool Web Backend starting...")
    # Initialize demo catalog, validate JMeter installation, etc.
    # These will be implemented in service layer


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("TTS Demo Tool Web Backend shutting down...")
    # Cleanup any running processes, close connections


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
