"""
FastAPI Backend Startup Script
Run with: python run.py
"""

import asyncio
import sys
import uvicorn
from app.config import settings

# Windows-specific fix for asyncio subprocess support - MUST be set before any asyncio usage
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
