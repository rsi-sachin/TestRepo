"""
Information Index Manager - Core logic for managing global and document-specific indexes.

This module handles:
- Creating and updating global information index
- Managing document-specific indexes with version tracking
- Querying facts by status, document, section, or keywords
- Tracking action items and their lifecycle
- Reconciling facts across document versions
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from .information_index_models import (
    GlobalInformationIndex, GlobalFact, ReferenceDocument, DocumentSpecificIndex,
    DocumentSpecificFact, ActionItemRecord, EvidenceLink, ItemStatus, ReferenceStatus
)


class InformationIndexManager:
    """Manager for global and document-specific information indexes."""
    
    def __init__(self, index_dir: Optional[str] = None):
        """
        Initialize the index manager.
        
        Args:
            index_dir: Directory to store index files. If None, uses './data/indexes'
        """
        if index_dir is None:
            index_dir = "./data/indexes"
        
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.global_index_path = self.index_dir / "global_information_index.json"
        self.action_items_path = self.index_dir / "action_items_log.json"
        
        self._global_index: Optional[GlobalInformationIndex] = None
        self._action_items: List[ActionItemRecord] = []
        
        self._load_or_initialize_indexes()
    
    def _load_or_initialize_indexes(self) -> None:
        """Load existing indexes or create new ones."""
        if self.global_index_path.exists():
            self._load_global_index()
        else:
            self._global_index = GlobalInformationIndex()
            self._save_global_index()
        
        if self.action_items_path.exists():
            self._load_action_items()
        else:
            self._save_action_items()
    
    def _load_global_index(self) -> None:
        """Load global index from JSON file."""
        try:
            with open(self.global_index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct GlobalInformationIndex from JSON
            facts = [
                GlobalFact(
                    fact_id=f["fact_id"],
                    title=f["title"],
                    description=f["description"],
                    fact_type=f["type"],
                    status=ItemStatus(f["status"]),
                    confidence=f["confidence"],
                    keywords=f["keywords"],
                    created_date=f["created_date"],
                    last_updated=f["last_updated"],
                    user_notes=f.get("user_notes"),
                    evidence_links=[
                        EvidenceLink(
                            source_document=e["source_document"],
                            section_number=e["section"],
                            page_number=e["page"],
                            line_number=e["line"],
                            extraction_confidence=e["confidence"],
                            extraction_methods=e["extraction_methods"],
                        )
                        for e in f.get("evidence_links", [])
                    ]
                )
                for f in data.get("facts", [])
            ]
            
            references = [
                ReferenceDocument(
                    reference_id=r["reference_id"],
                    reference_name=r["reference_name"],
                    description=r.get("description"),
                    url_template=r.get("url_template"),
                    status=ReferenceStatus(r["status"]),
                    discovered_in_documents=r.get("discovered_in_documents", []),
                    discovered_sections=r.get("discovered_sections", []),
                    retrieval_notes=r.get("retrieval_notes"),
                    created_date=r["created_date"],
                    last_checked=r.get("last_checked"),
                )
                for r in data.get("references", [])
            ]
            
            metadata = data.get("metadata", {})
            self._global_index = GlobalInformationIndex(
                index_version=metadata.get("index_version", "1.0"),
                created_date=metadata.get("created_date"),
                last_updated=metadata.get("last_updated"),
                document_count=metadata.get("document_count", 0),
                facts=facts,
                references=references,
            )
        except Exception as e:
            print(f"Error loading global index: {e}. Creating new index.")
            self._global_index = GlobalInformationIndex()
    
    def _load_action_items(self) -> None:
        """Load action items from JSON file."""
        try:
            with open(self.action_items_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._action_items = [
                ActionItemRecord(
                    action_id=a["action_id"],
                    title=a["title"],
                    description=a["description"],
                    related_documents=a.get("related_documents", []),
                    status=ItemStatus(a["status"]),
                    priority=a.get("priority", "medium"),
                    created_date=a["created_date"],
                    scheduled_date=a.get("scheduled_date"),
                    completed_date=a.get("completed_date"),
                    notes=a.get("notes"),
                )
                for a in data.get("action_items", [])
            ]
        except Exception as e:
            print(f"Error loading action items: {e}")
            self._action_items = []
    
    def _save_global_index(self) -> None:
        """Save global index to JSON file."""
        self._global_index.last_updated = datetime.now().isoformat()
        with open(self.global_index_path, 'w', encoding='utf-8') as f:
            f.write(self._global_index.to_json())
    
    def _save_action_items(self) -> None:
        """Save action items to JSON file."""
        data = {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "action_items_count": len(self._action_items),
            },
            "action_items": [a.to_dict() for a in self._action_items],
        }
        with open(self.action_items_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def add_fact(self, fact: GlobalFact) -> None:
        """
        Add a fact to the global index.
        
        Args:
            fact: GlobalFact to add
        """
        # Check if fact already exists
        existing = next((f for f in self._global_index.facts if f.fact_id == fact.fact_id), None)
        if existing:
            # Update existing fact
            self._global_index.facts.remove(existing)
        
        self._global_index.facts.append(fact)
        self._save_global_index()
    
    def get_facts_by_status(self, status: ItemStatus) -> List[GlobalFact]:
        """
        Get facts filtered by status.
        
        Args:
            status: ItemStatus to filter by
            
        Returns:
            List of matching facts
        """
        return [f for f in self._global_index.facts if f.status == status]
    
    def get_facts_by_document(self, document_name: str) -> List[GlobalFact]:
        """
        Get facts discovered in a specific document.
        
        Args:
            document_name: Name of the document
            
        Returns:
            List of facts with evidence from that document
        """
        result = []
        for fact in self._global_index.facts:
            if any(e.source_document == document_name for e in fact.evidence_links):
                result.append(fact)
        return result
    
    def get_facts_by_section(self, document_name: str, section_number: str) -> List[GlobalFact]:
        """
        Get facts from a specific section of a document.
        
        Args:
            document_name: Name of the document
            section_number: Section number (e.g., "4.1")
            
        Returns:
            List of matching facts
        """
        result = []
        for fact in self._global_index.facts:
            if any(
                e.source_document == document_name and e.section_number == section_number
                for e in fact.evidence_links
            ):
                result.append(fact)
        return result
    
    def get_facts_by_keywords(self, keywords: List[str]) -> List[GlobalFact]:
        """
        Get facts matching keywords.
        
        Args:
            keywords: List of keywords to search
            
        Returns:
            List of matching facts
        """
        result = []
        for fact in self._global_index.facts:
            if any(kw.lower() in fact.keywords for kw in keywords):
                result.append(fact)
        return result
    
    def get_completed_facts(self) -> List[GlobalFact]:
        """Get facts with completed status (highest priority)."""
        return self.get_facts_by_status(ItemStatus.COMPLETED)
    
    def add_reference(self, reference: ReferenceDocument) -> None:
        """
        Add a reference document to the index.
        
        Args:
            reference: ReferenceDocument to add
        """
        existing = next(
            (r for r in self._global_index.references if r.reference_id == reference.reference_id),
            None
        )
        if existing:
            self._global_index.references.remove(existing)
        
        self._global_index.references.append(reference)
        self._save_global_index()
    
    def get_reference_by_id(self, reference_id: str) -> Optional[ReferenceDocument]:
        """
        Get a reference by ID.
        
        Args:
            reference_id: ID of the reference
            
        Returns:
            ReferenceDocument or None
        """
        return next(
            (r for r in self._global_index.references if r.reference_id == reference_id),
            None
        )
    
    def get_references_by_status(self, status: ReferenceStatus) -> List[ReferenceDocument]:
        """
        Get references filtered by retrieval status.
        
        Args:
            status: ReferenceStatus to filter by
            
        Returns:
            List of matching references
        """
        return [r for r in self._global_index.references if r.status == status]
    
    def update_reference_status(self, reference_id: str, status: ReferenceStatus,
                               notes: Optional[str] = None) -> None:
        """
        Update the status of a reference document.
        
        Args:
            reference_id: ID of the reference
            status: New ReferenceStatus
            notes: Optional retrieval notes
        """
        reference = self.get_reference_by_id(reference_id)
        if reference:
            reference.status = status
            reference.last_checked = datetime.now().isoformat()
            if notes:
                reference.retrieval_notes = notes
            self._save_global_index()
    
    def add_action_item(self, action: ActionItemRecord) -> None:
        """
        Add a postponed action item.
        
        Args:
            action: ActionItemRecord to add
        """
        existing = next((a for a in self._action_items if a.action_id == action.action_id), None)
        if existing:
            self._action_items.remove(existing)
        
        self._action_items.append(action)
        self._save_action_items()
    
    def get_action_items_by_status(self, status: ItemStatus) -> List[ActionItemRecord]:
        """
        Get action items filtered by status.
        
        Args:
            status: ItemStatus to filter by
            
        Returns:
            List of matching action items
        """
        return [a for a in self._action_items if a.status == status]
    
    def get_pending_approvals(self) -> List[ActionItemRecord]:
        """Get action items pending user approval."""
        return self.get_action_items_by_status(ItemStatus.PENDING_APPROVAL)
    
    def update_action_item_status(self, action_id: str, status: ItemStatus,
                                 scheduled_date: Optional[str] = None,
                                 completed_date: Optional[str] = None,
                                 notes: Optional[str] = None) -> None:
        """
        Update the status of an action item.
        
        Args:
            action_id: ID of the action item
            status: New ItemStatus
            scheduled_date: Optional scheduled date
            completed_date: Optional completion date
            notes: Optional notes
        """
        action = next((a for a in self._action_items if a.action_id == action_id), None)
        if action:
            action.status = status
            if scheduled_date:
                action.scheduled_date = scheduled_date
            if completed_date:
                action.completed_date = completed_date
            if notes:
                action.notes = notes
            self._save_action_items()
    
    def create_document_specific_index(self, document_id: str, document_name: str,
                                      document_version: str, document_path: str) -> DocumentSpecificIndex:
        """
        Create a new document-specific index.
        
        Args:
            document_id: Unique identifier for the document
            document_name: Human-readable name of the document
            document_version: Version of the document
            document_path: Path to the document file
            
        Returns:
            New DocumentSpecificIndex instance
        """
        return DocumentSpecificIndex(
            document_id=document_id,
            document_name=document_name,
            document_version=document_version,
            document_path=document_path,
        )
    
    def save_document_specific_index(self, doc_index: DocumentSpecificIndex) -> None:
        """
        Save a document-specific index to file.
        
        Args:
            doc_index: DocumentSpecificIndex to save
        """
        index_file = self.index_dir / f"{doc_index.document_id}_information_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(doc_index.to_json())
    
    def load_document_specific_index(self, document_id: str) -> Optional[DocumentSpecificIndex]:
        """
        Load a document-specific index from file.
        
        Args:
            document_id: ID of the document
            
        Returns:
            DocumentSpecificIndex or None if not found
        """
        index_file = self.index_dir / f"{document_id}_information_index.json"
        if not index_file.exists():
            return None
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data["document_metadata"]
            facts_by_section = {}
            
            for section, facts_list in data.get("facts_by_section", {}).items():
                facts_by_section[section] = [
                    DocumentSpecificFact(
                        fact_id=f["fact_id"],
                        title=f["title"],
                        description=f["description"],
                        section_number=f["section"],
                        page_number=f["page"],
                        extraction_confidence=f["extraction_confidence"],
                        extraction_methods=f["extraction_methods"],
                        status=ItemStatus(f["status"]),
                        source_code_references=f.get("source_code_references", []),
                    )
                    for f in facts_list
                ]
            
            return DocumentSpecificIndex(
                document_id=metadata["document_id"],
                document_name=metadata["document_name"],
                document_version=metadata["document_version"],
                document_path=metadata["document_path"],
                extraction_date=metadata["extraction_date"],
                facts_by_section=facts_by_section,
                source_code_mapping=data.get("source_code_mapping", {}),
                extraction_summary=data.get("extraction_summary", {}),
                metadata=data.get("metadata", {}),
            )
        except Exception as e:
            print(f"Error loading document-specific index: {e}")
            return None
    
    def get_global_index(self) -> GlobalInformationIndex:
        """Get the current global index."""
        return self._global_index
    
    def export_summary(self) -> Dict[str, Any]:
        """
        Export a summary of the information index state.
        
        Returns:
            Dictionary with summary statistics
        """
        return {
            "global_index": {
                "facts_count": len(self._global_index.facts),
                "facts_by_status": {
                    status.value: len(self.get_facts_by_status(status))
                    for status in ItemStatus
                },
                "references_count": len(self._global_index.references),
                "references_by_status": {
                    status.value: len(self.get_references_by_status(status))
                    for status in ReferenceStatus
                },
            },
            "action_items": {
                "total_count": len(self._action_items),
                "by_status": {
                    status.value: len(self.get_action_items_by_status(status))
                    for status in ItemStatus
                },
            },
        }
