"""
Example: Section 4.1 Analysis with Information Indexing

This example demonstrates:
1. Analyzing Section 4.1 (A1 Application Protocol Introduction)
2. Extracting facts, decisions, and referenced documents
3. Populating global and document-specific information indexes
4. Creating postponed action items for reference retrieval
5. Exporting index summaries

Use this as a template for processing other sections and documents.
"""

from pathlib import Path
from app.intelligent_document_parsing import (
    DocumentAnalysisService,
    InformationIndexManager,
    populate_global_index_from_section_4_1,
    create_global_facts_from_analysis,
    extract_referenced_documents,
    create_document_specific_facts,
    create_postponed_action_item_for_reference_retrieval,
)
from app.intelligent_document_parsing.services import create_reference_resolver


def example_section_4_1_indexing():
    """
    Full workflow: Analyze Section 4.1 and populate information indexes.
    """
    print("=" * 70)
    print("Example: Section 4.1 Analysis with Information Indexing")
    print("=" * 70)
    
    # Configuration
    pdf_path = Path("C:/TestRepo/ORAN/docs/ts_103987v040300p.pdf")
    section_number = "4.1"
    document_id = "ts_103987v040300p"
    document_version = "4.3.0"
    
    print(f"\n[1] ANALYZING SECTION {section_number}")
    print(f"    Document: {pdf_path.name}")
    print(f"    Version: {document_version}")
    print("-" * 70)
    
    # Step 1: Analyze section using DocumentAnalysisService
    service = DocumentAnalysisService()
    try:
        analysis_result = service.analyze_section(
            pdf_path=pdf_path,
            section_number=section_number,
            subsection_depth=1
        )
        print(f"✓ Analysis complete")
        print(f"  - Decisions found: {len(analysis_result.decisions)}")
        print(f"  - Action items: {len(analysis_result.action_items)}")
        print(f"  - Information gaps: {len(analysis_result.information_gaps)}")
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        return
    
    # Step 2: Initialize Information Index Manager
    print(f"\n[2] INITIALIZING INFORMATION INDEXES")
    print("-" * 70)
    index_manager = InformationIndexManager()
    print(f"✓ Index manager initialized")
    print(f"  - Global index path: {index_manager.global_index_path}")
    print(f"  - Index directory: {index_manager.index_dir}")
    
    # Step 3: Populate global index with facts from Section 4.1
    print(f"\n[3] POPULATING GLOBAL INDEX")
    print("-" * 70)
    try:
        populate_global_index_from_section_4_1(index_manager, analysis_result)
        print(f"✓ Global index populated")
        
        global_index = index_manager.get_global_index()
        print(f"  - Total facts in index: {len(global_index.facts)}")
        print(f"  - Total references tracked: {len(global_index.references)}")
        
        # Show reference documents discovered
        if global_index.references:
            print(f"\n  Referenced documents discovered:")
            for ref in global_index.references:
                print(f"    - {ref.reference_id}: {ref.reference_name}")
                print(f"      Status: {ref.status.value}")
    except Exception as e:
        print(f"✗ Failed to populate global index: {e}")
        return
    
    # Step 4: Create document-specific index
    print(f"\n[4] CREATING DOCUMENT-SPECIFIC INDEX")
    print("-" * 70)
    try:
        doc_index = index_manager.create_document_specific_index(
            document_id=document_id,
            document_name="ts_103987v040300p",
            document_version=document_version,
            document_path=str(pdf_path)
        )
        
        # Populate facts organized by section
        facts_by_section = create_document_specific_facts(
            analysis_result=analysis_result,
            document_version=document_version
        )
        doc_index.facts_by_section = facts_by_section
        
        # Save document-specific index
        index_manager.save_document_specific_index(doc_index)
        print(f"✓ Document-specific index created and saved")
        print(f"  - Sections with facts: {len(facts_by_section)}")
        for section, facts in facts_by_section.items():
            print(f"    - Section {section}: {len(facts)} facts")
    except Exception as e:
        print(f"✗ Failed to create document-specific index: {e}")
        return
    
    # Step 5: Create postponed action items for reference retrieval
    print(f"\n[5] CREATING POSTPONED ACTION ITEMS")
    print("-" * 70)
    try:
        action_items = []
        for ref in global_index.references:
            if ref.status.value in ("not_found", "scheduled_for_retrieval"):
                action = create_postponed_action_item_for_reference_retrieval(
                    reference_id=ref.reference_id,
                    document_context=f"Section {section_number} of {analysis_result.document_name}",
                    index_manager=index_manager
                )
                index_manager.add_action_item(action)
                action_items.append(action)
        
        print(f"✓ Postponed action items created")
        print(f"  - Total action items: {len(action_items)}")
        for action in action_items:
            print(f"    - {action.title}")
            print(f"      Priority: {action.priority}")
            print(f"      Status: {action.status.value}")
    except Exception as e:
        print(f"✗ Failed to create action items: {e}")
        return
    
    # Step 6: Export index summary
    print(f"\n[6] EXPORTING INDEX SUMMARY")
    print("-" * 70)
    try:
        summary = index_manager.export_summary()
        
        print(f"✓ Index summary exported")
        print(f"\n  Global Index Statistics:")
        print(f"    - Facts: {summary['global_index']['facts_count']}")
        print(f"    - References: {summary['global_index']['references_count']}")
        
        print(f"\n  Facts by Status:")
        for status, count in summary['global_index']['facts_by_status'].items():
            if count > 0:
                print(f"    - {status}: {count}")
        
        print(f"\n  References by Status:")
        for status, count in summary['global_index']['references_by_status'].items():
            if count > 0:
                print(f"    - {status}: {count}")
        
        print(f"\n  Action Items Statistics:")
        print(f"    - Total: {summary['action_items']['total_count']}")
        for status, count in summary['action_items']['by_status'].items():
            if count > 0:
                print(f"    - {status}: {count}")
        
        # Save summary to file
        summary_path = Path(f"./data/indexes/section_{section_number}_summary.json")
        import json
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"\n  Summary saved to: {summary_path}")
    except Exception as e:
        print(f"✗ Failed to export summary: {e}")
        return
    
    # Step 7: Initialize reference resolver
    print(f"\n[7] INITIALIZING REFERENCE RESOLVER")
    print("-" * 70)
    try:
        resolver = create_reference_resolver(index_manager)
        print(f"✓ Reference resolver initialized")
        print(f"  - Known reference patterns: {len(resolver.known_references)}")
        
        # Suggest reference sources
        suggestions = resolver.suggest_reference_sources(["A1", "interface", "protocol"])
        print(f"\n  Reference suggestions for keywords ['A1', 'interface', 'protocol']:")
        for ref_id in suggestions:
            print(f"    - {ref_id}")
    except Exception as e:
        print(f"✗ Failed to initialize resolver: {e}")
        return
    
    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE")
    print("=" * 70)
    print(f"\nNext Steps:")
    print(f"1. Review facts in global_information_index.json")
    print(f"2. Review document-specific index: {document_id}_information_index.json")
    print(f"3. Review postponed action items in action_items_log.json")
    print(f"4. Use reference resolver to locate reference documents")
    print(f"5. Process reference documents when available")
    print(f"6. Update global index with findings from reference documents")


def example_query_and_analyze_indexes():
    """
    Example: Query and analyze populated indexes.
    """
    print("\n" + "=" * 70)
    print("Example: Query and Analyze Information Indexes")
    print("=" * 70)
    
    index_manager = InformationIndexManager()
    
    # Query facts by status
    print(f"\n[1] QUERYING FACTS BY STATUS")
    print("-" * 70)
    
    from app.intelligent_document_parsing.models import ItemStatus
    
    for status in ItemStatus:
        facts = index_manager.get_facts_by_status(status)
        if facts:
            print(f"\n{status.value.upper()}:")
            for fact in facts[:3]:  # Show first 3
                print(f"  - {fact.title}")
                print(f"    Confidence: {fact.confidence:.2f}")
                print(f"    Evidence count: {len(fact.evidence_links)}")
            if len(facts) > 3:
                print(f"  ... and {len(facts) - 3} more")
    
    # Query action items
    print(f"\n[2] QUERYING ACTION ITEMS")
    print("-" * 70)
    
    pending_actions = index_manager.get_pending_approvals()
    print(f"Pending user approval: {len(pending_actions)}")
    for action in pending_actions[:3]:
        print(f"  - {action.title}")
        print(f"    Priority: {action.priority}")
    
    # Query references
    print(f"\n[3] QUERYING REFERENCE DOCUMENTS")
    print("-" * 70)
    
    from app.intelligent_document_parsing.models import ReferenceStatus
    
    for status in ReferenceStatus:
        refs = index_manager.get_references_by_status(status)
        if refs:
            print(f"\n{status.value.upper()}: {len(refs)}")
            for ref in refs[:3]:
                print(f"  - {ref.reference_name} ({ref.reference_id})")


def example_progressive_index_updates():
    """
    Example: Progressive updates to indexes as more documents are processed.
    
    Shows how the index accumulates knowledge as new documents are analyzed
    and their facts are added to the global index.
    """
    print("\n" + "=" * 70)
    print("Example: Progressive Index Updates")
    print("=" * 70)
    
    index_manager = InformationIndexManager()
    
    print(f"\nScenario: Processing multiple documents over time")
    print(f"- Each document contributes facts to the global index")
    print(f"- Cross-references between documents are tracked")
    print(f"- Action items accumulate for follow-up work")
    
    # Export current state
    print(f"\n[Current Index State]")
    summary = index_manager.export_summary()
    print(f"  Facts: {summary['global_index']['facts_count']}")
    print(f"  References: {summary['global_index']['references_count']}")
    print(f"  Pending actions: {summary['action_items']['by_status'].get('pending_user_approval', 0)}")
    
    print(f"\n[Future Documents]")
    print(f"  - ts_103987v040300p (COMPLETED) - A1 Application Protocol")
    print(f"    Status: Processed, facts indexed")
    print(f"  - [NEXT] TS 132 158 - ETSI Design Patterns")
    print(f"    Status: Awaiting retrieval and processing")
    print(f"  - [NEXT] A1TP Specification")
    print(f"    Status: Awaiting retrieval and processing")


if __name__ == "__main__":
    # Run examples
    try:
        example_section_4_1_indexing()
        example_query_and_analyze_indexes()
        example_progressive_index_updates()
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
