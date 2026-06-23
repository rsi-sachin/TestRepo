"""
Information Index Integrator - Utility functions to integrate analysis results with information indexes.

This module provides helper functions to:
- Convert analysis results (decisions, actions, gaps) into indexed facts
- Extract and track referenced documents from analysis
- Populate global and document-specific indexes
- Create action items for postponed tasks
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ..models.information_index_models import (
    GlobalFact, EvidenceLink, ReferenceDocument, ActionItemRecord,
    DocumentSpecificFact, DocumentSpecificIndex, ItemStatus, ReferenceStatus
)
from ..models.analysis_models import AnalysisResult, Decision, ActionItem, InformationGap


def create_global_fact_from_decision(decision: Decision, document_name: str) -> GlobalFact:
    """
    Convert an extracted decision to a global fact.
    
    Args:
        decision: Decision object from analysis
        document_name: Name of the document
        
    Returns:
        GlobalFact with evidence linking back to source
    """
    evidence = EvidenceLink(
        source_document=document_name,
        section_number=decision.section_number,
        page_number=decision.page_number,
        extraction_confidence=decision.confidence,
        extraction_methods=[]
    )
    
    return GlobalFact(
        fact_id=f"fact_{uuid.uuid4().hex[:12]}",
        title=decision.title,
        description=decision.description,
        fact_type=decision.decision_type.value,
        evidence_links=[evidence],
        status=ItemStatus.DRAFT,
        confidence=decision.confidence,
        keywords=decision.keywords,
    )


def create_global_facts_from_analysis(analysis_result: AnalysisResult) -> List[GlobalFact]:
    """
    Convert all analysis results (decisions, actions, gaps) to global facts.
    
    Args:
        analysis_result: AnalysisResult from document analysis
        
    Returns:
        List of GlobalFact objects
    """
    facts = []
    doc_name = analysis_result.document_name
    
    # Convert decisions
    for decision in analysis_result.decisions:
        facts.append(create_global_fact_from_decision(decision, doc_name))
    
    # Convert action items
    for action in analysis_result.action_items:
        evidence = EvidenceLink(
            source_document=doc_name,
            section_number=action.section_number,
            page_number=action.page_number,
            extraction_confidence=action.confidence,
            extraction_methods=[]
        )
        facts.append(GlobalFact(
            fact_id=f"fact_{uuid.uuid4().hex[:12]}",
            title=action.title,
            description=action.description,
            fact_type=f"action_{action.priority.value}",
            evidence_links=[evidence],
            status=ItemStatus.DRAFT,
            confidence=action.confidence,
        ))
    
    # Convert information gaps
    for gap in analysis_result.information_gaps:
        evidence = EvidenceLink(
            source_document=doc_name,
            section_number=gap.section_number,
            page_number=gap.page_number,
            extraction_confidence=gap.confidence,
            extraction_methods=[]
        )
        facts.append(GlobalFact(
            fact_id=f"fact_{uuid.uuid4().hex[:12]}",
            title=gap.title,
            description=gap.description,
            fact_type=f"gap_{gap.impact}",
            evidence_links=[evidence],
            status=ItemStatus.DRAFT,
            confidence=gap.confidence,
        ))
    
    return facts


def extract_referenced_documents(analysis_result: AnalysisResult) -> List[ReferenceDocument]:
    """
    Extract referenced document information from analysis text.
    
    This is a placeholder that identifies patterns like "A1TP [3]", "ETSI TS 132 158", etc.
    
    Args:
        analysis_result: AnalysisResult from document analysis
        
    Returns:
        List of ReferenceDocument objects
    """
    references = []
    
    # Combine all text from analysis
    all_text = "\n".join([
        d.description for d in analysis_result.decisions
    ] + [
        a.description for a in analysis_result.action_items
    ] + [
        g.description for g in analysis_result.information_gaps
    ])
    
    # Known reference patterns
    reference_patterns = {
        r"A1TP\s*\[": ("A1TP", "A1 Technical Protocol"),
        r"A1TD\s*\[": ("A1TD", "A1 Technical Data Model"),
        r"A1GAP\s*\[": ("A1GAP", "A1 Gap Analysis Protocol"),
        r"ETSI\s+TS\s+132\s+158": ("ETSI TS 132 158", "ETSI TS 132 158 - Design Patterns"),
    }
    
    import re
    found_refs = set()
    
    for pattern, (ref_id, ref_name) in reference_patterns.items():
        if re.search(pattern, all_text):
            if ref_id not in found_refs:
                found_refs.add(ref_id)
                references.append(ReferenceDocument(
                    reference_id=ref_id,
                    reference_name=ref_name,
                    status=ReferenceStatus.NOT_FOUND,
                    discovered_in_documents=[analysis_result.document_name],
                    discovered_sections=[analysis_result.analyzed_section],
                ))
    
    return references


def create_document_specific_facts(analysis_result: AnalysisResult,
                                  document_version: str) -> Dict[str, List[DocumentSpecificFact]]:
    """
    Create document-specific facts organized by section.
    
    Args:
        analysis_result: AnalysisResult from document analysis
        document_version: Version of the document
        
    Returns:
        Dictionary mapping section numbers to lists of DocumentSpecificFact
    """
    facts_by_section: Dict[str, List[DocumentSpecificFact]] = {}
    
    # Process decisions
    for decision in analysis_result.decisions:
        section = decision.section_number
        if section not in facts_by_section:
            facts_by_section[section] = []
        
        facts_by_section[section].append(DocumentSpecificFact(
            fact_id=f"fact_{uuid.uuid4().hex[:12]}",
            title=decision.title,
            description=decision.description,
            section_number=section,
            page_number=decision.page_number,
            extraction_confidence=decision.confidence,
            status=ItemStatus.DRAFT,
        ))
    
    # Process action items
    for action in analysis_result.action_items:
        section = action.section_number
        if section not in facts_by_section:
            facts_by_section[section] = []
        
        facts_by_section[section].append(DocumentSpecificFact(
            fact_id=f"fact_{uuid.uuid4().hex[:12]}",
            title=action.title,
            description=action.description,
            section_number=section,
            page_number=action.page_number,
            extraction_confidence=action.confidence,
            status=ItemStatus.DRAFT,
        ))
    
    # Process information gaps
    for gap in analysis_result.information_gaps:
        section = gap.section_number
        if section not in facts_by_section:
            facts_by_section[section] = []
        
        facts_by_section[section].append(DocumentSpecificFact(
            fact_id=f"fact_{uuid.uuid4().hex[:12]}",
            title=gap.title,
            description=gap.description,
            section_number=section,
            page_number=gap.page_number,
            extraction_confidence=gap.confidence,
            status=ItemStatus.DRAFT,
        ))
    
    return facts_by_section


def create_action_item_from_postponed_task(
    title: str,
    description: str,
    related_documents: List[str],
    priority: str = "medium",
    notes: Optional[str] = None
) -> ActionItemRecord:
    """
    Create an action item record for postponed tasks.
    
    Args:
        title: Title of the action
        description: Description of what needs to be done
        related_documents: List of related document IDs
        priority: Priority level ('critical', 'high', 'medium', 'low')
        notes: Optional notes
        
    Returns:
        ActionItemRecord for tracking in the action items log
    """
    return ActionItemRecord(
        action_id=f"action_{uuid.uuid4().hex[:12]}",
        title=title,
        description=description,
        related_documents=related_documents,
        status=ItemStatus.PENDING_APPROVAL,
        priority=priority,
        notes=notes,
    )


def populate_global_index_from_section_4_1(
    index_manager,
    analysis_result: AnalysisResult
) -> None:
    """
    Populate global information index from Section 4.1 analysis results.
    
    This is a convenience function for the specific use case of processing
    Section 4.1 (A1 Application Protocol Introduction) and adding its
    technical foundation, design patterns, and solution approach to the
    global index.
    
    Args:
        index_manager: InformationIndexManager instance
        analysis_result: AnalysisResult from Section 4.1 analysis
    """
    # Add facts from section 4.1
    facts = create_global_facts_from_analysis(analysis_result)
    for fact in facts:
        index_manager.add_fact(fact)
    
    # Extract referenced documents
    references = extract_referenced_documents(analysis_result)
    for ref in references:
        existing = index_manager.get_reference_by_id(ref.reference_id)
        if existing:
            # Update discovered documents and sections
            if analysis_result.document_name not in existing.discovered_in_documents:
                existing.discovered_in_documents.append(analysis_result.document_name)
            if analysis_result.analyzed_section not in existing.discovered_sections:
                existing.discovered_sections.append(analysis_result.analyzed_section)
            index_manager.add_reference(existing)
        else:
            index_manager.add_reference(ref)


def create_postponed_action_item_for_reference_retrieval(
    reference_id: str,
    document_context: str,
    index_manager
) -> ActionItemRecord:
    """
    Create a postponed action item for retrieving a reference document.
    
    Args:
        reference_id: ID of the reference document
        document_context: Context about why this document is needed
        index_manager: InformationIndexManager instance
        
    Returns:
        ActionItemRecord representing the postponed retrieval task
    """
    action = ActionItemRecord(
        action_id=f"action_{uuid.uuid4().hex[:12]}",
        title=f"Retrieve and analyze reference document: {reference_id}",
        description=(
            f"Locate and process reference document {reference_id} "
            f"mentioned in {document_context}. "
            f"Extract decisions, actions, and gaps. "
            f"Link findings back to global information index."
        ),
        related_documents=[reference_id],
        status=ItemStatus.PENDING_APPROVAL,
        priority="high",
        notes="Placeholder action - awaiting user confirmation for retrieval"
    )
    
    return action


def export_index_summary_to_file(index_manager, output_path: Path) -> None:
    """
    Export a summary of the information index state to a file.
    
    Args:
        index_manager: InformationIndexManager instance
        output_path: Path to write the summary file
    """
    import json
    summary = index_manager.export_summary()
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, default=str)
