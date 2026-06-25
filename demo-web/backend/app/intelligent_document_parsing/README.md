# Intelligent Document Parsing

High-level AI/heuristic-based capability for extracting decisions, action items, and information gaps from specification documents **without using LLM APIs**.

## Overview

This module provides intelligent analysis of technical specifications and protocol documents using deterministic heuristics and machine-learning-style approaches:

- **Section Parsing** - Hierarchical extraction of sections and subsections at configurable depth
- **Multi-Method Heuristics** - 4 complementary extraction methods:
  - Regex keyword matching
  - Sentence structure pattern matching
  - TF-IDF semantic scoring
  - Rule-based heuristics
- **Extraction Types**:
  - **Decisions** - Requirements, constraints, design choices, configurations
  - **Action Items** - Tasks, implementation steps, with priority inference
  - **Information Gaps** - Ambiguities, missing clarifications, unknowns
- **User Feedback Loop** - Validate extractions and refine rules based on feedback
- **Custom Rules** - Define domain-specific extraction patterns
- **JSON Output** - Easy integration with other tools

## Quick Start

### Basic Usage

```python
from pathlib import Path
from app.intelligent_document_parsing import DocumentAnalysisService

service = DocumentAnalysisService()

# Analyze a specific section
result = service.analyze_section(
    pdf_path=Path("spec.pdf"),
    section_number="4.1",          # Section to analyze
    subsection_depth=1             # Include direct subsections
)

# Access results
print(f"Decisions: {len(result.decisions)}")
print(f"Actions: {len(result.action_items)}")
print(f"Gaps: {len(result.information_gaps)}")

# Export to JSON
result.to_json()
```

### Custom Extraction Rules

```python
from app.intelligent_document_parsing import ExtractionRule

rule = ExtractionRule(
    id="my_rule_1",
    name="My Custom Rule",
    rule_type="decision",
    pattern=r"(?i)(A1\s+interface|specific\s+protocol)",
    confidence_boost=0.2
)

service.add_custom_extraction_rule(rule)
```

### User Feedback & Rule Refinement

```python
# Validate an extraction
service.validate_extraction(
    item_id="dec_123",
    is_valid=True,
    item_type="decision",
    feedback="Correctly identified"
)

# Or mark as incorrect and suggest improvement
service.validate_extraction(
    item_id="dec_456",
    is_valid=False,
    item_type="decision",
    feedback="This is not a decision",
    suggestion="Exclude introductory paragraphs"
)

# Get accuracy metrics
metrics = service.get_accuracy_metrics()

# Get suggested rules from feedback
suggestions = service.get_suggested_rules()
```

## Architecture

```
intelligent_document_parsing/
├── core/                           # Core extraction logic
│   ├── section_parser.py           # Hierarchical section extraction
│   ├── heuristic_engine.py         # 4-method extraction engine
│   └── decision_extractor.py       # Main orchestration
├── services/                       # High-level services
│   ├── document_analysis_service.py # Public API facade
│   └── user_feedback_handler.py    # Feedback and rule refinement
├── models/                         # Data structures
│   └── analysis_models.py          # Decision, Action, Gap, etc.
├── utils/                          # Text processing utilities
│   └── text_utils.py               # Tokenization, keyword matching, etc.
├── examples/                       # Usage examples
│   └── ts_103987_a1_example.py    # Concrete usage patterns
├── __init__.py                     # Module entry point
└── README.md                       # This file
```

## Data Models

### Decision

```python
@dataclass
class Decision:
    id: str                          # Unique identifier
    title: str                       # Short description
    description: str                 # Full text
    decision_type: DecisionType      # REQUIREMENT, CONSTRAINT, etc.
    confidence: float                # 0.0 - 1.0
    evidence: List[Evidence]         # Supporting text snippets
    keywords: List[str]              # Extracted keywords
    user_validated: bool             # User feedback received
    user_feedback: Optional[str]     # User's comment
```

### ActionItem

```python
@dataclass
class ActionItem:
    id: str
    title: str
    description: str
    priority: ItemPriority           # CRITICAL, HIGH, MEDIUM, LOW
    confidence: float
    owner_hints: List[str]           # Role suggestions
    evidence: List[Evidence]
    user_validated: bool
    user_feedback: Optional[str]
```

### InformationGap

```python
@dataclass
class InformationGap:
    id: str
    title: str
    description: str
    impact: str                      # "critical", "high", "medium", "low"
    confidence: float
    evidence: List[Evidence]
    user_validated: bool
    user_feedback: Optional[str]
```

### AnalysisResult

```python
@dataclass
class AnalysisResult:
    document_name: str
    analyzed_section: str
    decisions: List[Decision]
    action_items: List[ActionItem]
    information_gaps: List[InformationGap]
    sections: List[Section]          # Hierarchical section tree
    heuristic_methods_used: List[ExtractionMethod]
    
    def to_json() -> str            # Export to JSON
```

## Extraction Methods

### 1. Regex Keyword Matching
Matches text containing domain keywords:
- **Decisions**: "shall", "must", "require", "specify", "define"
- **Actions**: "implement", "test", "verify", "configure", "deploy"
- **Gaps**: "unclear", "missing", "undefined", "unknown", "todo"

### 2. Sentence Structure Patterns
Matches common phrase patterns:
- `"<verb> <noun>"` patterns for actions
- `"shall/must <action>"` for requirements
- `"<concept> is unclear|missing|undefined"`

### 3. TF-IDF Semantic Scoring
Identifies semantically important terms within document context:
- High TF-IDF indicates domain-specific, important content
- Used to boost confidence of relevant extractions

### 4. Rule-Based Heuristics
User-defined regex patterns with confidence adjustments:
- Custom domain rules (e.g., "A1 interface")
- Feedback-driven rule suggestions
- Enables continuous improvement

## Configuration

### Method Weights

Adjust relative importance of heuristic methods:

```python
from app.intelligent_document_parsing import ExtractionMethod

service.heuristic_engine.set_method_weights({
    ExtractionMethod.REGEX_KEYWORD: 0.2,
    ExtractionMethod.SENTENCE_PATTERN: 0.3,
    ExtractionMethod.TF_IDF_SCORING: 0.3,
    ExtractionMethod.RULE_BASED: 0.2,
})
```

### Confidence Thresholds

Configure confidence cutoffs (internal to heuristic engine):
- Decisions: 0.4 (default)
- Actions: 0.4 (default)
- Gaps: 0.35 (lower, more permissive)

## Integration

### With Demo-Web Backend

```python
# In app/main.py or initialization
from app.intelligent_document_parsing import DocumentAnalysisService

doc_service = DocumentAnalysisService()

# Use in FastAPI routes
@app.post("/api/v1/document-analysis/section")
async def analyze_section(pdf_path: str, section: str):
    result = doc_service.analyze_section(Path(pdf_path), section)
    return json.loads(result.to_json())
```

## Examples

See `examples/` folder for complete working examples:

- **ts_103987_a1_example.py** - Real-world usage with ETSI TS 103987 Section 4

Run examples:
```bash
python examples/ts_103987_a1_example.py
```

## Output Format

### JSON Structure

```json
{
  "metadata": {
    "document": "ts_103987v040300p.pdf",
    "section": "4.1",
    "timestamp": "2026-06-23T10:30:00",
    "methods": ["regex_keyword", "sentence_pattern", "tfidf_scoring", "rule_based"]
  },
  "decisions": [
    {
      "id": "dec_abc123",
      "title": "A1 interface definition",
      "type": "requirement",
      "confidence": 0.85,
      "keywords": ["A1", "interface", "protocol"],
      "evidence_count": 1,
      "user_validated": false
    }
  ],
  "action_items": [
    {
      "id": "act_def456",
      "title": "Implement A1 protocol handler",
      "priority": "high",
      "confidence": 0.72,
      "owner_hints": ["developer", "team"],
      "evidence_count": 1
    }
  ],
  "information_gaps": [
    {
      "id": "gap_ghi789",
      "title": "A1 interface implementation details unclear",
      "impact": "high",
      "confidence": 0.65,
      "evidence_count": 2
    }
  ],
  "summary": {
    "total_decisions": 12,
    "total_actions": 8,
    "total_gaps": 5,
    "avg_confidence": 0.71
  }
}
```

## Files Structure

| File | Purpose |
|------|---------|
| `core/section_parser.py` | Extract document hierarchy |
| `core/heuristic_engine.py` | 4-method extraction scoring |
| `core/decision_extractor.py` | Main extraction orchestration |
| `services/document_analysis_service.py` | High-level public API |
| `services/user_feedback_handler.py` | Feedback collection & analysis |
| `models/analysis_models.py` | Data classes (Decision, Action, Gap, etc.) |
| `utils/text_utils.py` | Text processing utilities |
| `examples/ts_103987_a1_example.py` | Real-world usage patterns |

## Performance Notes

- No external API calls (no LLM dependency)
- Processes typical specification sections in < 1 second
- Memory: ~10-50 MB per document depending on size
- Fully deterministic (same input → same output)

## Extensibility

### Adding New Extraction Methods

Extend `HeuristicEngine`:
```python
def extract_with_custom_method(self, text: str) -> List[Tuple[str, float, List[str]]]:
    # Your implementation
    pass
```

### Custom Domain Rules

Define patterns specific to your domain:
```python
ExtractionRule(
    id="my_domain_rule",
    name="Domain-Specific Decisions",
    rule_type="decision",
    pattern=r"(?i)(your_domain_keyword|specific_pattern)",
    confidence_boost=0.25
)
```

## Future Enhancements

- [ ] Support for Word, Markdown, HTML documents
- [ ] Relationship extraction (decision → actions → gaps)
- [ ] Traceability matrix generation
- [ ] REST API endpoints for document upload
- [ ] Database persistence for feedback and rules
- [ ] Machine learning model training from user feedback
- [ ] Batch document processing

## Testing

```bash
# Run tests (when available)
pytest app/intelligent_document_parsing/tests/
```

## Contributing

1. Add new extraction methods to `HeuristicEngine`
2. Add unit tests in `tests/` folder
3. Update examples in `examples/` folder
4. Document in README.md

## License

Part of demo-web project. See main project LICENSE.
