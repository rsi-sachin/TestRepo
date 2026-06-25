"""
Unit tests for Intelligent Document Parsing module.

Tests core functionality without requiring external PDFs.
"""

import pytest
from pathlib import Path
from io import StringIO

from app.intelligent_document_parsing.core.section_parser import SectionParser, SectionNode
from app.intelligent_document_parsing.core.heuristic_engine import HeuristicEngine, ExtractionRule
from app.intelligent_document_parsing.utils.text_utils import (
    TextNormalizer, KeywordMatcher, PatternMatcher, TextTokenizer
)
from app.intelligent_document_parsing.models.analysis_models import (
    Decision, ActionItem, InformationGap, DecisionType, ItemPriority
)
from app.intelligent_document_parsing.services.user_feedback_handler import (
    UserFeedbackHandler, UserFeedback
)


class TestSectionParser:
    """Test section parsing functionality."""
    
    def test_parse_sections(self):
        """Test parsing of document sections."""
        text = """
1 Introduction
This is the introduction.

2 Main Content
Main content here.

2.1 Subsection
More details.

2.2 Another Subsection
Additional info.

3 Conclusion
Final notes.
        """
        
        parser = SectionParser()
        sections = parser.parse(text)
        
        assert len(sections) == 3, f"Expected 3 top-level sections, got {len(sections)}"
        assert sections[0].number == "1"
        assert sections[0].title == "Introduction"
        assert sections[1].number == "2"
        assert len(sections[1].children) == 2, "Section 2 should have 2 subsections"
    
    def test_get_section_by_number(self):
        """Test retrieving section by number."""
        text = """
4 A1 Protocol
Content for 4

4.1 Introduction
Intro content

4.2 Details
Detail content
        """
        
        parser = SectionParser()
        parser.parse(text)
        
        section = parser.get_section_by_number("4.1")
        assert section is not None
        assert section.title == "Introduction"
    
    def test_get_sections_at_depth(self):
        """Test filtering sections by depth."""
        text = """
1 Top
1.1 Sub1
1.1.1 SubSub1
1.2 Sub2
2 Top2
        """
        
        parser = SectionParser()
        parser.parse(text)
        
        depth1 = parser.get_sections_at_depth(1)
        depth2 = parser.get_sections_at_depth(2)
        depth3 = parser.get_sections_at_depth(3)
        
        assert len(depth1) == 2
        assert len(depth2) == 2
        assert len(depth3) == 1


class TestKeywordMatcher:
    """Test keyword matching."""
    
    def test_decision_keywords(self):
        """Test decision keyword scoring."""
        text = "The system shall implement the feature"
        score, keywords = KeywordMatcher.score_decision_keywords(text)
        
        assert score > 0
        assert "shall" in keywords
    
    def test_action_keywords(self):
        """Test action keyword scoring."""
        text = "Implement the new feature and test it thoroughly"
        score, keywords = KeywordMatcher.score_action_keywords(text)
        
        assert score > 0
        assert "implement" in keywords
        assert "test" in keywords
    
    def test_gap_keywords(self):
        """Test gap keyword scoring."""
        text = "The requirements are unclear and need further clarification"
        score, keywords = KeywordMatcher.score_gap_keywords(text)
        
        assert score > 0
        assert "unclear" in keywords


class TestPatternMatcher:
    """Test pattern matching."""
    
    def test_requirement_patterns(self):
        """Test requirement pattern matching."""
        text = "The system must handle all requests"
        score, count = PatternMatcher.match_patterns(
            text,
            PatternMatcher.REQUIREMENT_PATTERNS
        )
        
        assert count > 0
        assert score > 0
    
    def test_action_patterns(self):
        """Test action pattern matching."""
        text = "Implement the new authentication module"
        score, count = PatternMatcher.match_patterns(
            text,
            PatternMatcher.ACTION_PATTERNS
        )
        
        assert count > 0


class TestTextTokenizer:
    """Test text tokenization."""
    
    def test_tokenize(self):
        """Test basic tokenization."""
        text = "The system shall implement features"
        tokens = TextTokenizer.tokenize(text)
        
        assert len(tokens) > 0
        assert "system" in tokens
        assert "implement" in tokens
    
    def test_tokenize_meaningful(self):
        """Test meaningful tokenization (excluding stopwords)."""
        text = "The system and the user"
        tokens = TextTokenizer.tokenize_meaningful(text)
        
        # Should exclude stopwords
        assert "system" in tokens
        assert "user" in tokens
        assert "and" not in tokens
        assert "the" not in tokens


class TestHeuristicEngine:
    """Test the heuristic extraction engine."""
    
    def test_extract_decisions(self):
        """Test decision extraction."""
        text = """
The system shall implement secure authentication.
Users must be able to change passwords.
This is important for security.
        """
        
        engine = HeuristicEngine()
        results = engine.extract_decisions(text)
        
        assert len(results) > 0
        for sentence, confidence, methods in results:
            assert 0 <= confidence <= 1
            assert len(methods) > 0
    
    def test_extract_action_items(self):
        """Test action item extraction."""
        text = """
The team must implement the new API.
We need to test all endpoints thoroughly.
        """
        
        engine = HeuristicEngine()
        results = engine.extract_action_items(text)
        
        assert len(results) > 0
        for sentence, confidence, methods, priority in results:
            assert priority in [ItemPriority.CRITICAL.value, ItemPriority.HIGH.value, 
                              ItemPriority.MEDIUM.value, ItemPriority.LOW.value]
    
    def test_extract_information_gaps(self):
        """Test information gap extraction."""
        text = """
The security requirements are unclear.
The API specification is still pending clarification.
        """
        
        engine = HeuristicEngine()
        results = engine.extract_information_gaps(text)
        
        assert len(results) > 0
    
    def test_custom_rules(self):
        """Test custom rule application."""
        engine = HeuristicEngine()
        
        rule = ExtractionRule(
            id="test_rule",
            name="Test Rule",
            rule_type="decision",
            pattern=r"(?i)custom_keyword",
            confidence_boost=0.5
        )
        
        engine.add_custom_rule(rule)
        
        text = "This sentence contains custom_keyword"
        results = engine.extract_decisions(text)
        
        assert len(results) > 0


class TestUserFeedbackHandler:
    """Test user feedback handling."""
    
    def test_record_feedback(self):
        """Test feedback recording."""
        handler = UserFeedbackHandler()
        
        feedback = UserFeedback(
            item_id="dec_123",
            item_type="decision",
            is_valid=True,
            feedback_text="Good extraction"
        )
        
        handler.record_feedback(feedback)
        
        stats = handler.stats_by_type["decision"]
        assert stats.total_validations == 1
        assert stats.valid_count == 1
        assert stats.accuracy == 1.0
    
    def test_accuracy_calculation(self):
        """Test accuracy metrics calculation."""
        handler = UserFeedbackHandler()
        
        # Record valid feedback
        handler.record_feedback(UserFeedback(
            item_id="1", item_type="decision", is_valid=True
        ))
        handler.record_feedback(UserFeedback(
            item_id="2", item_type="decision", is_valid=True
        ))
        
        # Record invalid feedback
        handler.record_feedback(UserFeedback(
            item_id="3", item_type="decision", is_valid=False
        ))
        
        report = handler.get_accuracy_report()
        
        assert report["decision"]["total"] == 3
        assert report["decision"]["valid"] == 2
        assert report["decision"]["invalid"] == 1
        assert report["decision"]["accuracy"] == pytest.approx(0.67, abs=0.01)
    
    def test_false_positives(self):
        """Test identifying false positives."""
        handler = UserFeedbackHandler()
        
        handler.record_feedback(UserFeedback(
            item_id="fp_1", item_type="decision", is_valid=False
        ))
        handler.record_feedback(UserFeedback(
            item_id="tp_1", item_type="decision", is_valid=True
        ))
        
        false_positives = handler.get_false_positives()
        assert len(false_positives) == 1
        assert false_positives[0].item_id == "fp_1"


class TestTextNormalizer:
    """Test text normalization."""
    
    def test_normalize(self):
        """Test text normalization."""
        text = "  This   has   extra    spaces  "
        normalized = TextNormalizer.normalize(text)
        
        assert normalized == "This has extra spaces"
    
    def test_extract_sentences(self):
        """Test sentence extraction."""
        text = "First sentence. Second sentence! Third sentence?"
        sentences = TextNormalizer.extract_sentences(text)
        
        assert len(sentences) == 3
        assert sentences[0] == "First sentence"


class TestDataModels:
    """Test data models."""
    
    def test_decision_to_dict(self):
        """Test Decision model serialization."""
        decision = Decision(
            id="dec_1",
            title="Test Decision",
            description="This is a test",
            decision_type=DecisionType.REQUIREMENT,
            confidence=0.85
        )
        
        d = decision.to_dict()
        
        assert d["id"] == "dec_1"
        assert d["type"] == "requirement"
        assert d["confidence"] == 0.85
    
    def test_action_item_to_dict(self):
        """Test ActionItem model serialization."""
        action = ActionItem(
            id="act_1",
            title="Test Action",
            description="Do something",
            priority=ItemPriority.HIGH,
            confidence=0.9
        )
        
        d = action.to_dict()
        
        assert d["priority"] == "high"
        assert d["confidence"] == 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
