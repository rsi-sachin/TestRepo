# Phase 2 Complete - Testing Guide

**Date**: May 14, 2026  
**Status**: ✅ Phase 2 Core Features Complete

## What Was Built

### Backend (FastAPI + Python)
✅ **DemoService**
- Loads 12 demos from demos.json
- Supports filtering by protocol, complexity, and search text
- Returns properly formatted JSON with camelCase/snake_case handling

✅ **ExecutionService**  
- Spawns JMeter subprocess with parameters
- Streams console output in real-time via WebSocket
- Parses JTL files for success/failure statistics
- Handles process lifecycle (start, monitor, cleanup)

✅ **API Endpoints**
- `GET /health` - Health check
- `GET /api/demos` - List all demos (12 demos loaded)
- `GET /api/demos/{id}` - Get demo by ID
- `GET /api/demos/protocols` - List protocols (SIP_IMS, DIAMETER, RADIUS)
- `GET /api/demos/complexity-levels` - List complexity levels
- `POST /api/execute` - Execute demo (returns execution_id)
- `WS /ws/demo-output/{execution_id}` - Real-time output stream

✅ **WebSocket Messages**
- `connected` - Connection established
- `output` - Console output line
- `status` - Execution status change
- `error` - Error message
- `complete` - Execution finished with statistics

### Frontend (Vanilla JS + HTML/CSS)
✅ **Demo List Tab**
- Displays all 12 demos from backend
- Search functionality (filters by title/description)
- Filter by protocol dropdown (dynamically populated)
- Filter by complexity dropdown (BASIC, INTERMEDIATE, ADVANCED)
- Click to select demo and view details

✅ **Demo Details View**
- Shows demo title, protocol, complexity, description, expected outcome
- Displays configurable parameters with input fields
- "Run Demo" button to start execution

✅ **Execution Tab**
- Real-time console output display
- Auto-scrolling console
- Clear console button
- Call flow diagram panel (ready for SIP messages)
- Statistics cards: Total Attempts, Successful, Failed, Success Rate

✅ **Traffic Generator Tab**
- Configuration sliders (concurrent calls, total calls, ramp-up, failure rate)
- Conformance scenario selector
- Plotly.js chart for per-node throughput
- Live statistics display

✅ **History Tab**
- Structure ready (implementation in Phase 5)

## Testing Instructions

### 1. Start Backend
```powershell
cd C:\TestRepo\demo-web\backend
python run.py
```

Server should start at: http://localhost:8000  
API docs available at: http://localhost:8000/api/docs

### 2. Open Web Interface
Navigate to: http://localhost:8000

### 3. Test Demo List
✅ Verify 12 demos are displayed in left sidebar
✅ Test search: Type "VoLTE" - should filter to matching demos
✅ Test protocol filter: Select "SIP_IMS" - should show only SIP demos
✅ Test complexity filter: Select "ADVANCED" - should show only advanced demos
✅ Click a demo - details should appear on right panel
✅ Verify parameters are editable

### 4. Test Demo Execution (Simple Demo)
**Recommended**: Start with "sip-001" - Self-Contained VoLTE Call Setup

1. Click "sip-001" demo in list
2. View demo details on right
3. Keep default parameters (or adjust as needed)
4. Click "Run Demo" button
5. Should automatically switch to "Execution" tab
6. Watch console output appear in real-time
7. Statistics should update when execution completes

**Expected Console Output**:
```
>>> Status: starting
>>> Status: running
[JMeter output lines...]
>>> Status: completed
=== EXECUTION COMPLETE ===
Total Attempts: X
Successful: Y
Failed: Z
Success Rate: N%
```

### 5. Test API Directly (Optional)
```powershell
# Get all demos
curl http://localhost:8000/api/demos

# Get specific demo
curl http://localhost:8000/api/demos/sip-001

# Get protocols
curl http://localhost:8000/api/demos/protocols

# Execute demo (returns execution_id)
curl http://localhost:8000/api/execute -Method POST -ContentType "application/json" -Body '{"demo_id":"sip-001","parameters":{"threads":"1","loops":"1"}}'
```

## Known Limitations (Phase 2)

⚠️ **JMeter Must Be Installed**: Requires JMeter at C:\TTS\bin\jmeter.bat
⚠️ **JMX Files Must Exist**: Demo JMX files must be at specified paths
⚠️ **Call Flow Visualization**: Not implemented yet (Phase 3)
⚠️ **Traffic Generation**: UI ready, but full integration pending (Phase 4)
⚠️ **History**: Structure ready, implementation in Phase 5

## Troubleshooting

### Issue: Demos not loading
**Solution**: Check backend logs. Verify demos.json path in .env:
```
DEMO_CATALOG_PATH=../../demo-tool/src/main/resources/data/demos.json
```

### Issue: Demo execution fails immediately
**Solution**: Verify JMeter is installed at C:\TTS\bin\jmeter.bat
Check JMX file exists at the path specified in demo

### Issue: No console output during execution
**Solution**: Check browser console (F12) for WebSocket errors
Verify WebSocket connection in Network tab

### Issue: Statistics show 0/0/0
**Solution**: JTL file may not have been created or parsed correctly
Check backend logs for JTL parsing errors

## Next Steps - Phase 3 (Weeks 5-6)

1. **SIP Message Parsing**: Extract SIP messages from JTL file
2. **Mermaid.js Diagrams**: Render real-time call flow sequence diagrams
3. **RCA Demo**: Add Root Cause Analysis visualization
4. **Enhanced Statistics**: Add response time charts

## API Documentation

Full interactive API docs available at: http://localhost:8000/api/docs

## Files Modified in Phase 2

**Backend**:
- `backend/app/services/demo_service.py` - Demo catalog loading with filtering
- `backend/app/services/execution_service.py` - Complete JMeter execution engine
- `backend/app/websockets/demo_output.py` - WebSocket message broadcasting
- `backend/app/models/demo.py` - Updated to match JSON structure
- `backend/app/api/demos.py` - Added complexity-levels endpoint
- `backend/.env` - Configuration file

**Frontend**:
- `frontend/static/js/app.js` - Complete demo list, execution, WebSocket integration
- `frontend/templates/index.html` - Fixed complexity filter values

## Success Metrics

✅ Backend API responds to all endpoints  
✅ 12 demos loaded and displayed  
✅ Demo filtering works (search, protocol, complexity)  
✅ Demo execution launches JMeter  
✅ Real-time console output via WebSocket  
✅ Statistics parsed and displayed  
✅ Error handling throughout  

**Phase 2 is production-ready for internal testing!** 🎉
