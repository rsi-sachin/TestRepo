"""
Data models for intelligent document analysis results.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class DecisionType(str, Enum):
    """Classification of decision types."""
    REQUIREMENT = "requirement"
    CONSTRAINT = "constraint"
    DESIGN_DECISION = "design_decision"
    CONFIGURATION = "configuration"
    PROCESS = "process"
    STANDARD = "standard"
    BEST_PRACTICE = "best_practice"
    OTHER = "other"


class ItemPriority(str, Enum):
    """Priority levels for action items."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ExtractionMethod(str, Enum):
    """Heuristic methods used for extraction."""
    REGEX_KEYWORD = "regex_keyword"
    SENTENCE_PATTERN = "sentence_pattern"
    TF_IDF_SCORING = "tfidf_scoring"
    RULE_BASED = "rule_based"


@dataclass
class Evidence:
    """Evidence supporting an extraction."""
    source_text: str
    page_number: Optional[int] = None
    line_number: Optional[int] = None
    extraction_methods: List[ExtractionMethod] = field(default_factory=list)
    confidence_score: float = 0.0


@dataclass
class Decision:
    """Extracted decision or requirement."""
    id: str
    title: str
    description: str
    decision_type: DecisionType
    evidence: List[Evidence] = field(default_factory=list)
    section_number: str = ""
    page_number: Optional[int] = None
    confidence: float = 0.0
    keywords: List[str] = field(default_factory=list)
    user_validated: bool = False
    user_feedback: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.decision_type.value,
            "confidence": round(self.confidence, 2),
            "keywords": self.keywords,
            "section": self.section_number,
            "page": self.page_number,
            "evidence_count": len(self.evidence),
            "user_validated": self.user_validated,
            "user_feedback": self.user_feedback,
        }


@dataclass
class ActionItem:
    """Extracted action item or task."""
    id: str
    title: str
    description: str
    priority: ItemPriority
    related_decision_ids: List[str] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    section_number: str = ""
    page_number: Optional[int] = None
    confidence: float = 0.0
    owner_hints: List[str] = field(default_factory=list)
    user_validated: bool = False
    user_feedback: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "confidence": round(self.confidence, 2),
            "section": self.section_number,
            "page": self.page_number,
            "owner_hints": self.owner_hints,
            "related_decisions": self.related_decision_ids,
            "evidence_count": len(self.evidence),
            "user_validated": self.user_validated,
            "user_feedback": self.user_feedback,
        }


@dataclass
class InformationGap:
    """Identified information gap or missing context."""
    id: str
    title: str
    description: str
    impact: str
    related_decision_ids: List[str] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    section_number: str = ""
    page_number: Optional[int] = None
    confidence: float = 0.0
    user_validated: bool = False
    user_feedback: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "impact": self.impact,
            "confidence": round(self.confidence, 2),
            "section": self.section_number,
            "page": self.page_number,
            "related_decisions": self.related_decision_ids,
            "evidence_count": len(self.evidence),
            "user_validated": self.user_validated,
            "user_feedback": self.user_feedback,
        }


@dataclass
class Section:
    """Document section metadata."""
    number: str
    title: str
    page_number: int
    depth: int
    text_preview: str = ""
    subsections: List['Section'] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "number": self.number,
            "title": self.title,
            "page": self.page_number,
            "depth": self.depth,
            "subsections": [s.to_dict() for s in self.subsections],
        }


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    document_name: str
    document_path: str
    analyzed_section: str
    analysis_depth: int
    decisions: List[Decision] = field(default_factory=list)
    action_items: List[ActionItem] = field(default_factory=list)
    information_gaps: List[InformationGap] = field(default_factory=list)
    sections: List[Section] = field(default_factory=list)
    timestamp: str = ""
    heuristic_methods_used: List[ExtractionMethod] = field(default_factory=list)
    extraction_rules_applied: List[str] = field(default_factory=list)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        data = {
            "metadata": {
                "document": self.document_name,
                "section": self.analyzed_section,
                "timestamp": self.timestamp,
                "methods": [m.value for m in self.heuristic_methods_used],
                "rules": self.extraction_rules_applied,
            },
            "decisions": [d.to_dict() for d in self.decisions],
            "action_items": [a.to_dict() for a in self.action_items],
            "information_gaps": [g.to_dict() for g in self.information_gaps],
            "sections": [s.to_dict() for s in self.sections],
            "summary": {
                "total_decisions": len(self.decisions),
                "total_actions": len(self.action_items),
                "total_gaps": len(self.information_gaps),
                "avg_confidence": round(self._avg_confidence(), 2),
            }
        }
        return json.dumps(data, indent=2, default=str)
    
    def _avg_confidence(self) -> float:
        """Calculate average confidence across all extractions."""
        all_items = self.decisions + self.action_items + self.information_gaps
        if not all_items:
            return 0.0
        total = sum(item.confidence for item in all_items)
        return total / len(all_items)
