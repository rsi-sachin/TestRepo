"""
Intelligent Document Analysis Service - High-level API.
"""

from pathlib import Path
from typing import Optional
import logging

from app.intelligent_document_parsing.core.decision_extractor import DecisionExtractor
from app.intelligent_document_parsing.services.user_feedback_handler import (
    UserFeedbackHandler, UserFeedback
)
from app.intelligent_document_parsing.core.heuristic_engine import ExtractionRule
from app.intelligent_document_parsing.models.analysis_models import AnalysisResult

logger = logging.getLogger(__name__)


class DocumentAnalysisService:
    """
    High-level service for intelligent document analysis.
    
    Orchestrates:
    - PDF parsing and section extraction
    - Multi-method heuristic analysis
    - User feedback collection
    - Rule refinement
    """
    
    def __init__(self):
        self.extractor = DecisionExtractor()
        self.feedback_handler = UserFeedbackHandler()
    
    def analyze_section(
        self,
        pdf_path: Path,
        section_number: str,
        subsection_depth: int = 1
    ) -> AnalysisResult:
        """
        Analyze a specific section of a PDF.
        
        Args:
            pdf_path: Path to PDF file
            section_number: Section number (e.g., "4.1")
            subsection_depth: How many levels of subsections to extract
            
        Returns:
            AnalysisResult with decisions, actions, and gaps
        """
        logger.info(f"Starting section analysis: {section_number}")
        result = self.extractor.analyze_section(
            pdf_path,
            section_number,
            depth=subsection_depth
        )
        return result
    
    def analyze_document(self, pdf_path: Path) -> AnalysisResult:
        """Analyze entire PDF document."""
        logger.info(f"Starting full document analysis: {pdf_path.name}")
        result = self.extractor.analyze_full_document(pdf_path)
        return result
    
    def add_custom_extraction_rule(self, rule: ExtractionRule):
        """
        Add a custom extraction rule.
        
        Allows fine-tuning extraction for specific documents or domains.
        """
        self.extractor.add_extraction_rule(rule)
        logger.info(f"Added custom rule: {rule.name}")
    
    def validate_extraction(
        self,
        item_id: str,
        is_valid: bool,
        item_type: str,
        feedback: str = "",
        suggestion: Optional[str] = None
    ):
        """
        Record user validation feedback for an extraction.
        
        Args:
            item_id: ID of the extracted item
            is_valid: Whether the extraction is correct
            item_type: Type of item ("decision", "action", "gap")
            feedback: User's feedback text
            suggestion: Suggested correction if invalid
        """
        if item_type not in ("decision", "action", "gap"):
            raise ValueError(f"Invalid item_type: {item_type!r}. Must be one of: decision, action, gap")
        fb = UserFeedback(
            item_id=item_id,
            item_type=item_type,
            is_valid=is_valid,
            feedback_text=feedback,
            suggested_correction=suggestion
        )
        self.feedback_handler.record_feedback(fb)
    
    def get_accuracy_metrics(self) -> dict:
        """Get accuracy metrics across all validations."""
        return self.feedback_handler.get_accuracy_report()
    
    def get_suggested_rules(self) -> list:
        """Get rules suggested by feedback analysis."""
        return self.feedback_handler.suggest_rules_from_feedback()
    
    def export_analysis_results(self, result: AnalysisResult, output_path: Path):
        """Export analysis results to JSON file."""
        with open(output_path, 'w') as f:
            f.write(result.to_json())
        logger.info(f"Analysis results exported to {output_path}")
    
    def export_feedback_metrics(self, output_path: Path):
        """Export feedback and accuracy metrics."""
        with open(output_path, 'w') as f:
            f.write(self.feedback_handler.generate_refined_rules())
        logger.info(f"Feedback metrics exported to {output_path}")
