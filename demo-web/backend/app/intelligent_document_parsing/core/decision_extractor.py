"""
Main decision extractor service that orchestrates extraction.
"""

import uuid
from typing import List, Optional, Dict
from datetime import datetime
import logging

from pathlib import Path
from app.parsers.pdf_parser import PdfParser
from ..models.analysis_models import (
    Decision, ActionItem, InformationGap, Section, Evidence,
    AnalysisResult, DecisionType, ItemPriority, ExtractionMethod
)
from ..core.section_parser import SectionParser, SectionNode
from ..core.heuristic_engine import HeuristicEngine, ExtractionRule
from ..utils.text_utils import TextNormalizer, SectionExtractor

logger = logging.getLogger(__name__)


class DecisionExtractor:
    """Main service for extracting decisions and analysis results."""
    
    def __init__(self):
        self.pdf_parser = PdfParser()
        self.section_parser = SectionParser()
        self.heuristic_engine = HeuristicEngine()
    
    def analyze_section(
        self,
        pdf_path: Path,
        section_number: str,
        depth: int = 1,
        apply_rules: bool = True
    ) -> AnalysisResult:
        """
        Analyze a specific section of a PDF document.
        
        Args:
            pdf_path: Path to PDF file
            section_number: Section number to analyze (e.g., "4.1")
            depth: Subsection depth to extract (1 = direct children only)
            apply_rules: Whether to apply custom extraction rules
            
        Returns:
            AnalysisResult with extracted decisions, actions, and gaps
        """
        logger.info(f"Starting analysis of {pdf_path.name} section {section_number}")
        
        # Parse PDF
        text = self.pdf_parser.parse_file(pdf_path)
        
        # Parse sections
        self.section_parser.parse(text)
        
        # Get target section
        section_node = self.section_parser.get_section_by_number(section_number)
        if not section_node:
            raise ValueError(f"Section {section_number} not found in document")
        
        # Use the section's own text; if empty (container section), aggregate from children
        section_text = section_node.text.strip()
        if not section_text and section_node.children:
            section_text = "\n".join(c.text for c in section_node.children if c.text)
        
        # Get subsections at specified depth
        subsections = self.section_parser.get_subsections(section_number, max_depth=depth)
        
        # Extract content
        decisions = self._extract_decisions_from_text(section_text, section_number)
        action_items = self._extract_actions_from_text(section_text, section_number)
        gaps = self._extract_gaps_from_text(section_text, section_number)
        
        # Build result
        result = AnalysisResult(
            document_name=pdf_path.name,
            document_path=str(pdf_path),
            analyzed_section=section_number,
            analysis_depth=depth,
            decisions=decisions,
            action_items=action_items,
            information_gaps=gaps,
            sections=self._build_section_tree(subsections),
            timestamp=datetime.now().isoformat(),
            heuristic_methods_used=list(ExtractionMethod),
        )
        
        logger.info(
            f"Analysis complete: {len(decisions)} decisions, "
            f"{len(action_items)} actions, {len(gaps)} gaps"
        )
        
        return result
    
    def analyze_full_document(self, pdf_path: Path) -> AnalysisResult:
        """Analyze entire PDF document."""
        logger.info(f"Starting full document analysis of {pdf_path.name}")
        
        text = self.pdf_parser.parse_file(pdf_path)
        self.section_parser.parse(text)
        
        # Extract from all sections
        decisions = self._extract_decisions_from_text(text, "full_document")
        action_items = self._extract_actions_from_text(text, "full_document")
        gaps = self._extract_gaps_from_text(text, "full_document")
        
        result = AnalysisResult(
            document_name=pdf_path.name,
            document_path=str(pdf_path),
            analyzed_section="full",
            analysis_depth=0,
            decisions=decisions,
            action_items=action_items,
            information_gaps=gaps,
            sections=self._build_section_tree(self.section_parser.sections),
            timestamp=datetime.now().isoformat(),
            heuristic_methods_used=list(ExtractionMethod),
        )
        
        return result
    
    def add_extraction_rule(self, rule: ExtractionRule):
        """Add a custom extraction rule."""
        self.heuristic_engine.add_custom_rule(rule)
    
    def validate_extraction(self, item_id: str, is_valid: bool, feedback: str = ""):
        """User validation of extracted item."""
        # This would update a database in a full implementation
        logger.info(f"Item {item_id} validated as {is_valid}: {feedback}")
    
    def _extract_decisions_from_text(
        self, 
        text: str, 
        section_num: str
    ) -> List[Decision]:
        """Extract decisions using heuristic engine."""
        results = self.heuristic_engine.extract_decisions(text)
        decisions = []
        
        for sentence, confidence, methods_used in results:
            decision = Decision(
                id=f"dec_{uuid.uuid4().hex[:8]}",
                title=sentence[:80].strip(),
                description=sentence,
                decision_type=self._infer_decision_type(sentence),
                section_number=section_num,
                confidence=confidence,
                evidence=[
                    Evidence(
                        source_text=sentence,
                        extraction_methods=methods_used,
                        confidence_score=confidence
                    )
                ],
                keywords=self._extract_keywords(sentence),
            )
            decisions.append(decision)
        
        return decisions
    
    def _extract_actions_from_text(
        self,
        text: str,
        section_num: str
    ) -> List[ActionItem]:
        """Extract action items using heuristic engine."""
        results = self.heuristic_engine.extract_action_items(text)
        actions = []
        
        for sentence, confidence, methods_used, priority_str in results:
            action = ActionItem(
                id=f"act_{uuid.uuid4().hex[:8]}",
                title=sentence[:80].strip(),
                description=sentence,
                priority=ItemPriority(priority_str),
                section_number=section_num,
                confidence=confidence,
                evidence=[
                    Evidence(
                        source_text=sentence,
                        extraction_methods=methods_used,
                        confidence_score=confidence
                    )
                ],
                owner_hints=self._extract_owner_hints(sentence),
            )
            actions.append(action)
        
        return actions
    
    def _extract_gaps_from_text(
        self,
        text: str,
        section_num: str
    ) -> List[InformationGap]:
        """Extract information gaps using heuristic engine."""
        results = self.heuristic_engine.extract_information_gaps(text)
        gaps = []
        
        for sentence, confidence, methods_used in results:
            gap = InformationGap(
                id=f"gap_{uuid.uuid4().hex[:8]}",
                title=sentence[:80].strip(),
                description=sentence,
                impact=self._infer_gap_impact(sentence),
                section_number=section_num,
                confidence=confidence,
                evidence=[
                    Evidence(
                        source_text=sentence,
                        extraction_methods=methods_used,
                        confidence_score=confidence
                    )
                ],
            )
            gaps.append(gap)
        
        return gaps
    
    def _infer_decision_type(self, text: str) -> DecisionType:
        """Infer decision type from text."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['shall', 'must', 'require']):
            return DecisionType.REQUIREMENT
        elif any(word in text_lower for word in ['constraint', 'limit', 'restriction']):
            return DecisionType.CONSTRAINT
        elif any(word in text_lower for word in ['design', 'architecture', 'design decision']):
            return DecisionType.DESIGN_DECISION
        elif any(word in text_lower for word in ['configure', 'configuration', 'setting']):
            return DecisionType.CONFIGURATION
        elif any(word in text_lower for word in ['process', 'procedure', 'workflow']):
            return DecisionType.PROCESS
        elif any(word in text_lower for word in ['standard', 'conform', 'compliance']):
            return DecisionType.STANDARD
        elif any(word in text_lower for word in ['best practice', 'recommend', 'prefer']):
            return DecisionType.BEST_PRACTICE
        else:
            return DecisionType.OTHER
    
    def _extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extract relevant keywords from text."""
        # Simple implementation: extract capitalized words
        import re
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        return list(dict.fromkeys(words))[:max_keywords]
    
    def _extract_owner_hints(self, text: str) -> List[str]:
        """Extract hints about who should own an action."""
        hints = []
        
        # Look for role/team mentions
        roles = ['developer', 'architect', 'tester', 'engineer', 'team', 'owner', 'manager']
        text_lower = text.lower()
        
        for role in roles:
            if role in text_lower:
                hints.append(role.capitalize())
        
        return hints
    
    def _infer_gap_impact(self, text: str) -> str:
        """Infer impact of an information gap."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['critical', 'blocking', 'impossible', 'cannot']):
            return "critical"
        elif any(word in text_lower for word in ['important', 'essential', 'required']):
            return "high"
        elif any(word in text_lower for word in ['useful', 'helpful', 'nice-to-have']):
            return "medium"
        else:
            return "low"
    
    def _build_section_tree(self, sections: List[SectionNode]) -> List[Section]:
        """Convert SectionNode tree to Section data class tree."""
        from ..models.analysis_models import Section as SectionModel
        
        result = []
        for node in sections:
            section = SectionModel(
                number=node.number,
                title=node.title,
                page_number=node.page_number or 1,
                depth=node.depth,
                text_preview=node.text[:200] + "..." if len(node.text) > 200 else node.text,
                subsections=self._build_section_tree(node.children)
            )
            result.append(section)
        
        return result
