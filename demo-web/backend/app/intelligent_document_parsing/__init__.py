"""
Intelligent Document Parsing Module

High-level AI/heuristic-based capability for extracting decisions, action items,
and information gaps from specification documents without using LLM APIs.

**Features:**
- Section and subsection extraction at configurable depth levels
- Multi-method heuristic analysis (regex, patterns, TF-IDF, rules)
- Decision, action item, and information gap extraction
- User feedback loop for continuous rule refinement
- Custom extraction rules support
- JSON output format for integration
- Global and document-specific information indexing
- Reference document discovery and tracking

**Quick Start:**
```python
from app.intelligent_document_parsing import (
    DocumentAnalysisService,
    InformationIndexManager,
    populate_global_index_from_section_4_1,
)

service = DocumentAnalysisService()
result = service.analyze_section(
    pdf_path=Path("ts_103987v040300p.pdf"),
    section_number="4.1",
    subsection_depth=1
)

# Index extraction results
index_manager = InformationIndexManager()
populate_global_index_from_section_4_1(index_manager, result)
```

**Key Components:**
- `core/section_parser.py` - Section hierarchy extraction
- `core/heuristic_engine.py` - 4-method extraction engine
- `core/decision_extractor.py` - Orchestration and extraction
- `services/document_analysis_service.py` - High-level API
- `services/user_feedback_handler.py` - Feedback and rule refinement
- `services/information_index_manager.py` - Global/document indexes
- `services/reference_document_resolver.py` - Reference discovery
- `services/information_index_integrator.py` - Integration helpers
- `models/analysis_models.py` - Data structures
- `models/information_index_models.py` - Index data models
- `utils/text_utils.py` - Text processing utilities

**Integration:**
See `examples/` for usage patterns and `README.md` for full documentation.
"""

from app.intelligent_document_parsing.services import (
    DocumentAnalysisService,
    UserFeedbackHandler,
    InformationIndexManager,
    ReferenceDocumentResolver,
    create_reference_resolver,
    create_global_fact_from_decision,
    create_global_facts_from_analysis,
    extract_referenced_documents,
    create_document_specific_facts,
    populate_global_index_from_section_4_1,
    create_postponed_action_item_for_reference_retrieval,
)
from app.intelligent_document_parsing.models import (
    AnalysisResult,
    Decision,
    ActionItem,
    InformationGap,
    GlobalFact,
    ReferenceDocument,
    GlobalInformationIndex,
    DocumentSpecificIndex,
    ActionItemRecord,
    ItemStatus,
    ReferenceStatus,
)
from app.intelligent_document_parsing.core import (
    DecisionExtractor,
    ExtractionRule,
)

__all__ = [
    # Analysis services
    'DocumentAnalysisService',
    'UserFeedbackHandler',
    'InformationIndexManager',
    'ReferenceDocumentResolver',
    'create_reference_resolver',
    # Analysis models
    'AnalysisResult',
    'Decision',
    'ActionItem',
    'InformationGap',
    # Information index models
    'GlobalFact',
    'ReferenceDocument',
    'GlobalInformationIndex',
    'DocumentSpecificIndex',
    'ActionItemRecord',
    'ItemStatus',
    'ReferenceStatus',
    # Integration functions
    'create_global_fact_from_decision',
    'create_global_facts_from_analysis',
    'extract_referenced_documents',
    'create_document_specific_facts',
    'populate_global_index_from_section_4_1',
    'create_postponed_action_item_for_reference_retrieval',
    # Core components
    'DecisionExtractor',
    'ExtractionRule',
]

__version__ = '0.2.0'
__description__ = 'Intelligent document parsing and analysis with information indexing'
