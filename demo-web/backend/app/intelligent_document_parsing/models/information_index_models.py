"""
Data models for information indexing and reference tracking.

This module provides models for managing global and document-specific
information indexes to track extracted facts, decisions, and their
evidence across multiple documents.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import json


class ItemStatus(str, Enum):
    """Status lifecycle for indexed items."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_user_approval"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"


class ReferenceStatus(str, Enum):
    """Status for reference document discovery."""
    NOT_FOUND = "not_found"
    FOUND_PUBLIC = "found_public"
    PROPRIETARY = "proprietary"
    SCHEDULED = "scheduled_for_retrieval"
    RETRIEVED = "retrieved"
    ERROR = "retrieval_error"


@dataclass
class EvidenceLink:
    """Link to evidence in source document."""
    source_document: str
    section_number: str
    page_number: Optional[int] = None
    line_number: Optional[int] = None
    extraction_confidence: float = 0.0
    extraction_methods: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "source_document": self.source_document,
            "section": self.section_number,
            "page": self.page_number,
            "line": self.line_number,
            "confidence": round(self.extraction_confidence, 2),
            "extraction_methods": self.extraction_methods,
        }


@dataclass
class GlobalFact:
    """Fact indexed in the global information index."""
    fact_id: str
    title: str
    description: str
    fact_type: str  # 'requirement', 'design_decision', 'constraint', etc.
    evidence_links: List[EvidenceLink] = field(default_factory=list)
    status: ItemStatus = ItemStatus.DRAFT
    confidence: float = 0.0
    keywords: List[str] = field(default_factory=list)
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    user_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "fact_id": self.fact_id,
            "title": self.title,
            "description": self.description,
            "type": self.fact_type,
            "status": self.status.value,
            "confidence": round(self.confidence, 2),
            "keywords": self.keywords,
            "evidence_count": len(self.evidence_links),
            "evidence_links": [e.to_dict() for e in self.evidence_links],
            "created_date": self.created_date,
            "last_updated": self.last_updated,
            "user_notes": self.user_notes,
        }


@dataclass
class ReferenceDocument:
    """Reference to another document mentioned in analyzed documents."""
    reference_id: str
    reference_name: str
    description: Optional[str] = None
    url_template: Optional[str] = None
    status: ReferenceStatus = ReferenceStatus.NOT_FOUND
    discovered_in_documents: List[str] = field(default_factory=list)
    discovered_sections: List[str] = field(default_factory=list)
    retrieval_notes: Optional[str] = None
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_checked: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "reference_id": self.reference_id,
            "reference_name": self.reference_name,
            "description": self.description,
            "url_template": self.url_template,
            "status": self.status.value,
            "discovered_in_documents": self.discovered_in_documents,
            "discovered_sections": self.discovered_sections,
            "retrieval_notes": self.retrieval_notes,
            "created_date": self.created_date,
            "last_checked": self.last_checked,
        }


@dataclass
class GlobalInformationIndex:
    """Global index of facts and references across all A1-related documents."""
    index_version: str = "1.0"
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    document_count: int = 0
    facts: List[GlobalFact] = field(default_factory=list)
    references: List[ReferenceDocument] = field(default_factory=list)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        data = {
            "metadata": {
                "index_version": self.index_version,
                "created_date": self.created_date,
                "last_updated": self.last_updated,
                "document_count": self.document_count,
                "facts_count": len(self.facts),
                "references_count": len(self.references),
            },
            "facts": [f.to_dict() for f in self.facts],
            "references": [r.to_dict() for r in self.references],
        }
        return json.dumps(data, indent=2, default=str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metadata": {
                "index_version": self.index_version,
                "created_date": self.created_date,
                "last_updated": self.last_updated,
                "document_count": self.document_count,
                "facts_count": len(self.facts),
                "references_count": len(self.references),
            },
            "facts": [f.to_dict() for f in self.facts],
            "references": [r.to_dict() for r in self.references],
        }


@dataclass
class DocumentSpecificFact:
    """Fact with version-specific information for a single document."""
    fact_id: str
    title: str
    description: str
    section_number: str
    page_number: Optional[int] = None
    extraction_confidence: float = 0.0
    extraction_methods: List[str] = field(default_factory=list)
    status: ItemStatus = ItemStatus.DRAFT
    source_code_references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "fact_id": self.fact_id,
            "title": self.title,
            "description": self.description,
            "section": self.section_number,
            "page": self.page_number,
            "extraction_confidence": round(self.extraction_confidence, 2),
            "extraction_methods": self.extraction_methods,
            "status": self.status.value,
            "source_code_references": self.source_code_references,
        }


@dataclass
class DocumentSpecificIndex:
    """Document-specific information index with version tracking."""
    document_id: str
    document_name: str
    document_version: str
    document_path: str
    extraction_date: str = field(default_factory=lambda: datetime.now().isoformat())
    facts_by_section: Dict[str, List[DocumentSpecificFact]] = field(default_factory=dict)
    source_code_mapping: Dict[str, List[str]] = field(default_factory=dict)
    extraction_summary: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        data = {
            "document_metadata": {
                "document_id": self.document_id,
                "document_name": self.document_name,
                "document_version": self.document_version,
                "document_path": self.document_path,
                "extraction_date": self.extraction_date,
            },
            "facts_by_section": {
                section: [f.to_dict() for f in facts]
                for section, facts in self.facts_by_section.items()
            },
            "source_code_mapping": self.source_code_mapping,
            "extraction_summary": self.extraction_summary,
            "metadata": self.metadata,
        }
        return json.dumps(data, indent=2, default=str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_metadata": {
                "document_id": self.document_id,
                "document_name": self.document_name,
                "document_version": self.document_version,
                "document_path": self.document_path,
                "extraction_date": self.extraction_date,
            },
            "facts_by_section": {
                section: [f.to_dict() for f in facts]
                for section, facts in self.facts_by_section.items()
            },
            "source_code_mapping": self.source_code_mapping,
            "extraction_summary": self.extraction_summary,
            "metadata": self.metadata,
        }


@dataclass
class ActionItemRecord:
    """Record of a postponed action item requiring user confirmation."""
    action_id: str
    title: str
    description: str
    related_documents: List[str] = field(default_factory=list)
    status: ItemStatus = ItemStatus.PENDING_APPROVAL
    priority: str = "medium"  # 'critical', 'high', 'medium', 'low'
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    scheduled_date: Optional[str] = None
    completed_date: Optional[str] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "action_id": self.action_id,
            "title": self.title,
            "description": self.description,
            "related_documents": self.related_documents,
            "status": self.status.value,
            "priority": self.priority,
            "created_date": self.created_date,
            "scheduled_date": self.scheduled_date,
            "completed_date": self.completed_date,
            "notes": self.notes,
        }
