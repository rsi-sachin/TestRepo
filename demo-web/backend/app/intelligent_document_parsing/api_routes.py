"""
FastAPI routes for Intelligent Document Parsing API.

Provides HTTP endpoints for document analysis, rule management, and feedback.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from pathlib import Path
import logging
from typing import Optional

from app.intelligent_document_parsing import DocumentAnalysisService
from app.intelligent_document_parsing.core import ExtractionRule
from app.intelligent_document_parsing.services import UserFeedback

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/document-analysis", tags=["document-analysis"])

# Initialize service (in production, use dependency injection)
_service = None

def get_service() -> DocumentAnalysisService:
    """Get or initialize the document analysis service."""
    global _service
    if _service is None:
        _service = DocumentAnalysisService()
    return _service


@router.post("/section")
async def analyze_section(
    pdf_path: str = Query(..., description="Path to PDF file"),
    section_number: str = Query(..., description="Section number (e.g., '4.1')"),
    subsection_depth: int = Query(1, description="Subsection depth to extract")
):
    """
    Analyze a specific section of a PDF document.
    
    Returns decisions, action items, and information gaps in JSON format.
    """
    try:
        service = get_service()
        result = service.analyze_section(
            pdf_path=Path(pdf_path),
            section_number=section_number,
            subsection_depth=subsection_depth
        )
        return JSONResponse(content=result.to_json())
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"PDF file not found: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid section: {str(e)}")
    except Exception as e:
        logger.error(f"Error analyzing section: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/document")
async def analyze_document(
    pdf_path: str = Query(..., description="Path to PDF file")
):
    """
    Analyze entire PDF document.
    
    Extracts all decisions, actions, and gaps from the full document.
    """
    try:
        service = get_service()
        result = service.analyze_document(Path(pdf_path))
        return JSONResponse(content=result.to_json())
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"PDF file not found: {str(e)}")
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/rules")
async def add_extraction_rule(
    rule_id: str = Query(..., description="Unique rule ID"),
    rule_name: str = Query(..., description="Human-readable rule name"),
    rule_type: str = Query(..., description="Rule type: decision|action|gap"),
    pattern: str = Query(..., description="Regex pattern for extraction"),
    confidence_boost: float = Query(0.2, description="Confidence boost (0.0-1.0)")
):
    """
    Add a custom extraction rule.
    
    Allows fine-tuning extraction for specific documents or domains.
    """
    try:
        if rule_type not in ["decision", "action", "gap"]:
            raise ValueError(f"Invalid rule_type: {rule_type}")
        
        service = get_service()
        rule = ExtractionRule(
            id=rule_id,
            name=rule_name,
            rule_type=rule_type,
            pattern=pattern,
            confidence_boost=confidence_boost
        )
        service.add_custom_extraction_rule(rule)
        
        return {
            "status": "success",
            "message": f"Rule '{rule_name}' added",
            "rule_id": rule_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(
    item_id: str = Query(..., description="ID of extracted item"),
    item_type: str = Query(..., description="Item type: decision|action|gap"),
    is_valid: bool = Query(..., description="Whether extraction is valid"),
    feedback_text: str = Query("", description="User feedback"),
    suggestion: Optional[str] = Query(None, description="Suggested correction if invalid")
):
    """
    Submit user validation feedback for an extraction.
    
    Feedback is used to refine extraction rules and track accuracy metrics.
    """
    try:
        if item_type not in ["decision", "action", "gap"]:
            raise ValueError(f"Invalid item_type: {item_type}")
        
        service = get_service()
        service.validate_extraction(
            item_id=item_id,
            is_valid=is_valid,
            item_type=item_type,
            feedback=feedback_text,
            suggestion=suggestion
        )
        
        return {
            "status": "success",
            "message": "Feedback recorded",
            "item_id": item_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error recording feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_accuracy_metrics():
    """
    Get accuracy metrics across all user validations.
    
    Returns validation counts and accuracy by item type.
    """
    try:
        service = get_service()
        metrics = service.get_accuracy_metrics()
        return {
            "status": "success",
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggested-rules")
async def get_suggested_rules():
    """
    Get rules suggested by feedback analysis.
    
    Rules are suggested based on false positives and false negatives
    identified through user feedback.
    """
    try:
        service = get_service()
        suggestions = service.get_suggested_rules()
        return {
            "status": "success",
            "suggestions": suggestions,
            "count": len(suggestions)
        }
    except Exception as e:
        logger.error(f"Error getting suggested rules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "intelligent-document-analysis",
        "version": "0.1.0"
    }
