"""
ORAN API Endpoints
Handles O-RAN test catalog management, test generation, and execution
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, UploadFile, File, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pathlib import Path
import uuid
import json
from datetime import datetime

from app.models.a1_service import A1ServiceRegistryResponse
from app.models.oran import (
    OranTestCatalog,
    OranTestCase,
    OranExecutionResult,
    SpecType,
    MethodologyAnalysisResult,
    MethodologySectionResult,
    TestModuleCandidate,
    TestTitleCandidate,
)
from app.models.db_models import TestCase
from app.services.oran_execution_service import OranExecutionService
from app.services.spec_parser_service import SpecParserService
from app.services.catalog_generator_service import CatalogGeneratorService
from app.services.a1_service_registry import A1ServiceRegistry
from app.services.a1_policy_service import A1PolicyService
from app.services.a1_enrichment_service import A1EnrichmentInformationService
from app.services.rule_learner_service import RuleLearnerService
from app.repositories.rule_pack_repository import RulePackRepository
from app.models.rule_pack import RulePack, RulePackSummary
from app.models.hierarchy_tree import HierarchyTree
from app.database import get_db
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
oran_execution_service = OranExecutionService()
a1_service_registry = A1ServiceRegistry()
a1_policy_service = A1PolicyService(a1_service_registry)
a1_ei_service = A1EnrichmentInformationService(a1_service_registry)

# Initialize parser and catalog generator
specs_upload_dir = Path("./data/spec_uploads")
specs_upload_dir.mkdir(parents=True, exist_ok=True)

catalogs_dir = settings.oran_catalogs_path or (settings.runs_directory / "oran_catalogs")
spec_parser = SpecParserService(specs_upload_dir)
catalog_generator = CatalogGeneratorService(catalogs_dir)
rule_learner = RuleLearnerService()
rule_pack_repository = RulePackRepository()
from app.services.hierarchical_extractor_service import HierarchicalExtractorService
hierarchical_extractor = HierarchicalExtractorService()
sections_options_dir = Path("./data/oran_sections")
sections_options_dir.mkdir(parents=True, exist_ok=True)
sections_options_file = sections_options_dir / "sections_by_spec.json"

# TS spec metadata: canonical map used by resolve-specs endpoint
SPEC_METADATA = {
    "TS_103_989": {"ts_number": "TS 103 989", "title": "A1 Test Specification"},
    "TS_103_987": {"ts_number": "TS 103 987", "title": "A1 Application Protocol"},
    "TS_103_988": {"ts_number": "TS 103 988", "title": "A1 Type Definitions"},
    "TS_103_983": {"ts_number": "TS 103 983", "title": "A1 General Principles"},
}


@router.get("/services", response_model=A1ServiceRegistryResponse)
async def list_a1_services():
    """List supported A1 services and their role definitions."""
    return a1_service_registry.get_response()


@router.get("/services/{service_type}")
async def get_a1_service(service_type: str):
    """Return metadata for a single supported A1 service."""
    try:
        definition = a1_service_registry.get_service_definition(service_type)
        helper = a1_policy_service if definition.service_type.value == "A1-P" else a1_ei_service
        return {
            "service": definition.model_dump(mode="json"),
            "catalog_context": helper.get_catalog_context(),
            "summary": helper.build_service_summary(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _get_docs_path() -> Optional[Path]:
    """Return configured or default repository docs path."""
    if settings.oran_docs_path:
        return settings.oran_docs_path
    # Default: backend is at demo-web/backend/ → repo root is ../../  → ORAN/docs
    default = Path("../../ORAN/docs")
    return default if default.exists() else None


def _find_spec_in_docs(spec_type: str, docs_path: Path) -> Optional[Path]:
    """Case-insensitive prefix match: TS_103_989 → ts_103989*.pdf / *.docx."""
    prefix = spec_type.replace("TS_", "ts_").replace("_", "")
    for ext in [".pdf", ".docx"]:
        for candidate in docs_path.glob(f"*{ext}"):
            # normalise: remove underscores and lower-case
            if candidate.stem.lower().replace("_", "").startswith(prefix):
                return candidate
    return None


def _resolve_spec_file(spec_type: str) -> Optional[Path]:
    """Resolve a spec from uploads first, then repository docs fallback."""
    for ext in ('.pdf', '.docx'):
        candidate = specs_upload_dir / f"{spec_type}{ext}"
        if candidate.exists():
            return candidate

    docs_path = _get_docs_path()
    if docs_path:
        return _find_spec_in_docs(spec_type, docs_path)
    return None


def _save_sections_options(all_clauses: Dict[SpecType, List]) -> None:
    """Persist section options for Manage Tests dropdown/text input."""
    sections_by_spec: Dict[str, List[Dict[str, str]]] = {}

    for spec_type, clauses in all_clauses.items():
        options = []
        for clause in clauses:
            options.append({
                "section_number": clause.clause_number,
                "title": clause.title
            })

        # De-duplicate by section number while preserving first occurrence.
        seen = set()
        unique_options = []
        for option in options:
            section_number = option["section_number"]
            if section_number in seen:
                continue
            seen.add(section_number)
            unique_options.append(option)

        sections_by_spec[spec_type.value] = unique_options

    payload = {
        "generated_at": datetime.now().isoformat(),
        "sections_by_spec": sections_by_spec
    }

    with open(sections_options_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


@router.post("/extract-methodology", response_model=MethodologyAnalysisResult)
async def extract_methodology_plan(
    spec_type: str = Query(default="TS_103_989", description="Spec to analyze, e.g. TS_103_989"),
    service_type: str = Query(default="A1-P", description="A1 service to target"),
):
    """Extract methodology context and generate module/title candidates."""
    try:
        spec_file = _resolve_spec_file(spec_type)
        if spec_file is None:
            raise HTTPException(
                status_code=404,
                detail=f"Spec file for {spec_type} not found in uploads or repository docs",
            )

        service_definition = a1_service_registry.get_service_definition(service_type)
        analysis = spec_parser.extract_methodology_plan(spec_file, SpecType(spec_type))

        sections = [
            MethodologySectionResult(
                section_number=item.section_number,
                title=item.title,
                page_number=item.page_number,
                depth=item.depth,
                evidence=item.evidence,
            )
            for item in analysis['methodology_sections']
        ]
        modules = [
            TestModuleCandidate(
                module_name=item.module_name,
                module_id=item.module_id,
                source_section=item.source_section,
                source_title=item.source_title,
                confidence=item.confidence,
                evidence=item.evidence,
                keywords=item.keywords,
            )
            for item in analysis['modules']
        ]
        titles = [
            TestTitleCandidate(
                title=item.title,
                module_id=item.module_id,
                source_section=item.source_section,
                confidence=item.confidence,
                evidence=item.evidence,
            )
            for item in analysis['titles']
        ]

        return MethodologyAnalysisResult(
            spec_type=SpecType(spec_type),
            service_type=service_definition.service_type.value,
            spec_file=analysis['spec_file'],
            methodology_sections=sections,
            test_modules=modules,
            test_titles=titles,
            summary=analysis['summary'],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting methodology plan: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error extracting methodology plan: {str(e)}")


# ==================== CATALOG MANAGEMENT ====================

@router.get("/catalogs", response_model=List[OranTestCatalog])
async def get_all_catalogs(db: Session = Depends(get_db)):
    """
    Get all generated O-RAN test catalogs with actual test counts from database or JSON data
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
                    
                    # Calculate actual count from test_cases array
                    actual_test_count = len(catalog_data.get('test_cases', []))
                    catalog_data['total_tests'] = str(actual_test_count)
                    
                    catalog = OranTestCatalog(**catalog_data)
                    
                    # Prefer database count if available (Phase 3+)
                    db_count = db.query(TestCase).filter(
                        TestCase.catalog_id == catalog.catalog_id
                    ).count()
                    
                    if db_count > 0:
                        catalog.total_tests = str(db_count)
                    
                    catalogs.append(catalog)
            except Exception as e:
                logger.error(f"Error loading catalog {catalog_file}: {e}")
        
        return catalogs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading catalogs: {str(e)}")


@router.get("/catalogs/{catalog_id}", response_model=OranTestCatalog)
async def get_catalog(catalog_id: str, db: Session = Depends(get_db)):
    """Get a specific O-RAN test catalog by ID with actual test count from database or JSON data"""
    try:
        catalogs_dir = settings.oran_catalogs_path or (settings.runs_directory / "oran_catalogs")
        catalog_file = catalogs_dir / f"{catalog_id}.json"
        
        if not catalog_file.exists():
            raise HTTPException(status_code=404, detail=f"Catalog {catalog_id} not found")
        
        import json
        with open(catalog_file, 'r') as f:
            catalog_data = json.load(f)
            
            # Calculate actual count from test_cases array
            actual_test_count = len(catalog_data.get('test_cases', []))
            catalog_data['total_tests'] = str(actual_test_count)
            
            catalog = OranTestCatalog(**catalog_data)
            
            # Prefer database count if available (Phase 3+)
            db_count = db.query(TestCase).filter(
                TestCase.catalog_id == catalog_id
            ).count()
            
            if db_count > 0:
                catalog.total_tests = str(db_count)
            
            return catalog
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading catalog: {str(e)}")


@router.delete("/catalogs/{catalog_id}")
async def delete_catalog(catalog_id: str, db: Session = Depends(get_db)):
    """Delete a catalog JSON file and its associated test cases."""
    try:
        catalogs_dir = settings.oran_catalogs_path or (settings.runs_directory / "oran_catalogs")
        catalog_file = catalogs_dir / f"{catalog_id}.json"

        deleted_rows = db.query(TestCase).filter(TestCase.catalog_id == catalog_id).delete(synchronize_session=False)
        db.commit()

        file_deleted = False
        if catalog_file.exists():
            catalog_file.unlink()
            file_deleted = True

        if deleted_rows == 0 and not file_deleted:
            raise HTTPException(status_code=404, detail=f"Catalog {catalog_id} not found")

        return {
            "status": "deleted",
            "catalog_id": catalog_id,
            "database_rows_deleted": deleted_rows,
            "catalog_file_deleted": file_deleted,
            "message": f"Catalog {catalog_id} deleted successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting catalog: {str(e)}")


@router.get("/catalogs/{catalog_id}/tests", response_model=List[OranTestCase])
async def get_catalog_tests(catalog_id: str):
    """Get all test cases from a specific catalog"""
    catalog = await get_catalog(catalog_id)
    return catalog.test_cases


@router.get("/resolve-specs")
async def resolve_specs(selected: Optional[List[str]] = Query(default=None)):
    """
    For each selected spec type, check whether the file exists in the
    repository docs folder and return resolution status.
    Frontend calls this when the user changes spec checkboxes.
    """
    if selected is None:
        selected = list(SPEC_METADATA.keys())

    docs_path = _get_docs_path()
    results = []

    for spec_type in selected:
        meta = SPEC_METADATA.get(spec_type, {})
        found_path: Optional[Path] = None

        if docs_path:
            found_path = _find_spec_in_docs(spec_type, docs_path)

        results.append({
            "spec_type": spec_type,
            "ts_number": meta.get("ts_number", spec_type),
            "title": meta.get("title", ""),
            "status": "auto" if found_path else "missing",
            "filename": found_path.name if found_path else None,
        })

    return {"specs": results, "docs_folder_available": docs_path is not None}


@router.get("/sections/options")
async def get_section_options():
    """Get section options used by Manage Tests source spec/section filters."""
    if not sections_options_file.exists():
        return {
            "generated_at": None,
            "sections_by_spec": {}
        }

    try:
        with open(sections_options_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load section options: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load section options: {str(e)}")


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
    description: Optional[str] = Query("", description="Catalog description"),
    service_type: str = Query(default="A1-P", description="A1 service to generate for"),
    db: Session = Depends(get_db)
):
    """
    Generate O-RAN test catalog from uploaded specifications
    
    Parses PDF/DOCX specs, extracts test clauses, cross-references, and generates catalog
    Saves test cases to database for Phase 3 UI
    """
    try:
        logger.info(f"Starting catalog generation: {catalog_name}")
        service_definition = a1_service_registry.get_service_definition(service_type)
        
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
        
        # Parse all specifications once without limit for section options JSON.
        all_sections_clauses = spec_parser.parse_all_specs(spec_files, max_tests_per_spec=None)
        _save_sections_options(all_sections_clauses)

        # Parse all specifications with MVP limit
        max_tests_per_spec = settings.max_tests_per_spec
        all_clauses = spec_parser.parse_all_specs(spec_files, max_tests_per_spec)
        total_clauses = sum(len(clauses) for clauses in all_clauses.values())
        logger.info(f"Extracted {total_clauses} total test clauses (MVP limit: {max_tests_per_spec} per spec)")
        
        # Cross-reference specs for enrichment
        enriched_cases = spec_parser.cross_reference_specs(all_clauses)
        logger.info(f"Created {len(enriched_cases)} enriched test cases")
        
        # Generate catalog (with section limit) - returns catalog and deduplicated cases
        catalog, deduplicated_cases = catalog_generator.generate_catalog(
            enriched_cases,
            catalog_name,
            description,
            apply_section_limit=True,  # MVP constraint: 1 test per section
            service_type=service_definition.service_type.value,
            service_name=service_definition.name,
        )
        
        # Save catalog JSON
        catalog_path = catalog_generator.save_catalog(catalog)
        logger.info(f"Saved catalog to {catalog_path}")
        
        # Save test cases to database (Phase 3) - use deduplicated list
        try:
            saved_count = catalog_generator.save_to_database(
                deduplicated_cases,  # Use deduplicated list from catalog generation
                catalog.catalog_id,
                db
            )
            logger.info(f"Saved {saved_count} test cases to database")
        except Exception as e:
            logger.error(f"Failed to save to database: {e}", exc_info=True)
            # Continue even if database save fails - catalog JSON is still saved
        
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
            "conflicts_detected": str(len(conflicts)),
            "service_type": service_definition.service_type.value,
            "service_name": service_definition.name,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating catalog: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating catalog: {str(e)}")


@router.post("/preview-sections")
async def preview_sections():
    """
    Preview test sections from uploaded specifications without generating catalog.
    Returns all available sections with metadata for user selection.
    """
    try:
        logger.info("Previewing test sections from uploaded specs")
        
        # Map uploaded files to SpecType
        spec_files = {}
        for spec_type in [SpecType.TS_103_989, SpecType.TS_103_987, 
                          SpecType.TS_103_988, SpecType.TS_103_983]:
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
        
        # Parse all specifications WITHOUT limit to show all available sections
        all_clauses = spec_parser.parse_all_specs(spec_files, max_tests_per_spec=None)
        
        # Format sections for UI display
        sections_by_spec = {}
        for spec_type, clauses in all_clauses.items():
            sections_by_spec[spec_type.value] = [
                {
                    "section_number": clause.clause_number,
                    "title": clause.title,
                    "page": clause.page_number,
                    "complexity": "BASIC" if len(clause.description or "") < 200 else "INTERMEDIATE",
                    "description_preview": (clause.description or clause.title)[:150] + "..."
                }
                for clause in clauses
            ]
        
        total_sections = sum(len(sections) for sections in sections_by_spec.values())
        
        return {
            "status": "success",
            "total_sections": total_sections,
            "sections_by_spec": sections_by_spec,
            "message": f"Found {total_sections} available test sections across {len(spec_files)} specifications"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing sections: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error previewing sections: {str(e)}")


@router.post("/generate-from-selection")
async def generate_from_selection(
    selected_sections: Dict[str, List[str]],
    catalog_name: str = Query(..., description="Name for the generated catalog"),
    description: Optional[str] = Query("", description="Catalog description"),
    service_type: str = Query(default="A1-P", description="A1 service to generate for"),
    db: Session = Depends(get_db)
):
    """
    Generate test catalog from user-selected sections.
    
    Args:
        selected_sections: Dict mapping spec_type to list of section numbers
                          e.g., {"TS_103_989": ["5.2.6.2.1", "5.3.1"], ...}
        catalog_name: Name for the catalog
        description: Optional description
        db: Database session
    """
    try:
        logger.info(f"Generating catalog from selected sections: {catalog_name}")
        service_definition = a1_service_registry.get_service_definition(service_type)
        
        # Map uploaded files to SpecType
        spec_files = {}
        for spec_type in [SpecType.TS_103_989, SpecType.TS_103_987, 
                          SpecType.TS_103_988, SpecType.TS_103_983]:
            pdf_path = specs_upload_dir / f"{spec_type.value}.pdf"
            docx_path = specs_upload_dir / f"{spec_type.value}.docx"
            
            if pdf_path.exists():
                spec_files[spec_type] = pdf_path
            elif docx_path.exists():
                spec_files[spec_type] = docx_path
        
        if not spec_files:
            raise HTTPException(
                status_code=400,
                detail="No specification files found. Upload specs first"
            )
        
        # Parse all specifications without limit
        all_clauses = spec_parser.parse_all_specs(spec_files, max_tests_per_spec=None)
        _save_sections_options(all_clauses)
        
        # Filter clauses to only include selected sections
        filtered_clauses = {}
        for spec_type, clauses in all_clauses.items():
            spec_key = spec_type.value
            if spec_key in selected_sections:
                selected_nums = set(selected_sections[spec_key])
                filtered_clauses[spec_type] = [
                    clause for clause in clauses 
                    if clause.clause_number in selected_nums
                ]
            else:
                filtered_clauses[spec_type] = []
        
        total_selected = sum(len(clauses) for clauses in filtered_clauses.values())
        logger.info(f"Processing {total_selected} selected test clauses")
        
        # Cross-reference specs for enrichment
        enriched_cases = spec_parser.cross_reference_specs(filtered_clauses)
        logger.info(f"Created {len(enriched_cases)} enriched test cases")
        
        # Generate catalog WITHOUT section limit (user already selected)
        catalog, deduplicated_cases = catalog_generator.generate_catalog(
            enriched_cases,
            catalog_name,
            description,
            apply_section_limit=False,  # Don't apply limit - user made selection
            service_type=service_definition.service_type.value,
            service_name=service_definition.name,
        )
        
        # Save catalog JSON
        catalog_path = catalog_generator.save_catalog(catalog)
        logger.info(f"Saved catalog to {catalog_path}")
        
        # Save test cases to database
        try:
            saved_count = catalog_generator.save_to_database(
                deduplicated_cases,
                catalog.catalog_id,
                db
            )
            logger.info(f"Saved {saved_count} test cases to database")
        except Exception as e:
            logger.error(f"Failed to save to database: {e}", exc_info=True)
        
        return {
            "catalog_id": catalog.catalog_id,
            "status": "completed",
            "message": f"Successfully generated catalog with {catalog.total_tests} test cases from selected sections",
            "total_tests": str(catalog.total_tests),
            "total_selected_sections": str(total_selected),
            "service_type": service_definition.service_type.value,
            "service_name": service_definition.name,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating catalog from selection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating catalog: {str(e)}")


@router.post("/upload-specs")
async def upload_specifications(
    request: Request,
    service_type: str = Query(default="A1-P", description="A1 service to upload for"),
    ts_103_989: Optional[UploadFile] = File(None, description="TS 103 989 - A1 Test Specification"),
    ts_103_987: Optional[UploadFile] = File(None, description="TS 103 987 - A1 Application Protocol"),
    ts_103_988: Optional[UploadFile] = File(None, description="TS 103 988 - A1 Type Definitions"),
    ts_103_983: Optional[UploadFile] = File(None, description="TS 103 983 - A1 General Principles"),
):
    """
    Upload / auto-resolve ETSI specification files for test generation.

    For each selected spec:
      1. If a file is provided by the user → save it to spec_uploads/.
      2. Else → attempt to auto-bind from the repository docs folder.
    Returns per-spec resolution status for the frontend to render.
    """
    try:
        service_definition = a1_service_registry.get_service_definition(service_type)
        # Parse selected_specs from form data (list of spec type strings)
        form = await request.form()
        selected_specs_raw = form.getlist("selected_specs")
        selected_specs = selected_specs_raw if selected_specs_raw else list(SPEC_META.keys())

        uploaded_specs = {}
        resolution = {}

        for spec_file, spec_type_str in [
            (ts_103_989, "TS_103_989"),
            (ts_103_987, "TS_103_987"),
            (ts_103_988, "TS_103_988"),
            (ts_103_983, "TS_103_983"),
        ]:
            if spec_type_str not in selected_specs:
                continue  # Skip non-selected specs

            if spec_file:
                # Manual upload path
                file_ext = Path(spec_file.filename).suffix
                file_path = specs_upload_dir / f"{spec_type_str}{file_ext}"
                with open(file_path, "wb") as f:
                    content = await spec_file.read()
                    f.write(content)
                uploaded_specs[spec_type_str] = str(file_path)
                resolution[spec_type_str] = {"source": "manual", "filename": file_path.name}
                logger.info(f"Manually uploaded {spec_type_str}: {file_path}")
            else:
                # Auto-bind from docs folder
                docs_path = _get_docs_path()
                found = _find_spec_in_docs(spec_type_str, docs_path) if docs_path else None
                if found:
                    # Symlink or copy into upload dir so downstream services see it
                    dest = specs_upload_dir / f"{spec_type_str}{found.suffix}"
                    if not dest.exists() or dest.stat().st_mtime < found.stat().st_mtime:
                        import shutil
                        shutil.copy2(found, dest)
                    uploaded_specs[spec_type_str] = str(dest)
                    resolution[spec_type_str] = {"source": "docs_folder", "filename": found.name}
                    logger.info(f"Auto-bound {spec_type_str} from docs: {found}")
                else:
                    resolution[spec_type_str] = {"source": "missing", "filename": None}
                    logger.warning(f"Spec {spec_type_str} not found in docs and not uploaded")

        missing = [k for k, v in resolution.items() if v["source"] == "missing"]
        resolved = len(uploaded_specs)

        return {
            "message": f"Resolved {resolved}/{len(selected_specs)} specification(s)",
            "specs": uploaded_specs,
            "resolution": resolution,
            "missing": missing,
            "status": "ready" if not missing else "partial",
            "service_type": service_definition.service_type.value,
            "service_name": service_definition.name,
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


# ==================== RULE PACK MANAGEMENT ====================

@router.get("/rules", response_model=List[RulePackSummary])
async def list_rule_packs(document_type: Optional[str] = None):
    """
    List all available rule packs
    
    Args:
        document_type: Optional filter by document type (e.g., TEST_SPECIFICATION)
    
    Returns:
        List of rule pack summaries
    """
    try:
        logger.info(f"Listing rule packs (filter: {document_type})")
        summaries = rule_pack_repository.list_rule_packs(document_type=document_type)
        return summaries
    except Exception as e:
        logger.error(f"Error listing rule packs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list rule packs: {str(e)}")


@router.get("/rules/{rule_pack_id}", response_model=RulePack)
async def get_rule_pack(rule_pack_id: str):
    """
    Get specific rule pack details
    
    Args:
        rule_pack_id: Rule pack identifier
    
    Returns:
        Full RulePack object
    """
    try:
        logger.info(f"Fetching rule pack: {rule_pack_id}")
        rule_pack = rule_pack_repository.load_rule_pack(rule_pack_id)
        
        if not rule_pack:
            raise HTTPException(status_code=404, detail=f"Rule pack not found: {rule_pack_id}")
        
        return rule_pack
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching rule pack: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch rule pack: {str(e)}")


@router.post("/rules/learn")
async def learn_rules_from_document(
    spec_type: str,
    max_depth: int = 4
):
    """
    Learn extraction rules from a document
    
    Args:
        spec_type: Specification type (e.g., TS_103_989)
        max_depth: Maximum hierarchy depth to extract
    
    Returns:
        Created rule pack information
    """
    try:
        logger.info(f"Learning rules from {spec_type} (max_depth={max_depth})")
        
        # Resolve spec file
        spec_path = _resolve_spec_file(spec_type)
        if not spec_path:
            raise HTTPException(status_code=404, detail=f"Specification file not found: {spec_type}")
        
        # Learn rules
        from app.services.document_classifier_service import DocumentType
        rule_pack = rule_learner.learn_from_document(
            pdf_path=spec_path,
            doc_type=DocumentType.TEST_SPECIFICATION,
            max_depth=max_depth
        )
        
        # Save rule pack
        success = rule_pack_repository.save_rule_pack(rule_pack)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save rule pack")
        
        logger.info(f"Created rule pack: {rule_pack.id}")
        
        return {
            "rule_pack_id": rule_pack.id,
            "name": rule_pack.name,
            "document_type": rule_pack.document_type,
            "max_depth": rule_pack.hierarchy_config.max_depth,
            "extraction_rules_count": len(rule_pack.extraction_rules),
            "message": "Rule pack created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error learning rules: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to learn rules: {str(e)}")


@router.post("/rules/{rule_pack_id}/apply")
async def apply_rule_pack(
    rule_pack_id: str,
    spec_type: str
):
    """
    Apply a rule pack to extract hierarchy from a document
    
    Args:
        rule_pack_id: Rule pack to apply
        spec_type: Specification to process
    
    Returns:
        Extraction results with hierarchy
    """
    try:
        logger.info(f"Applying rule pack {rule_pack_id} to {spec_type}")
        
        # Load rule pack
        rule_pack = rule_pack_repository.load_rule_pack(rule_pack_id)
        if not rule_pack:
            raise HTTPException(status_code=404, detail=f"Rule pack not found: {rule_pack_id}")
        
        # Resolve spec file
        spec_path = _resolve_spec_file(spec_type)
        if not spec_path:
            raise HTTPException(status_code=404, detail=f"Specification file not found: {spec_type}")
        
        # Directly apply the rule pack (bypass fingerprint matching)
        logger.info(f"Directly applying rule pack: {rule_pack.name}")
        hierarchy_tree = hierarchical_extractor.extract_hierarchy(
            pdf_path=spec_path,
            rule_pack=rule_pack
        )
        
        # Calculate quality score
        quality_score = 0.0
        if hierarchy_tree and hierarchy_tree.total_nodes > 0:
            quality_score = min(1.0, hierarchy_tree.avg_confidence)
            # Update rule pack statistics
            rule_pack.update_statistics(success=True, quality_score=quality_score)
            rule_pack_repository.update_rule_pack(rule_pack)
        
        avg_confidence = hierarchy_tree.avg_confidence if hierarchy_tree else 0.0
        
        return {
            "rule_pack_id": rule_pack_id,
            "spec_type": spec_type,
            "extraction_method": "rule_based",
            "quality_score": quality_score,
            "hierarchy_tree_id": hierarchy_tree.tree_id if hierarchy_tree else None,
            "total_nodes": hierarchy_tree.total_nodes if hierarchy_tree else 0,
            "avg_confidence": avg_confidence,
            "message": "Rule pack applied successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying rule pack: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply rule pack: {str(e)}")


@router.delete("/rules/{rule_pack_id}")
async def delete_rule_pack(rule_pack_id: str):
    """
    Delete a rule pack
    
    Args:
        rule_pack_id: Rule pack to delete
    
    Returns:
        Success message
    """
    try:
        logger.info(f"Deleting rule pack: {rule_pack_id}")
        
        success = rule_pack_repository.delete_rule_pack(rule_pack_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Rule pack not found: {rule_pack_id}")
        
        return {
            "rule_pack_id": rule_pack_id,
            "message": "Rule pack deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rule pack: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete rule pack: {str(e)}")


# ==================== HIERARCHY VISUALIZATION ====================

@router.get("/hierarchy/{document_hash}")
async def get_hierarchy(document_hash: str):
    """
    Get extracted hierarchy tree for a document
    
    Args:
        document_hash: Document hash identifier
    
    Returns:
        Hierarchy tree structure
    """
    try:
        logger.info(f"Fetching hierarchy for document: {document_hash}")
        
        # Try to load cached hierarchy
        hierarchy_file = Path(f"./data/oran_learning/extractions/{document_hash}.json")
        
        if not hierarchy_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Hierarchy not found for document: {document_hash}"
            )
        
        with open(hierarchy_file, 'r', encoding='utf-8') as f:
            hierarchy_data = json.load(f)
        
        return hierarchy_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching hierarchy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch hierarchy: {str(e)}")


@router.post("/hierarchy/extract")
async def extract_hierarchy(
    spec_type: str,
    use_rules: bool = True
):
    """
    Extract hierarchical structure from a document
    
    Args:
        spec_type: Specification type (e.g., TS_103_989)
        use_rules: Whether to use rule-based extraction (default: True)
    
    Returns:
        Extracted hierarchy with metadata
    """
    try:
        logger.info(f"Extracting hierarchy from {spec_type} (use_rules={use_rules})")
        
        # Resolve spec file
        spec_path = _resolve_spec_file(spec_type)
        if not spec_path:
            raise HTTPException(status_code=404, detail=f"Specification file not found: {spec_type}")
        
        # Extract hierarchy
        result = spec_parser.extract_hierarchy_with_rules(
            file_path=spec_path,
            spec_type=SpecType(spec_type) if hasattr(SpecType, spec_type) else None,
            force_heuristic=not use_rules
        )
        
        # If hierarchy tree exists, save it for future retrieval
        if result['hierarchy_tree']:
            tree = result['hierarchy_tree']
            hierarchy_dir = Path("./data/oran_learning/extractions")
            hierarchy_dir.mkdir(parents=True, exist_ok=True)
            hierarchy_file = hierarchy_dir / f"{tree.document_hash}.json"
            
            with open(hierarchy_file, 'w', encoding='utf-8') as f:
                json.dump(tree.to_dict(), f, indent=2, default=str)
            
            logger.info(f"Saved hierarchy to {hierarchy_file}")
        
        # Return summary
        return {
            "spec_type": spec_type,
            "extraction_method": result['extraction_method'],
            "document_hash": result['hierarchy_tree'].document_hash if result['hierarchy_tree'] else None,
            "quality_score": result['quality_score'],
            "total_nodes": result['hierarchy_tree'].total_nodes if result['hierarchy_tree'] else 0,
            "max_depth": result['hierarchy_tree'].max_depth if result['hierarchy_tree'] else 0,
            "avg_confidence": result['hierarchy_tree'].avg_confidence if result['hierarchy_tree'] else 0.0,
            "fallback_used": result['fallback_used'],
            "hierarchy_tree": result['hierarchy_tree'].to_dict() if result['hierarchy_tree'] else None,
            "message": "Hierarchy extracted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting hierarchy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract hierarchy: {str(e)}")
