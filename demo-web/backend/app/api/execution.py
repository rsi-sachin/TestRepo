"""
Demo Execution API Endpoints
Handles starting, stopping, and monitoring demo executions
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict
from app.models import ExecutionRequest, ExecutionResult, ExecutionStatus
from app.services.execution_service import ExecutionService
import uuid

router = APIRouter()
execution_service = ExecutionService()


@router.post("/execute", response_model=Dict[str, str])
async def start_execution(request: ExecutionRequest, background_tasks: BackgroundTasks):
    """
    Start demo execution
    
    Returns execution ID for tracking via WebSocket
    """
    execution_id = str(uuid.uuid4())
    
    # Start execution in background
    background_tasks.add_task(
        execution_service.execute_demo,
        execution_id,
        request.demo_id,
        request.parameters
    )
    
    return {
        "execution_id": execution_id,
        "status": "queued",
        "message": "Execution started. Connect to WebSocket for real-time updates."
    }


@router.get("/execute/{execution_id}/status", response_model=ExecutionResult)
async def get_execution_status(execution_id: str):
    """Get current status of an execution"""
    result = await execution_service.get_execution_result(execution_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    return result


@router.post("/execute/{execution_id}/cancel")
async def cancel_execution(execution_id: str):
    """Cancel a running execution"""
    success = await execution_service.cancel_execution(execution_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found or already completed")
    return {"message": "Execution cancelled"}


@router.get("/execute/active", response_model=Dict[str, ExecutionResult])
async def get_active_executions():
    """Get all currently active executions"""
    return await execution_service.get_active_executions()
