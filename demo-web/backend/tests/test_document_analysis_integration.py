"""
Integration test for complete Document Analysis Service workflow.

Tests end-to-end scenarios without requiring actual PDF files.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from app.intelligent_document_parsing import DocumentAnalysisService
from app.intelligent_document_parsing.core import ExtractionRule
from app.intelligent_document_parsing.models import DecisionType, ItemPriority


class TestDocumentAnalysisServiceIntegration:
    """Integration tests for DocumentAnalysisService."""
    
    @patch('app.intelligent_document_parsing.core.decision_extractor.PdfParser')
    def test_analyze_section_workflow(self, mock_pdf_parser):
        """Test complete section analysis workflow."""
        # Setup mock
        mock_text = """
4 A1 Application Protocol
Content for section 4

4.1 Introduction
The A1 interface shall support multiple communication patterns.
Developers must implement proper error handling.
The specification is unclear about timeout values.

4.2 Requirements
The system shall ensure secure communication.
Implementers need to follow ETSI standards.
        """
        
        mock_instance = MagicMock()
        mock_instance.parse_file.return_value = mock_text
        mock_pdf_parser.return_value = mock_instance
        
        service = DocumentAnalysisService()
        
        # Execute
        result = service.analyze_section(
            pdf_path=Path("test.pdf"),
            section_number="4.1",
            subsection_depth=1
        )
        
        # Verify
        assert result.document_name == "test.pdf"
        assert result.analyzed_section == "4.1"
        assert len(result.decisions) > 0
        assert len(result.action_items) > 0
        assert len(result.information_gaps) > 0
        assert result._avg_confidence() > 0
    
    def test_add_custom_rule_and_validate(self):
        """Test adding custom rules and validating extractions."""
        service = DocumentAnalysisService()
        
        # Add custom rule
        rule = ExtractionRule(
            id="test_rule",
            name="A1 Interface Rule",
            rule_type="decision",
            pattern=r"(?i)(A1\s+interface|information\s+service)",
            confidence_boost=0.3
        )
        
        service.add_custom_extraction_rule(rule)
        
        # Verify rule was added
        assert len(service.extractor.heuristic_engine.custom_rules) == 1
    
    def test_feedback_workflow(self):
        """Test user feedback recording and analysis."""
        service = DocumentAnalysisService()
        
        # Record validations
        service.validate_extraction(
            item_id="dec_1",
            is_valid=True,
            item_type="decision",
            feedback="Correct decision extraction"
        )
        
        service.validate_extraction(
            item_id="dec_2",
            is_valid=False,
            item_type="decision",
            feedback="False positive, just background text",
            suggestion="Exclude background paragraphs"
        )
        
        service.validate_extraction(
            item_id="act_1",
            is_valid=True,
            item_type="action",
            feedback="Good action item"
        )
        
        # Get metrics
        metrics = service.get_accuracy_metrics()
        
        assert metrics["decision"]["total"] == 2
        assert metrics["decision"]["accuracy"] == 0.5  # 1 valid out of 2
        assert metrics["action"]["total"] == 1
        assert metrics["action"]["accuracy"] == 1.0
    
    def test_suggested_rules_from_feedback(self):
        """Test rule suggestions from feedback."""
        service = DocumentAnalysisService()
        
        # Record invalid feedback with suggestions
        service.validate_extraction(
            item_id="fp_1",
            is_valid=False,
            item_type="decision",
            feedback="This is not a decision",
            suggestion="background_pattern"
        )
        
        # Get suggestions
        suggestions = service.get_suggested_rules()
        
        assert len(suggestions) > 0
        assert any(s["type"] == "exclusion_rule" for s in suggestions)
    
    def test_export_results_json(self):
        """Test exporting results to JSON."""
        service = DocumentAnalysisService()
        
        # Create mock result
        from app.intelligent_document_parsing.models import AnalysisResult, Decision
        
        result = AnalysisResult(
            document_name="test.pdf",
            document_path="/path/to/test.pdf",
            analyzed_section="4.1",
            analysis_depth=1,
            decisions=[
                Decision(
                    id="dec_1",
                    title="Test Decision",
                    description="A test decision",
                    decision_type=DecisionType.REQUIREMENT,
                    confidence=0.85
                )
            ],
            timestamp="2026-06-23T10:00:00"
        )
        
        # Export to JSON
        json_output = result.to_json()
        
        assert "test.pdf" in json_output
        assert "decisions" in json_output
        assert "4.1" in json_output
        
        # Verify valid JSON
        import json
        parsed = json.loads(json_output)
        assert parsed["metadata"]["document"] == "test.pdf"
        assert len(parsed["decisions"]) == 1


class TestAPIRoutesIntegration:
    """Integration tests for API routes."""
    
    def test_api_health_check(self):
        """Test health check endpoint."""
        from app.intelligent_document_parsing.api_routes import router, get_service
        
        # The health check should be accessible
        assert router is not None
        assert get_service is not None
    
    def test_extraction_rule_api_model(self):
        """Test ExtractionRule API model."""
        rule = ExtractionRule(
            id="api_rule",
            name="API Test Rule",
            rule_type="decision",
            pattern=r"(?i)test",
            confidence_boost=0.15
        )
        
        assert rule.id == "api_rule"
        assert rule.rule_type == "decision"
        assert rule.confidence_boost == 0.15


class TestErrorHandling:
    """Test error handling in the service."""
    
    @patch('app.intelligent_document_parsing.core.decision_extractor.PdfParser')
    def test_missing_section(self, mock_pdf_parser):
        """Test handling of missing section."""
        mock_text = """
1 Introduction
2 Content
        """
        
        mock_instance = MagicMock()
        mock_instance.parse_file.return_value = mock_text
        mock_pdf_parser.return_value = mock_instance
        
        service = DocumentAnalysisService()
        
        # Should raise ValueError for non-existent section
        with pytest.raises(ValueError):
            service.analyze_section(
                pdf_path=Path("test.pdf"),
                section_number="99.99"
            )
    
    def test_invalid_feedback_item_type(self):
        """Test validation of feedback item type."""
        service = DocumentAnalysisService()
        
        # Invalid item type should raise
        with pytest.raises(ValueError):
            service.validate_extraction(
                item_id="test",
                is_valid=True,
                item_type="invalid_type",
                feedback="test"
            )


class TestConcurrency:
    """Test concurrent access to service."""
    
    def test_multiple_services(self):
        """Test multiple service instances."""
        service1 = DocumentAnalysisService()
        service2 = DocumentAnalysisService()
        
        # Each service should be independent
        rule1 = ExtractionRule(
            id="rule1",
            name="Service 1 Rule",
            rule_type="decision",
            pattern=r"test1",
            confidence_boost=0.1
        )
        
        service1.add_custom_extraction_rule(rule1)
        
        # Service 2 should not have this rule
        assert len(service1.extractor.heuristic_engine.custom_rules) == 1
        assert len(service2.extractor.heuristic_engine.custom_rules) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
