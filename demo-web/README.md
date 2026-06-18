# TTS Demo Tool - Web Application

Browser-based version of the TTS Demo Tool with FastAPI backend and vanilla JavaScript frontend.

## Project Structure

```
demo-web/
├── backend/          # FastAPI Python backend
│   ├── app/
│   │   ├── api/      # REST API endpoints
│   │   ├── models/   # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   └── websockets/ # WebSocket handlers
│   ├── requirements.txt
│   └── run.py
├── frontend/         # Static web frontend
│   ├── static/
│   │   ├── css/      # Stylesheets
│   │   └── js/       # JavaScript modules
│   └── templates/
│       └── index.html
└── tests/            # Playwright E2E tests
    ├── e2e/
    └── unit/
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **WebSockets**: Real-time communication
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Plotly.js**: Interactive charts
- **Mermaid.js**: Sequence diagram rendering
- **CSS Grid/Flexbox**: Responsive layout

### Testing
- **Playwright**: End-to-end browser automation
- **Pytest**: Test framework

## Setup Instructions

### 1. Prerequisites
- Python 3.11 or higher
- Node.js 18+ (for Playwright browsers)
- TTS installed at `C:\TTS` (or update `.env`)

### 2. Backend Setup

```powershell
# Navigate to backend directory
cd C:\TestRepo\demo-web\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Edit .env to match your setup
notepad .env

# Run backend
python run.py
```

Backend will start at: http://localhost:8000

### 3. Frontend

Frontend is served by FastAPI from `/frontend` directory. No separate build step required.

Access at: http://localhost:8000

API documentation: http://localhost:8000/api/docs

### 4. Testing Setup

```powershell
# Install test dependencies
cd C:\TestRepo\demo-web\tests
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run tests
pytest e2e/test_demo_workflows.py -v
```

## API Endpoints

### REST API

#### Demos
- `GET /api/demos` - List all demos
- `GET /api/demos/{id}` - Get demo details
- `GET /api/demos/protocols` - List protocols
- `GET /api/demos/categories` - List categories

#### Execution
- `POST /api/execute` - Start demo execution
- `GET /api/execute/{id}/status` - Get execution status
- `POST /api/execute/{id}/cancel` - Cancel execution
- `GET /api/execute/active` - List active executions

#### History
- `GET /api/history` - Get run history
- `GET /api/history/{id}` - Get run details
- `GET /api/history/statistics` - Aggregated statistics
- `DELETE /api/history/{id}` - Delete run

### WebSocket

- `WS /ws/demo-output/{execution_id}` - Real-time demo output stream

Message types:
- `output`: Console output line
- `sip_message`: SIP call flow message
- `traffic_stats`: Real-time statistics
- `status`: Execution status change
- `complete`: Execution completed

## Development

### Running in Development Mode

```powershell
# Backend with auto-reload
cd backend
python run.py

# Backend will reload on code changes
```

### Code Style

```powershell
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## Architecture

### Service Layer Reuse
The backend reuses business logic concepts from the Java desktop app:
- `DemoService` → `DemoCatalog.java`
- `ExecutionService` → `DemoRunner.java`
- Models → Java POJOs

### Real-Time Communication Flow
```
JMeter Process → ExecutionService → WebSocket → Browser
                       ↓
                  Parse JTL File
                       ↓
                Update Statistics
```

### Frontend Architecture
```
index.html → app.js → API/WebSocket
                ↓
         Plotly (Charts)
         Mermaid (Diagrams)
```

## Playwright Testing

### Running Tests

```powershell
# Run all E2E tests
pytest tests/e2e/ -v

# Run specific test
pytest tests/e2e/test_demo_workflows.py::TestDemoSelection::test_load_homepage -v

# Run with headed browser (see what's happening)
pytest tests/e2e/ -v --headed

# Generate HTML report
pytest tests/e2e/ --html=report.html
```

### Test Structure

Tests are organized by workflow:
- `TestDemoSelection`: Demo browsing and filtering
- `TestDemoExecution`: Running demos
- `TestNavigation`: Tab switching
- `TestTrafficGenerator`: Traffic generation UI
- `TestAPIIntegration`: API endpoint validation

## Migration from Desktop App

See [MIGRATION.md](../MIGRATION.md) for detailed migration guide.

Key differences:
- JavaFX → HTML/CSS/JavaScript
- `Platform.runLater()` → WebSocket callbacks
- Canvas drawing → SVG/Mermaid.js
- FXML → HTML templates
- Event handlers → JavaScript event listeners

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (must be 3.11+)
- Check TTS path in `.env`
- Check demo catalog path: `DEMO_CATALOG_PATH` in `.env`

### Frontend not loading
- Check backend is running: http://localhost:8000/health
- Check browser console for errors
- Clear browser cache

### WebSocket not connecting
- Check firewall settings
- Verify WebSocket URL in browser console
- Check backend logs for connection attempts

### Tests failing
- Ensure backend is running before tests
- Check Playwright browsers installed: `playwright install chromium`
- Increase timeouts in `conftest.py` if tests are slow

## Production Deployment

### Backend

```powershell
# Production server (Gunicorn/Uvicorn)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or with Gunicorn
gunicorn app.main:app --bind 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker --workers 4
```

### Environment Variables
Set in production:
- `DEBUG=false`
- `CORS_ORIGINS=["https://your-domain.com"]`
- Update paths to absolute production paths

### Security Considerations
- Enable HTTPS
- Configure CORS properly
- Implement authentication/authorization
- Rate limiting on API endpoints
- Input validation (already done via Pydantic)

## License

Copyright 2026 Computaris. All rights reserved.
