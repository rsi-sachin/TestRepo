# API Quick Reference

## Python API

### Import
```python
from app.intelligent_document_parsing import (
    DocumentAnalysisService,
    DecisionExtractor,
    ExtractionRule,
    UserFeedbackHandler,
)
```

### Initialize Service
```python
service = DocumentAnalysisService()
```

### Analyze Section
```python
result = service.analyze_section(
    pdf_path=Path("spec.pdf"),
    section_number="4.1",
    subsection_depth=1
)
```

### Analyze Full Document
```python
result = service.analyze_document(pdf_path=Path("spec.pdf"))
```

### Add Custom Rule
```python
rule = ExtractionRule(
    id="rule_id",
    name="Rule Name",
    rule_type="decision",  # "decision", "action", "gap"
    pattern=r"(?i)keyword",
    confidence_boost=0.2
)
service.add_custom_extraction_rule(rule)
```

### Record Feedback
```python
# Valid extraction
service.validate_extraction(
    item_id="dec_123",
    is_valid=True,
    item_type="decision",
    feedback="Correct"
)

# Invalid extraction
service.validate_extraction(
    item_id="act_456",
    is_valid=False,
    item_type="action",
    feedback="Not an action",
    suggestion="exclude_pattern"
)
```

### Get Metrics
```python
metrics = service.get_accuracy_metrics()
# Returns: {"decision": {...}, "action": {...}, "gap": {...}}
```

### Get Suggested Rules
```python
suggestions = service.get_suggested_rules()
# Returns: [{"type": "exclusion_rule", "pattern": "...", ...}]
```

### Export Results
```python
service.export_analysis_results(result, Path("output.json"))
service.export_feedback_metrics(Path("metrics.json"))
```

### Access Results
```python
# Decisions
for decision in result.decisions:
    print(decision.title)
    print(decision.confidence)
    print(decision.decision_type.value)

# Actions
for action in result.action_items:
    print(action.title)
    print(action.priority.value)

# Gaps
for gap in result.information_gaps:
    print(gap.title)
    print(gap.impact)

# JSON
json_string = result.to_json()
```

## HTTP API

### Base URL
```
http://localhost:8000/api/v1/document-analysis
```

### Analyze Section
```
POST /section
?pdf_path=path/to/file.pdf
&section_number=4.1
&subsection_depth=1
```

**Response:**
```json
{
  "metadata": {...},
  "decisions": [...],
  "action_items": [...],
  "information_gaps": [...],
  "summary": {...}
}
```

### Analyze Document
```
POST /document
?pdf_path=path/to/file.pdf
```

### Add Rule
```
POST /rules
?rule_id=rule_1
&rule_name=My Rule
&rule_type=decision
&pattern=(?i)keyword
&confidence_boost=0.2
```

**Response:**
```json
{
  "status": "success",
  "message": "Rule 'My Rule' added",
  "rule_id": "rule_1"
}
```

### Submit Feedback
```
POST /feedback
?item_id=dec_123
&item_type=decision
&is_valid=true
&feedback_text=Correct
&suggestion=null
```

**Response:**
```json
{
  "status": "success",
  "message": "Feedback recorded",
  "item_id": "dec_123"
}
```

### Get Metrics
```
GET /metrics
```

**Response:**
```json
{
  "status": "success",
  "metrics": {
    "decision": {
      "total": 15,
      "valid": 12,
      "invalid": 3,
      "accuracy": 0.8
    },
    ...
  }
}
```

### Get Suggested Rules
```
GET /suggested-rules
```

**Response:**
```json
{
  "status": "success",
  "suggestions": [
    {
      "type": "exclusion_rule",
      "pattern": "...",
      "reason": "...",
      "confidence": 0.7
    }
  ],
  "count": 2
}
```

### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "service": "intelligent-document-analysis",
  "version": "0.1.0"
}
```

## Data Models

### Decision Types
- `requirement` - Formal requirement
- `constraint` - Limitation or restriction
- `design_decision` - Architectural choice
- `configuration` - Setup specification
- `process` - Procedural step
- `standard` - Standard conformance
- `best_practice` - Recommended approach
- `other` - Unclassified

### Priority Levels
- `critical` - Must implement
- `high` - Important
- `medium` - Should do
- `low` - Optional

### Extraction Methods
- `regex_keyword` - Keyword matching
- `sentence_pattern` - Pattern matching
- `tfidf_scoring` - Semantic scoring
- `rule_based` - Custom rules

### Item Types
- `decision` - Extracted decision
- `action` - Action item
- `gap` - Information gap

## Common Workflows

### Workflow 1: Analyze Section and Export
```python
service = DocumentAnalysisService()
result = service.analyze_section(pdf, "4.1")
service.export_analysis_results(result, Path("output.json"))
```

### Workflow 2: Add Rule and Re-Analyze
```python
rule = ExtractionRule("id", "name", "decision", r"pattern")
service.add_custom_extraction_rule(rule)
result = service.analyze_section(pdf, "4.1")
```

### Workflow 3: Collect Feedback and Get Metrics
```python
service.validate_extraction(item_id, True, "decision", "Correct")
service.validate_extraction(item_id, False, "decision", "Wrong", "exclude")
metrics = service.get_accuracy_metrics()
suggestions = service.get_suggested_rules()
```

### Workflow 4: Batch Process Sections
```python
sections = ["4.1", "4.2", "4.3"]
results = [service.analyze_section(pdf, s) for s in sections]
for result in results:
    service.export_analysis_results(result, Path(f"{result.analyzed_section}.json"))
```

## Extraction Configuration

### Method Weights
```python
engine = service.extractor.heuristic_engine
engine.set_method_weights({
    ExtractionMethod.REGEX_KEYWORD: 0.25,
    ExtractionMethod.SENTENCE_PATTERN: 0.25,
    ExtractionMethod.TF_IDF_SCORING: 0.25,
    ExtractionMethod.RULE_BASED: 0.25,
})
```

### Confidence Thresholds (internal)
- Decisions: 0.4 minimum
- Actions: 0.4 minimum
- Gaps: 0.35 minimum

## Regex Patterns for Rules

```
# A1 Protocol
(?i)(A1\s+interface|A1\s+protocol)

# Action verbs
(?i)(implement|develop|test|verify|configure)

# Gap keywords
(?i)(unclear|missing|undefined|ambiguous)

# Constraint
(?i)(must\s+not|shall\s+not|cannot)

# Requirement
(?i)(shall|must|require)
```

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 404 | PDF file not found | Check file path exists |
| 400 | Invalid section/parameter | Verify section number format |
| 500 | Analysis failed | Check logs, verify PDF readable |

## Performance Tips

- Analyze sections individually (faster than full document)
- Cache results to avoid re-analysis
- Use parallel processing for multiple sections
- Monitor metrics regularly
- Add custom rules to improve accuracy

## Debugging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Analyze with detailed logs
result = service.analyze_section(pdf, "4.1")
```

## Documentation Links

- **Full README:** `app/intelligent_document_parsing/README.md`
- **Integration Guide:** `INTEGRATION_GUIDE.md`
- **Implementation Summary:** `IMPLEMENTATION_SUMMARY.md`
- **Feature Registry:** `FEATURES.md`
- **Examples:** `app/intelligent_document_parsing/examples/`
