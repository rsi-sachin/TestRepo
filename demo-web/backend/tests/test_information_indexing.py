"""
Tests for Information Indexing System

Tests cover:
- Data model serialization
- Index manager operations
- Reference document resolution
- Integration with analysis results
- Index querying and filtering
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from app.intelligent_document_parsing.models.information_index_models import (
    GlobalFact, EvidenceLink, ReferenceDocument, DocumentSpecificFact,
    DocumentSpecificIndex, ActionItemRecord, GlobalInformationIndex,
    ItemStatus, ReferenceStatus
)
from app.intelligent_document_parsing.services.information_index_manager import (
    InformationIndexManager
)
from app.intelligent_document_parsing.services.reference_document_resolver import (
    ReferenceDocumentResolver, create_reference_resolver
)
from app.intelligent_document_parsing.services.information_index_integrator import (
    create_global_fact_from_decision,
    extract_referenced_documents,
    create_document_specific_facts,
    create_postponed_action_item_for_reference_retrieval,
)
from app.intelligent_document_parsing.models.analysis_models import (
    Decision, DecisionType, ActionItem, ItemPriority, InformationGap,
    AnalysisResult, Evidence
)


class TestInformationIndexModels:
    """Test data models for information indexing."""
    
    def test_evidence_link_serialization(self):
        """Test EvidenceLink can be serialized to dict."""
        link = EvidenceLink(
            source_document="ts_103987v040300p",
            section_number="4.1",
            page_number=42,
            extraction_confidence=0.85,
            extraction_methods=["tfidf_scoring", "regex_keyword"]
        )
        
        data = link.to_dict()
        assert data["source_document"] == "ts_103987v040300p"
        assert data["section"] == "4.1"
        assert data["page"] == 42
        assert data["confidence"] == 0.85
    
    def test_global_fact_with_evidence(self):
        """Test GlobalFact with evidence links."""
        evidence = EvidenceLink(
            source_document="ts_103987v040300p",
            section_number="4.1",
            extraction_confidence=0.75
        )
        
        fact = GlobalFact(
            fact_id="fact_001",
            title="REST Architecture",
            description="Uses REST pattern for API design",
            fact_type="design_decision",
            evidence_links=[evidence],
            status=ItemStatus.DRAFT,
            confidence=0.75
        )
        
        assert fact.fact_id == "fact_001"
        assert len(fact.evidence_links) == 1
        assert fact.status == ItemStatus.DRAFT
        
        data = fact.to_dict()
        assert data["fact_id"] == "fact_001"
        assert data["status"] == "draft"
    
    def test_reference_document_model(self):
        """Test ReferenceDocument model."""
        ref = ReferenceDocument(
            reference_id="A1TP",
            reference_name="A1 Technical Protocol",
            description="HTTP definition for A1",
            url_template="https://example.com/a1tp/{version}.pdf",
            status=ReferenceStatus.NOT_FOUND,
            discovered_in_documents=["ts_103987v040300p"],
            discovered_sections=["4.1"]
        )
        
        assert ref.reference_id == "A1TP"
        assert ref.status == ReferenceStatus.NOT_FOUND
        assert len(ref.discovered_in_documents) == 1
        
        data = ref.to_dict()
        assert data["status"] == "not_found"
    
    def test_document_specific_fact(self):
        """Test DocumentSpecificFact model."""
        fact = DocumentSpecificFact(
            fact_id="fact_sec_001",
            title="HTTP based",
            description="Architecture based on HTTP",
            section_number="4.1",
            page_number=42,
            extraction_confidence=0.80
        )
        
        assert fact.section_number == "4.1"
        assert fact.extraction_confidence == 0.80
        
        data = fact.to_dict()
        assert data["section"] == "4.1"
    
    def test_action_item_record(self):
        """Test ActionItemRecord model."""
        action = ActionItemRecord(
            action_id="action_001",
            title="Retrieve A1TP specification",
            description="Locate and process A1TP reference",
            related_documents=["A1TP"],
            status=ItemStatus.PENDING_APPROVAL,
            priority="high"
        )
        
        assert action.status == ItemStatus.PENDING_APPROVAL
        assert action.priority == "high"
        
        data = action.to_dict()
        assert data["action_id"] == "action_001"
        assert data["status"] == "pending_user_approval"
    
    def test_global_index_json_serialization(self):
        """Test GlobalInformationIndex can be serialized to JSON."""
        index = GlobalInformationIndex(
            document_count=1,
            facts=[],
            references=[]
        )
        
        json_str = index.to_json()
        data = json.loads(json_str)
        
        assert data["metadata"]["index_version"] == "1.0"
        assert data["metadata"]["document_count"] == 1
        assert len(data["facts"]) == 0


class TestInformationIndexManager:
    """Test InformationIndexManager operations."""
    
    @pytest.fixture
    def temp_index_dir(self):
        """Create temporary directory for index files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def manager(self, temp_index_dir):
        """Create IndexManager with temporary directory."""
        return InformationIndexManager(index_dir=temp_index_dir)
    
    def test_manager_initialization(self, manager):
        """Test manager initializes with empty index."""
        index = manager.get_global_index()
        assert index is not None
        assert len(index.facts) == 0
        assert len(index.references) == 0
    
    def test_add_and_retrieve_fact(self, manager):
        """Test adding and retrieving facts."""
        fact = GlobalFact(
            fact_id="fact_test_001",
            title="Test Fact",
            description="Test description",
            fact_type="requirement",
            status=ItemStatus.DRAFT,
            confidence=0.85
        )
        
        manager.add_fact(fact)
        retrieved = manager.get_global_index()
        
        assert len(retrieved.facts) == 1
        assert retrieved.facts[0].fact_id == "fact_test_001"
    
    def test_add_and_retrieve_reference(self, manager):
        """Test adding and retrieving references."""
        ref = ReferenceDocument(
            reference_id="TEST_REF",
            reference_name="Test Reference",
            status=ReferenceStatus.NOT_FOUND
        )
        
        manager.add_reference(ref)
        retrieved = manager.get_reference_by_id("TEST_REF")
        
        assert retrieved is not None
        assert retrieved.reference_id == "TEST_REF"
    
    def test_get_facts_by_status(self, manager):
        """Test filtering facts by status."""
        fact1 = GlobalFact(
            fact_id="fact_draft",
            title="Draft Fact",
            description="",
            fact_type="requirement",
            status=ItemStatus.DRAFT
        )
        fact2 = GlobalFact(
            fact_id="fact_completed",
            title="Completed Fact",
            description="",
            fact_type="requirement",
            status=ItemStatus.COMPLETED
        )
        
        manager.add_fact(fact1)
        manager.add_fact(fact2)
        
        draft_facts = manager.get_facts_by_status(ItemStatus.DRAFT)
        completed_facts = manager.get_facts_by_status(ItemStatus.COMPLETED)
        
        assert len(draft_facts) == 1
        assert len(completed_facts) == 1
    
    def test_get_completed_facts(self, manager):
        """Test getting completed facts (highest priority)."""
        fact = GlobalFact(
            fact_id="fact_completed",
            title="Completed Fact",
            description="",
            fact_type="requirement",
            status=ItemStatus.COMPLETED
        )
        
        manager.add_fact(fact)
        completed = manager.get_completed_facts()
        
        assert len(completed) == 1
        assert completed[0].fact_id == "fact_completed"
    
    def test_add_and_manage_action_items(self, manager):
        """Test adding and managing action items."""
        action = ActionItemRecord(
            action_id="action_test_001",
            title="Test Action",
            description="Test action description",
            status=ItemStatus.PENDING_APPROVAL,
            priority="high"
        )
        
        manager.add_action_item(action)
        pending = manager.get_pending_approvals()
        
        assert len(pending) == 1
        assert pending[0].action_id == "action_test_001"
        
        # Update status
        manager.update_action_item_status(
            "action_test_001",
            ItemStatus.SCHEDULED
        )
        scheduled = manager.get_action_items_by_status(ItemStatus.SCHEDULED)
        
        assert len(scheduled) == 1
    
    def test_reference_status_update(self, manager):
        """Test updating reference status."""
        ref = ReferenceDocument(
            reference_id="REF_TEST",
            reference_name="Test Ref",
            status=ReferenceStatus.NOT_FOUND
        )
        
        manager.add_reference(ref)
        manager.update_reference_status(
            "REF_TEST",
            ReferenceStatus.FOUND_PUBLIC,
            notes="Found on ETSI website"
        )
        
        updated = manager.get_reference_by_id("REF_TEST")
        assert updated.status == ReferenceStatus.FOUND_PUBLIC
        assert "ETSI" in updated.retrieval_notes
    
    def test_get_references_by_status(self, manager):
        """Test filtering references by status."""
        ref1 = ReferenceDocument(
            reference_id="REF_1",
            reference_name="Not Found",
            status=ReferenceStatus.NOT_FOUND
        )
        ref2 = ReferenceDocument(
            reference_id="REF_2",
            reference_name="Found Public",
            status=ReferenceStatus.FOUND_PUBLIC
        )
        
        manager.add_reference(ref1)
        manager.add_reference(ref2)
        
        not_found = manager.get_references_by_status(ReferenceStatus.NOT_FOUND)
        found = manager.get_references_by_status(ReferenceStatus.FOUND_PUBLIC)
        
        assert len(not_found) == 1
        assert len(found) == 1
    
    def test_document_specific_index_creation(self, manager):
        """Test creating document-specific indexes."""
        doc_index = manager.create_document_specific_index(
            document_id="test_doc",
            document_name="Test Document",
            document_version="1.0",
            document_path="/path/to/doc.pdf"
        )
        
        assert doc_index.document_id == "test_doc"
        assert doc_index.document_version == "1.0"
        
        # Save and load
        manager.save_document_specific_index(doc_index)
        loaded = manager.load_document_specific_index("test_doc")
        
        assert loaded is not None
        assert loaded.document_id == "test_doc"
    
    def test_export_summary(self, manager):
        """Test exporting index summary."""
        fact = GlobalFact(
            fact_id="fact_1",
            title="Test",
            description="",
            fact_type="requirement",
            status=ItemStatus.DRAFT
        )
        manager.add_fact(fact)
        
        summary = manager.export_summary()
        
        assert summary["global_index"]["facts_count"] == 1
        assert summary["global_index"]["facts_by_status"]["draft"] == 1


class TestReferenceDocumentResolver:
    """Test ReferenceDocumentResolver placeholder functions."""
    
    @pytest.fixture
    def manager(self):
        """Create IndexManager for resolver."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield InformationIndexManager(index_dir=tmpdir)
    
    @pytest.fixture
    def resolver(self, manager):
        """Create reference resolver."""
        return create_reference_resolver(manager)
    
    def test_resolver_initialization(self, resolver):
        """Test resolver initializes with known patterns."""
        assert resolver is not None
        assert len(resolver.known_references) > 0
        assert "A1TP" in resolver.known_references
    
    def test_locate_reference_document(self, resolver):
        """Test placeholder locate function."""
        ref = resolver.locate_reference_document("A1TP")
        
        assert ref is not None
        assert ref.reference_id == "A1TP"
        assert ref.reference_name == "A1 Technical Protocol"
    
    def test_batch_locate_references(self, resolver):
        """Test batch location of references."""
        results = resolver.batch_locate_references(
            ["A1TP", "A1TD", "UNKNOWN"]
        )
        
        assert len(results) == 3
        assert results["A1TP"] is not None
        assert results["A1TD"] is not None
        assert results["UNKNOWN"] is None
    
    def test_suggest_reference_sources(self, resolver):
        """Test suggesting reference sources by keywords."""
        suggestions = resolver.suggest_reference_sources(
            ["A1", "protocol", "HTTP"]
        )
        
        # Should find A1TP and A1TD (contain "A1")
        assert len(suggestions) > 0


class TestInformationIndexIntegration:
    """Test integration with analysis results."""
    
    def test_create_fact_from_decision(self):
        """Test converting Decision to GlobalFact."""
        decision = Decision(
            id="dec_001",
            title="Use REST",
            description="REST architecture selected for API",
            decision_type=DecisionType.DESIGN_DECISION,
            section_number="4.1",
            page_number=42,
            confidence=0.85
        )
        
        fact = create_global_fact_from_decision(decision, "test_doc")
        
        assert fact.title == "Use REST"
        assert fact.fact_type == "design_decision"
        assert len(fact.evidence_links) == 1
        assert fact.evidence_links[0].source_document == "test_doc"
    
    def test_extract_referenced_documents(self):
        """Test extracting references from analysis."""
        decision = Decision(
            id="dec_001",
            title="Based on A1TP",
            description="Architecture based on HTTP as defined in A1TP [3]",
            decision_type=DecisionType.DESIGN_DECISION,
            section_number="4.1",
            page_number=42,
            confidence=0.85
        )
        
        result = AnalysisResult(
            document_name="ts_103987v040300p",
            document_path="/path/to/doc.pdf",
            analyzed_section="4.1",
            analysis_depth=1,
            decisions=[decision],
            action_items=[],
            information_gaps=[]
        )
        
        references = extract_referenced_documents(result)
        
        assert len(references) > 0
        # Should find A1TP reference
        assert any(ref.reference_id == "A1TP" for ref in references)
    
    def test_create_document_specific_facts(self):
        """Test creating document-specific facts from analysis."""
        decision = Decision(
            id="dec_001",
            title="Test Decision",
            description="Test description",
            decision_type=DecisionType.REQUIREMENT,
            section_number="4.1",
            page_number=42,
            confidence=0.80
        )
        
        result = AnalysisResult(
            document_name="test_doc",
            document_path="/path/to/doc.pdf",
            analyzed_section="4.1",
            analysis_depth=1,
            decisions=[decision],
            action_items=[],
            information_gaps=[]
        )
        
        facts_by_section = create_document_specific_facts(result, "1.0")
        
        assert "4.1" in facts_by_section
        assert len(facts_by_section["4.1"]) == 1
        assert facts_by_section["4.1"][0].section_number == "4.1"
    
    def test_create_postponed_action_item(self):
        """Test creating postponed action item."""
        action = create_postponed_action_item_for_reference_retrieval(
            reference_id="A1TP",
            document_context="Section 4.1",
            index_manager=None
        )
        
        assert action.action_id is not None
        assert "A1TP" in action.title
        assert action.status == ItemStatus.PENDING_APPROVAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
