"""
ORAN API Endpoints
Handles O-RAN test catalog management, test generation, and execution
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, UploadFile, File
from typing import List, Dict, Optional
from pathlib import Path
import uuid
from datetime import datetime

from app.models.oran import (
    OranTestCatalog,
    OranTestCase,
    OranExecutionResult,
    SpecType
)
from app.services.oran_execution_service import OranExecutionService
from app.services.spec_parser_service import SpecParserService
from app.services.catalog_generator_service import CatalogGeneratorService
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
oran_execution_service = OranExecutionService()

# Initialize parser and catalog generator
specs_upload_dir = Path("./data/spec_uploads")
specs_upload_dir.mkdir(parents=True, exist_ok=True)

catalogs_dir = settings.oran_catalogs_path or (settings.runs_directory / "oran_catalogs")
spec_parser = SpecParserService(specs_upload_dir)
catalog_generator = CatalogGeneratorService(catalogs_dir)


# ==================== CATALOG MANAGEMENT ====================

@router.get("/catalogs", response_model=List[OranTestCatalog])
async def get_all_catalogs():
    """
    Get all generated O-RAN test catalogs
    """
    try:
        catalogs_dir = settings.oran_catalogs_path or (settings.runs_directory / "oran_catalogs")
        catalogs_dir.mkdir(parents=True, exist_ok=True)
        
        catalogs = []
        for catalog_file in catalogs_dir.glob("*.json"):
            try:
                import json
                with open(catalog_file, 'r') as f:
                    catalog_data = json.load(f)
                    catalogs.append(OranTestCatalog(**catalog_data))
            except Exception as e:
                print(f"Error loading catalog {catalog_file}: {e}")
        
        return catalogs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading catalogs: {str(e)}")


@router.get("/catalogs/{catalog_id}", response_model=OranTestCatalog)
async def get_catalog(catalog_id: str):
    """Get a specific O-RAN test catalog by ID"""
    try:
        catalogs_dir = settings.oran_catalogs_path or (settings.runs_directory / "oran_catalogs")
        catalog_file = catalogs_dir / f"{catalog_id}.json"
        
        if not catalog_file.exists():
            raise HTTPException(status_code=404, detail=f"Catalog {catalog_id} not found")
        
        import json
        with open(catalog_file, 'r') as f:
            catalog_data = json.load(f)
            return OranTestCatalog(**catalog_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading catalog: {str(e)}")


@router.get("/catalogs/{catalog_id}/tests", response_model=List[OranTestCase])
async def get_catalog_tests(catalog_id: str):
    """Get all test cases from a specific catalog"""
    catalog = await get_catalog(catalog_id)
    return catalog.test_cases


# ==================== SCRIPT VIEWING ====================

@router.get("/scripts/{test_id}")
async def get_test_script(test_id: str):
    """
    View generated pytest script for a test case
    
    Returns the Python script as plain text
    """
    try:
        scripts_dir = settings.oran_generated_tests_path or (settings.tts_path / "generated_tests")
        script_file = scripts_dir / f"{test_id}.py"
        
        if not script_file.exists():
            raise HTTPException(status_code=404, detail=f"Script for test {test_id} not found")
        
        with open(script_file, 'r') as f:
            script_content = f.read()
        
        return {
            "test_id": test_id,
            "script_path": str(script_file),
            "content": script_content,
            "language": "python"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading script: {str(e)}")


@router.get("/scripts/{test_id}/download")
async def download_test_script(test_id: str):
    """
    Download generated pytest script
    
    Returns file for download
    """
    from fastapi.responses import FileResponse
    
    try:
        scripts_dir = settings.oran_generated_tests_path or (settings.tts_path / "generated_tests")
        script_file = scripts_dir / f"{test_id}.py"
        
        if not script_file.exists():
            raise HTTPException(status_code=404, detail=f"Script for test {test_id} not found")
        
        return FileResponse(
            path=script_file,
            filename=f"{test_id}.py",
            media_type="text/x-python"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading script: {str(e)}")


# ==================== TEST GENERATION ====================

@router.post("/generate", response_model=Dict[str, str])
async def generate_test_catalog(
    catalog_name: str = Query(..., description="Name for the generated catalog"),
    description: Optional[str] = Query("", description="Catalog description")
):
    """
    Generate O-RAN test catalog from uploaded specifications
    
    Parses PDF/DOCX specs, extracts test clauses, cross-references, and generates catalog
    """
    try:
        logger.info(f"Starting catalog generation: {catalog_name}")
        
        # Map uploaded files to SpecType
        spec_files = {}
        for spec_type in [SpecType.TS_103_989, SpecType.TS_103_987, 
                          SpecType.TS_103_988, SpecType.TS_103_983]:
            # Check for both .pdf and .docx
            pdf_path = specs_upload_dir / f"{spec_type.value}.pdf"
            docx_path = specs_upload_dir / f"{spec_type.value}.docx"
            
            if pdf_path.exists():
                spec_files[spec_type] = pdf_path
            elif docx_path.exists():
                spec_files[spec_type] = docx_path
        
        if not spec_files:
            raise HTTPException(
                status_code=400,
                detail="No specification files found. Upload specs first using /upload-specs"
            )
        
        logger.info(f"Found {len(spec_files)} specification files")
        
        # Parse all specifications
        all_clauses = spec_parser.parse_all_specs(spec_files)
        total_clauses = sum(len(clauses) for clauses in all_clauses.values())
        logger.info(f"Extracted {total_clauses} total test clauses")
        
        # Cross-reference specs for enrichment
        enriched_cases = spec_parser.cross_reference_specs(all_clauses)
        logger.info(f"Created {len(enriched_cases)} enriched test cases")
        
        # Generate catalog (with section limit)
        catalog = catalog_generator.generate_catalog(
            enriched_cases,
            catalog_name,
            description,
            apply_section_limit=True  # MVP constraint: 1 test per section
        )
        
        # Save catalog
        catalog_path = catalog_generator.save_catalog(catalog)
        logger.info(f"Saved catalog to {catalog_path}")
        
        # Save conflicts if any
        conflicts = spec_parser.detect_conflicts(enriched_cases)
        if conflicts:
            conflicts_path = catalogs_dir / "spec_conflicts.json"
            spec_parser.save_conflicts(conflicts_path)
            logger.info(f"Saved {len(conflicts)} conflicts")
        
        return {
            "catalog_id": catalog.catalog_id,
            "status": "completed",
            "message": f"Successfully generated catalog with {catalog.total_tests} test cases",
            "total_tests": str(catalog.total_tests),
            "total_clauses_parsed": str(total_clauses),
            "conflicts_detected": str(len(conflicts))
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating catalog: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating catalog: {str(e)}")


@router.post("/upload-specs")
async def upload_specifications(
    ts_103_989: Optional[UploadFile] = File(None, description="TS 103 989 - A1 Test Specification"),
    ts_103_987: Optional[UploadFile] = File(None, description="TS 103 987 - A1 Application Protocol"),
    ts_103_988: Optional[UploadFile] = File(None, description="TS 103 988 - A1 Type Definitions"),
    ts_103_983: Optional[UploadFile] = File(None, description="TS 103 983 - A1 General Principles")
):
    """
    Upload ETSI specification files for test generation
    
    Saves uploaded PDF/DOCX files to spec_uploads directory
    """
    try:
        uploaded_specs = {}
        
        for spec_file, spec_type_str in [
            (ts_103_989, "TS_103_989"),
            (ts_103_987, "TS_103_987"),
            (ts_103_988, "TS_103_988"),
            (ts_103_983, "TS_103_983")
        ]:
            if spec_file:
                # Save file with spec type name
                file_ext = Path(spec_file.filename).suffix
                file_path = specs_upload_dir / f"{spec_type_str}{file_ext}"
                
                # Save uploaded file
                with open(file_path, 'wb') as f:
                    content = await spec_file.read()
                    f.write(content)
                
                uploaded_specs[spec_type_str] = str(file_path)
                logger.info(f"Uploaded {spec_type_str}: {file_path}")
        
        return {
            "message": f"Successfully uploaded {len(uploaded_specs)} specification file(s)",
            "specs": uploaded_specs,
            "status": "ready"
        }
    
    except Exception as e:
        logger.error(f"Error uploading specs: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading specifications: {str(e)}")


# ==================== TEST EXECUTION ====================

@router.post("/execute", response_model=Dict[str, str])
async def execute_oran_test(
    test_id: str = Query(..., description="Test ID to execute"),
    catalog_id: Optional[str] = Query(None, description="Catalog ID"),
    config: Optional[Dict[str, str]] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Execute an O-RAN test
    
    Returns execution ID for tracking via WebSocket
    """
    execution_id = str(uuid.uuid4())
    
    # Start execution in background
    background_tasks.add_task(
        oran_execution_service.execute_oran_test,
        execution_id,
        test_id,
        catalog_id,
        config or {}
    )
    
    return {
        "execution_id": execution_id,
        "status": "queued",
        "test_id": test_id,
        "message": "Execution started. Connect to WebSocket for real-time updates."
    }


@router.get("/execute/{execution_id}/status", response_model=OranExecutionResult)
async def get_oran_execution_status(execution_id: str):
    """Get current status of an O-RAN test execution"""
    result = await oran_execution_service.get_oran_execution_result(execution_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    return result


@router.post("/execute/{execution_id}/cancel")
async def cancel_oran_execution(execution_id: str):
    """Cancel a running O-RAN test execution"""
    success = await oran_execution_service.cancel_execution(execution_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found or already completed")
    return {"message": "Execution cancelled"}


@router.get("/execute/active")
async def get_active_oran_executions():
    """Get all currently active O-RAN test executions"""
    return await oran_execution_service.list_active_oran_executions()


# ==================== STATISTICS & HISTORY ====================

@router.get("/statistics")
async def get_oran_statistics():
    """
    Get overall O-RAN testing statistics
    
    Returns aggregated stats across all catalogs and executions
    """
    try:
        catalogs = await get_all_catalogs()
        
        total_catalogs = len(catalogs)
        total_tests = sum(c.total_tests for c in catalogs)
        
        # Get execution history stats (placeholder for Phase 4)
        total_executions = len(oran_execution_service.oran_executions)
        
        return {
            "total_catalogs": total_catalogs,
            "total_test_cases": total_tests,
            "total_executions": total_executions,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating statistics: {str(e)}")


# ==================== CONFIGURATION ====================

@router.get("/config")
async def get_oran_config():
    """Get current O-RAN configuration"""
    return {
        "oran_install_path": str(getattr(settings, 'oran_install_path', 'Not configured')),
        "oran_ric_endpoint": getattr(settings, 'oran_ric_endpoint', 'Not configured'),
        "catalogs_path": str(settings.oran_catalogs_path or (settings.runs_directory / "oran_catalogs")),
        "generated_tests_path": str(settings.oran_generated_tests_path or (settings.tts_path / "generated_tests")),
        "pytest_available": True  # TODO: Check if pytest is installed
    }
