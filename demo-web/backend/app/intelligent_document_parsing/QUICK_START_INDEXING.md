# Information Indexing Quick Start Guide

## 5-Minute Setup

### 1. Import the System
```python
from app.intelligent_document_parsing import (
    DocumentAnalysisService,
    InformationIndexManager,
    populate_global_index_from_section_4_1,
)
from pathlib import Path
```

### 2. Analyze a Section
```python
service = DocumentAnalysisService()
result = service.analyze_section(
    pdf_path=Path("C:/TestRepo/ORAN/docs/ts_103987v040300p.pdf"),
    section_number="4.1",
    subsection_depth=1
)

print(f"Found: {len(result.decisions)} decisions")
print(f"Found: {len(result.action_items)} actions")
print(f"Found: {len(result.information_gaps)} gaps")
```

### 3. Initialize Index Manager
```python
index_manager = InformationIndexManager()
# Creates/loads: ./data/indexes/global_information_index.json
```

### 4. Populate Global Index
```python
populate_global_index_from_section_4_1(index_manager, result)

# Check what was added
summary = index_manager.export_summary()
print(f"Facts in index: {summary['global_index']['facts_count']}")
print(f"References found: {summary['global_index']['references_count']}")
```

### 5. Query the Index
```python
from app.intelligent_document_parsing.models import ItemStatus

# Get all completed facts (highest priority)
completed = index_manager.get_completed_facts()

# Get facts from a specific section
section_facts = index_manager.get_facts_by_section(
    "ts_103987v040300p", "4.1"
)

# Get facts matching keywords
facts = index_manager.get_facts_by_keywords(["HTTP", "REST", "protocol"])

# Get draft facts awaiting review
draft = index_manager.get_facts_by_status(ItemStatus.DRAFT)
```

## Common Tasks

### Export Index to File
```python
import json
from pathlib import Path

global_index = index_manager.get_global_index()
output = Path("my_index_export.json")
with open(output, 'w') as f:
    f.write(global_index.to_json())
```

### Create Document-Specific Index
```python
doc_index = index_manager.create_document_specific_index(
    document_id="ts_103987v040300p",
    document_name="ts_103987v040300p",
    document_version="4.3.0",
    document_path="C:/TestRepo/ORAN/docs/ts_103987v040300p.pdf"
)

# Add facts organized by section
from app.intelligent_document_parsing import create_document_specific_facts
facts_by_section = create_document_specific_facts(result, "4.3.0")
doc_index.facts_by_section = facts_by_section

# Save to file
index_manager.save_document_specific_index(doc_index)
```

### Handle Referenced Documents
```python
from app.intelligent_document_parsing.services import create_reference_resolver

# Create resolver
resolver = create_reference_resolver(index_manager)

# Get unresolved references
global_idx = index_manager.get_global_index()
for ref in global_idx.references:
    print(f"{ref.reference_id}: {ref.reference_name}")
    print(f"  Status: {ref.status.value}")
    print(f"  Found in: {ref.discovered_in_documents}")
```

### Create Postponed Action Items
```python
from app.intelligent_document_parsing import (
    create_postponed_action_item_for_reference_retrieval
)

# For each unresolved reference, create an action
for ref in global_idx.references:
    if ref.status.value == "not_found":
        action = create_postponed_action_item_for_reference_retrieval(
            reference_id=ref.reference_id,
            document_context="Section 4.1 of ts_103987v040300p",
            index_manager=index_manager
        )
        index_manager.add_action_item(action)

# View pending approvals
pending = index_manager.get_pending_approvals()
for action in pending:
    print(f"⏳ {action.title}")
    print(f"   Priority: {action.priority}")
```

## Data Models Reference

### GlobalFact
```python
{
    "fact_id": "fact_abc123",
    "title": "REST Architecture Selected",
    "description": "Design uses REST...",
    "type": "design_decision",
    "status": "draft",  # draft, pending_user_approval, scheduled, completed
    "confidence": 0.85,
    "evidence_links": [
        {
            "source_document": "ts_103987v040300p",
            "section": "4.1",
            "page": 42,
            "confidence": 0.85
        }
    ],
    "keywords": ["REST", "HTTP", "architecture"]
}
```

### ReferenceDocument
```python
{
    "reference_id": "A1TP",
    "reference_name": "A1 Technical Protocol",
    "status": "not_found",  # not_found, found_public, retrieved, error, etc
    "discovered_in_documents": ["ts_103987v040300p"],
    "discovered_sections": ["4.1"],
    "url_template": "https://example.com/a1tp/{version}.pdf"
}
```

### ActionItemRecord
```python
{
    "action_id": "action_001",
    "title": "Retrieve and analyze reference document: A1TP",
    "description": "Locate and process A1TP...",
    "status": "pending_user_approval",  # Same lifecycle as facts
    "priority": "high",  # critical, high, medium, low
    "related_documents": ["A1TP"],
    "created_date": "2026-06-23T..."
}
```

## File Locations

### Index Files
```
./data/indexes/
  ├── global_information_index.json         # Main index (all documents)
  ├── action_items_log.json                 # Postponed tasks
  └── ts_103987v040300p_information_index.json  # Document-specific
```

### Source Code
```
app/intelligent_document_parsing/
  ├── models/
  │   └── information_index_models.py       # Data model classes
  ├── services/
  │   ├── information_index_manager.py      # Index operations
  │   ├── reference_document_resolver.py    # Reference discovery
  │   └── information_index_integrator.py   # Helper functions
  ├── examples/
  │   └── example_information_indexing.py   # Complete examples
  └── docs/
      └── INFORMATION_INDEXING.md           # Full documentation
```

## Status Lifecycle

### Fact Statuses
```
DRAFT → PENDING_APPROVAL → SCHEDULED → COMPLETED
└─ New extractions      └─ User review   └─ Ready for prod
```

### Reference Statuses
```
NOT_FOUND → {FOUND_PUBLIC | PROPRIETARY | ERROR}
                      ↓
                  SCHEDULED
                      ↓
                  RETRIEVED
```

## Filtering Examples

```python
# Get facts by status
from app.intelligent_document_parsing.models import ItemStatus

draft = index_manager.get_facts_by_status(ItemStatus.DRAFT)
completed = index_manager.get_facts_by_status(ItemStatus.COMPLETED)

# Get facts from a document
doc_facts = index_manager.get_facts_by_document("ts_103987v040300p")

# Get facts from a section
section_facts = index_manager.get_facts_by_section(
    "ts_103987v040300p", "4.1"
)

# Get facts by keywords (case-insensitive)
rest_facts = index_manager.get_facts_by_keywords(["REST", "HTTP"])
```

## Troubleshooting

### Index File Corrupted
```python
# Delete corrupted file and reinitialize
from pathlib import Path
index_file = Path("./data/indexes/global_information_index.json")
if index_file.exists():
    index_file.unlink()  # Delete file

# Reinitialize
index_manager = InformationIndexManager()
# New empty index created automatically
```

### Reference Not Found
```python
# Check if resolver can locate it
resolver = create_reference_resolver(index_manager)
ref = resolver.locate_reference_document("A1TP")

if ref is None:
    print("Reference not found in known patterns")
    # Add to index_manager manually if known
```

### Action Item Not Found
```python
# Get all action items
all_actions = index_manager._action_items  # All loaded actions

# Find by ID
action = next((a for a in all_actions if a.action_id == "action_001"), None)
```

## Complete Example

```python
#!/usr/bin/env python3
"""Complete workflow example."""

from pathlib import Path
from app.intelligent_document_parsing import (
    DocumentAnalysisService,
    InformationIndexManager,
    populate_global_index_from_section_4_1,
)

# 1. Analyze document
print("Analyzing Section 4.1...")
service = DocumentAnalysisService()
result = service.analyze_section(
    pdf_path=Path("ts_103987v040300p.pdf"),
    section_number="4.1"
)

# 2. Populate indexes
print("Populating indexes...")
index_manager = InformationIndexManager()
populate_global_index_from_section_4_1(index_manager, result)

# 3. Export results
print("Exporting summary...")
summary = index_manager.export_summary()

print(f"\n✓ Analysis Complete")
print(f"  Facts: {summary['global_index']['facts_count']}")
print(f"  References: {summary['global_index']['references_count']}")
print(f"  Pending Actions: {summary['action_items']['by_status'].get('pending_user_approval', 0)}")

# 4. Query examples
facts = index_manager.get_facts_by_section("ts_103987v040300p", "4.1")
print(f"\n✓ Facts from Section 4.1: {len(facts)}")
for fact in facts[:3]:
    print(f"  - {fact.title} ({fact.confidence:.2f})")
```

## Next Steps

1. ✅ Run the complete example above
2. ✅ Modify to analyze different sections
3. ✅ Add custom extraction rules for domain-specific patterns
4. ✅ Process additional documents and watch index grow
5. ✅ Implement reference resolver placeholders
6. ✅ Integrate with your analysis pipeline

## Support

- See `INFORMATION_INDEXING.md` for complete API reference
- See `examples/example_information_indexing.py` for full workflows
- Run tests: `pytest tests/test_information_indexing.py -v`
- Check repository memory for implementation notes
