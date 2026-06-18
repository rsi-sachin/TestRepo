"""
Demo Catalog API Endpoints
Provides CRUD operations for demo scenarios
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models import Demo
from app.services.demo_service import DemoService

router = APIRouter()
demo_service = DemoService()


@router.get("/demos", response_model=List[Demo])
async def get_all_demos(
    protocol: Optional[str] = Query(None, description="Filter by protocol (SIP_IMS, DIAMETER, RADIUS)"),
    complexity: Optional[str] = Query(None, description="Filter by complexity (BASIC, INTERMEDIATE, ADVANCED)"),
    search: Optional[str] = Query(None, description="Search in title and description")
):
    """
    Get all available demo scenarios with optional filters
    """
    if protocol or complexity or search:
        return await demo_service.filter_demos(protocol=protocol, complexity=complexity, search=search)
    return await demo_service.get_all_demos()


@router.get("/demos/{demo_id}", response_model=Demo)
async def get_demo(demo_id: str):
    """Get a specific demo by ID"""
    demo = await demo_service.get_demo_by_id(demo_id)
    if not demo:
        raise HTTPException(status_code=404, detail=f"Demo {demo_id} not found")
    return demo


@router.get("/demos/protocols", response_model=List[str])
async def get_protocols():
    """Get list of available protocols"""
    return await demo_service.get_protocols()


@router.get("/demos/complexity-levels", response_model=List[str])
async def get_complexity_levels():
    """Get list of available complexity levels"""
    return await demo_service.get_complexity_levels()
