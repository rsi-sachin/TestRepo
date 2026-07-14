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
from datetime import datetime, timezone
from html import escape

# Windows-specific fix for asyncio subprocess support
if sys.platform == 'win32' and sys.version_info < (3, 13):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.api import demos, execution, history, oran, test_cases
from app.websockets import demo_output
from app.database import init_db
from app.intelligent_document_parsing.api_routes import router as doc_analysis_router
import logging

logger = logging.getLogger(__name__)


def _feature_plan_path() -> Path:
    """Resolve FEATURE_PLAN path from backend app location."""
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "ORAN" / "FEATURE_PLAN.md"


def _normalize_status_for_board(status: str) -> str:
    """Convert plan statuses into requested board perspective."""
    normalized = status.strip().lower()
    if normalized in {"in progress", "in-progress", "inprogress", "incomplete"}:
        return "In Progress"
    if normalized == "complete":
        return "Complete"
    return "TBD"


def _extract_feature_plan_status_board() -> dict:
    """Parse module status board from ORAN FEATURE_PLAN markdown table."""
    plan_path = _feature_plan_path()
    if not plan_path.exists():
        return {
            "plan_path": str(plan_path),
            "last_updated": "Unknown",
            "modules": [],
            "summary": {"Complete": 0, "In Progress": 0, "TBD": 0},
            "next_best_item": "FEATURE_PLAN.md not found; add ORAN/FEATURE_PLAN.md to enable status board.",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    content = plan_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    last_updated = "Unknown"
    for line in lines:
        if line.startswith("Last updated:"):
            last_updated = line.split(":", 1)[1].strip()
            break

    header_index = next((i for i, line in enumerate(lines) if line.strip().startswith("| Module | Status |")), -1)
    modules: list[dict] = []
    if header_index >= 0:
        for row in lines[header_index + 1:]:
            stripped = row.strip()
            if not stripped.startswith("|"):
                break
            if "---" in stripped:
                continue
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if len(cells) < 4:
                continue
            raw_status = cells[1]
            modules.append(
                {
                    "module": cells[0],
                    "status": _normalize_status_for_board(raw_status),
                    "raw_status": raw_status,
                    "conformance_coverage": cells[2],
                    "evidence_anchor": cells[3],
                }
            )

    summary = {"Complete": 0, "In Progress": 0, "TBD": 0}
    for module in modules:
        if module["status"] in summary:
            summary[module["status"]] += 1

    module_names_in_progress = {m["module"] for m in modules if m["status"] == "In Progress"}
    module_names_tbd = {m["module"] for m in modules if m["status"] == "TBD"}

    if {"Non-RT RIC + A1 Interface", "Conformance Harness"}.intersection(module_names_in_progress):
        next_best_item = (
            "Close the A1 release gate by completing remaining TS 103 989 section 4.2.1 and 4.2.2 executable "
            "conformance checks and evidence outputs until the 26-test gate is fully passing."
        )
    elif {"O1 Interface", "E2 Interface"}.intersection(module_names_tbd):
        next_best_item = "Implement O1 and E2 production-capable contracts with schema validation, deterministic errors, and conformance tests."
    elif module_names_tbd:
        next_best_item = "Implement remaining simulator modules and connect them to cross-module conformance execution."
    else:
        next_best_item = "Run cross-module conformance and integration suites, then promote modules to Complete with evidence bundles."

    return {
        "plan_path": str(plan_path),
        "last_updated": last_updated,
        "modules": modules,
        "summary": summary,
        "next_best_item": next_best_item,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _render_status_rows_html(modules: list[dict]) -> str:
    rows = []
    for module in modules:
        status_class = module["status"].lower().replace(" ", "-")
        rows.append(
            "<tr>"
            f"<td>{escape(module['module'])}</td>"
            f"<td><span class='status-pill {escape(status_class)}'>{escape(module['status'])}</span></td>"
            f"<td>{escape(module['conformance_coverage'])}</td>"
            f"<td>{escape(module['evidence_anchor'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else "<tr><td colspan='4'>No status rows found in FEATURE_PLAN.md.</td></tr>"


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
app.include_router(doc_analysis_router, tags=["Document Analysis"])

# Include WebSocket router
app.include_router(demo_output.router, prefix="/ws", tags=["WebSocket"])


@app.get("/api/oran/feature-plan/status-board")
async def feature_plan_status_board():
    """Return FEATURE_PLAN module status board in JSON format."""
    return _extract_feature_plan_status_board()


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


@app.get("/oran/status-board", response_class=HTMLResponse)
async def oran_status_board():
    """Serve FEATURE_PLAN status board as HTML for UI viewing."""
    payload = _extract_feature_plan_status_board()
    template_path = frontend_path / "templates" / "oran_status_board.html"

    if not template_path.exists():
        return """
        <html><body><h1>Status Board Template Missing</h1><p>Create frontend/templates/oran_status_board.html</p></body></html>
        """

    html = template_path.read_text(encoding="utf-8")
    html = html.replace("__LAST_UPDATED__", escape(payload["last_updated"]))
    html = html.replace("__GENERATED_AT__", escape(payload["generated_at"]))
    html = html.replace("__SUMMARY_COMPLETE__", str(payload["summary"]["Complete"]))
    html = html.replace("__SUMMARY_IN_PROGRESS__", str(payload["summary"]["In Progress"]))
    html = html.replace("__SUMMARY_TBD__", str(payload["summary"]["TBD"]))
    html = html.replace("__NEXT_BEST_ITEM__", escape(payload["next_best_item"]))
    html = html.replace("__STATUS_ROWS__", _render_status_rows_html(payload["modules"]))
    return html


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
