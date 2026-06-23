# Information Indexing System

## Overview

The Information Indexing System tracks and manages extracted facts, decisions, and references from analyzed documents using a hybrid approach with:

- **Global Information Index** - Aggregated facts across all A1-related documents
- **Document-Specific Indexes** - Version-aware fact tracking for individual documents
- **Reference Document Tracking** - Discovery and status tracking of cited documents
- **Action Item Log** - Postponed tasks requiring user confirmation or follow-up

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Document Analysis                        │
│  (Section 4.1, 4.2, ... from PDF specifications)           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          Information Index Integrator                        │
│  - Extract facts from analysis results                      │
│  - Identify referenced documents                            │
│  - Create action items for postponed tasks                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                   ┌───┴────────────────────┐
                   │                        │
                   ▼                        ▼
        ┌──────────────────────┐ ┌──────────────────────┐
        │  Global Index        │ │ Document-Specific    │
        │  (facts + refs)      │ │ Indexes              │
        │  ~/data/indexes/     │ │ (version tracking)   │
        │  global_..._index.   │ │ ~/data/indexes/      │
        │  action_items_log.   │ │ {doc_id}_index.json  │
        └──────────┬───────────┘ └────────────┬─────────┘
                   │                          │
                   ▼                          ▼
        ┌──────────────────────┐ ┌──────────────────────┐
        │ Index Manager        │ │ Reference Resolver   │
        │ - Add/query facts    │ │ - Locate documents   │
        │ - Manage refs        │ │ - Fetch content      │
        │ - Track actions      │ │ - Extract info       │
        │ - Version tracking   │ │ - Update status      │
        └──────────────────────┘ └──────────────────────┘
```

## Key Components

### 1. Data Models (`information_index_models.py`)

#### Global Index Models
- **GlobalFact** - Fact extracted from documents with evidence links
- **ReferenceDocument** - Reference to another document with discovery status
- **GlobalInformationIndex** - Container for all global facts and references

#### Document-Specific Models
- **DocumentSpecificFact** - Fact mapped to source section/page with extraction confidence
- **DocumentSpecificIndex** - Version-aware facts and source mappings for one document
- **ActionItemRecord** - Postponed task requiring user confirmation

#### Enums
- **ItemStatus** - `draft`, `pending_user_approval`, `scheduled`, `completed`
- **ReferenceStatus** - `not_found`, `found_public`, `proprietary`, `scheduled`, `retrieved`, `error`

### 2. Index Manager (`information_index_manager.py`)

**Core Responsibilities:**
- Load/save global and document-specific indexes
- Query facts by status, document, section, keywords
- Add/update reference documents
- Manage action items lifecycle
- Export summary statistics

**Key Methods:**
```python
manager = InformationIndexManager(index_dir="./data/indexes")

# Add/query facts
manager.add_fact(fact)
facts = manager.get_facts_by_status(ItemStatus.COMPLETED)
facts = manager.get_facts_by_document("ts_103987v040300p")
facts = manager.get_facts_by_section("ts_103987v040300p", "4.1")

# Manage references
manager.add_reference(reference)
ref = manager.get_reference_by_id("A1TP")
refs = manager.get_references_by_status(ReferenceStatus.NOT_FOUND)
manager.update_reference_status("A1TP", ReferenceStatus.FOUND_PUBLIC)

# Manage action items
manager.add_action_item(action)
actions = manager.get_pending_approvals()
manager.update_action_item_status(action_id, ItemStatus.SCHEDULED)

# Document-specific indexing
doc_index = manager.create_document_specific_index(...)
manager.save_document_specific_index(doc_index)
loaded_index = manager.load_document_specific_index(document_id)
```

### 3. Reference Resolver (`reference_document_resolver.py`)

**Placeholder Functions for Progressive Enhancement:**

```python
resolver = create_reference_resolver(index_manager)

# Placeholder: Locate reference documents
ref = resolver.locate_reference_document("A1TP")
refs = resolver.batch_locate_references(["A1TP", "A1TD", "ETSI TS 132 158"])

# Placeholder: Fetch document content
content = resolver.fetch_document_content("A1TP", force_refresh=False)

# Placeholder: Extract from reference
results = resolver.extract_from_reference("A1TP", section_query="4.1", keywords=["HTTP"])

# Placeholder: Validate availability
validation = resolver.validate_reference_availability("A1TP")

# Placeholder: Suggest sources
suggestions = resolver.suggest_reference_sources(["A1", "interface", "protocol"])

# Placeholder: Track progress
resolver.track_resolution_progress("A1TP", "searching", "Checking ETSI repository")
```

### 4. Integration Helpers (`information_index_integrator.py`)

**Functions to Convert Analysis Results to Index Facts:**

```python
# Convert extraction results to indexable facts
facts = create_global_facts_from_analysis(analysis_result)
doc_facts = create_document_specific_facts(analysis_result, version="4.3.0")

# Extract referenced documents from analysis
references = extract_referenced_documents(analysis_result)

# Convenience function for Section 4.1 workflow
populate_global_index_from_section_4_1(index_manager, analysis_result)

# Create postponed action items
action = create_postponed_action_item_for_reference_retrieval(
    reference_id="A1TP",
    document_context="Section 4.1 of ts_103987v040300p",
    index_manager=index_manager
)
```

## Workflow: Section 4.1 Analysis

### Step 1: Analyze Section
```python
from app.intelligent_document_parsing import DocumentAnalysisService
from pathlib import Path

service = DocumentAnalysisService()
result = service.analyze_section(
    pdf_path=Path("ts_103987v040300p.pdf"),
    section_number="4.1",
    subsection_depth=1
)
# Result contains: decisions, action_items, information_gaps
```

### Step 2: Initialize Index Manager
```python
from app.intelligent_document_parsing import InformationIndexManager

index_manager = InformationIndexManager()
# Loads/creates: global_information_index.json, action_items_log.json
```

### Step 3: Populate Global Index
```python
from app.intelligent_document_parsing import (
    populate_global_index_from_section_4_1,
    extract_referenced_documents
)

populate_global_index_from_section_4_1(index_manager, result)
# Adds facts, discovers references, updates global index
```

### Step 4: Create Document-Specific Index
```python
from app.intelligent_document_parsing import create_document_specific_facts

doc_index = index_manager.create_document_specific_index(
    document_id="ts_103987v040300p",
    document_name="ts_103987v040300p",
    document_version="4.3.0",
    document_path="C:/TestRepo/ORAN/docs/ts_103987v040300p.pdf"
)

facts_by_section = create_document_specific_facts(result, version="4.3.0")
doc_index.facts_by_section = facts_by_section
index_manager.save_document_specific_index(doc_index)
```

### Step 5: Handle Postponed Action Items
```python
from app.intelligent_document_parsing import (
    create_postponed_action_item_for_reference_retrieval
)

# Create action items for reference retrieval
for ref in index_manager.get_global_index().references:
    if ref.status.value == "not_found":
        action = create_postponed_action_item_for_reference_retrieval(
            reference_id=ref.reference_id,
            document_context="Section 4.1 of ts_103987v040300p",
            index_manager=index_manager
        )
        index_manager.add_action_item(action)
```

## File Structure

```
./data/indexes/
  ├── global_information_index.json      # Global facts and references
  ├── action_items_log.json              # Postponed tasks
  ├── ts_103987v040300p_information_index.json  # Document-specific (v4.3.0)
  ├── {other_doc_id}_information_index.json    # Other documents
  └── section_4_1_summary.json           # Query results/exports
```

### Global Index Schema
```json
{
  "metadata": {
    "index_version": "1.0",
    "created_date": "2026-06-23T...",
    "last_updated": "2026-06-23T...",
    "document_count": 1,
    "facts_count": 6,
    "references_count": 4
  },
  "facts": [
    {
      "fact_id": "fact_abc123",
      "title": "REST Architecture Selected",
      "description": "A1 Application Protocol uses REST...",
      "type": "design_decision",
      "status": "draft",
      "confidence": 0.44,
      "evidence_links": [
        {
          "source_document": "ts_103987v040300p",
          "section": "4.1",
          "page": 42,
          "confidence": 0.44,
          "extraction_methods": ["tfidf_scoring"]
        }
      ]
    }
  ],
  "references": [
    {
      "reference_id": "A1TP",
      "reference_name": "A1 Technical Protocol",
      "url_template": "https://example.com/standards/a1tp/{version}.pdf",
      "status": "not_found",
      "discovered_in_documents": ["ts_103987v040300p"],
      "discovered_sections": ["4.1"],
      "created_date": "2026-06-23T..."
    }
  ]
}
```

### Document-Specific Index Schema
```json
{
  "document_metadata": {
    "document_id": "ts_103987v040300p",
    "document_name": "ts_103987v040300p",
    "document_version": "4.3.0",
    "document_path": "C:/TestRepo/ORAN/docs/...",
    "extraction_date": "2026-06-23T..."
  },
  "facts_by_section": {
    "4.1": [
      {
        "fact_id": "fact_xyz789",
        "title": "HTTP Based",
        "description": "Based on HTTP as defined in A1TP [3]",
        "section": "4.1",
        "page": 42,
        "extraction_confidence": 0.33,
        "status": "draft"
      }
    ]
  },
  "source_code_mapping": {
    "information_index_manager.py::add_fact": ["fact_1", "fact_2"],
    "reference_document_resolver.py::locate_document": ["fact_3"]
  },
  "metadata": {}
}
```

## Query Examples

```python
# Find all completed facts (highest priority)
completed = index_manager.get_completed_facts()

# Get facts from Section 4.1
section_41_facts = index_manager.get_facts_by_section(
    "ts_103987v040300p", "4.1"
)

# Find facts with specific keywords
facts = index_manager.get_facts_by_keywords(["HTTP", "REST", "JSON"])

# Get references needing retrieval
to_retrieve = index_manager.get_references_by_status(
    ReferenceStatus.NOT_FOUND
)

# Get action items pending approval
pending = index_manager.get_pending_approvals()

# Export summary
summary = index_manager.export_summary()
```

## Status Lifecycle

### Fact Status: `draft` → `pending_user_approval` → `scheduled` → `completed`
- **draft**: Newly extracted, awaiting review
- **pending_user_approval**: Awaiting user validation
- **scheduled**: Approved, scheduled for processing
- **completed**: Validated and finalized (highest priority for production code)

### Reference Status: 
- **not_found**: Not yet located
- **found_public**: Located on public internet
- **proprietary**: Non-public or restricted
- **scheduled**: Scheduled for retrieval
- **retrieved**: Successfully obtained
- **error**: Retrieval failed

### Action Item Status: Same as Fact Status

## Progressive Enhancement

The system is designed for progressive enhancement:

1. **Phase 1 (Current)**: Placeholder functions log actions, guide users
2. **Phase 2 (Future)**: Real implementations for reference retrieval
3. **Phase 3**: Integration with external APIs (ETSI database, GitHub, etc.)
4. **Phase 4**: Recursive document analysis and cross-reference resolution

Example placeholder in `reference_document_resolver.py`:
```python
def fetch_document_content(self, reference_id: str) -> Optional[str]:
    # PLACEHOLDER LOGIC
    print(f"[PLACEHOLDER] Fetching document content: {reference_id}")
    
    # TODO: Implement actual fetch logic
    # - Download from reference.url_template
    # - Extract text from PDF/document
    # - Validate content integrity
    # - Cache in ./data/reference_documents/
    # - Update reference status to RETRIEVED
    
    return None
```

## Integration with Analysis Service

The Information Indexing System works seamlessly with `DocumentAnalysisService`:

```python
# Create service and index manager
service = DocumentAnalysisService()
index_manager = InformationIndexManager()

# Analyze document
result = service.analyze_section(pdf_path, "4.1")

# Populate indexes
populate_global_index_from_section_4_1(index_manager, result)

# Export results
service.export_analysis_results(result, Path("results.json"))

# Review index state
summary = index_manager.export_summary()
```

## Testing

Comprehensive tests cover:
- Index creation and persistence
- Fact adding, querying, and filtering
- Reference document tracking
- Action item lifecycle management
- Document-specific index operations

```bash
pytest tests/test_information_indexing.py -v
```

## See Also

- [README.md](../README.md) - Main module documentation
- [INTEGRATION_GUIDE.md](../INTEGRATION_GUIDE.md) - Integration instructions
- [example_information_indexing.py](example_information_indexing.py) - Complete workflow example
- [examples/](.) - Other usage examples
