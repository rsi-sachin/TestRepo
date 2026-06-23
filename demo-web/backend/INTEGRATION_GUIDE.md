# Intelligent Document Parsing - Integration Guide

This guide covers how to integrate and use the Intelligent Document Parsing module in your applications.

## Table of Contents

1. [Setup](#setup)
2. [Python API Usage](#python-api-usage)
3. [HTTP API Usage](#http-api-usage)
4. [Custom Rules](#custom-rules)
5. [User Feedback Loop](#user-feedback-loop)
6. [Database Integration](#database-integration-optional)
7. [Monitoring & Metrics](#monitoring--metrics)
8. [Troubleshooting](#troubleshooting)

## Setup

### Installation

The module is already integrated into demo-web. No additional installation needed.

**Dependencies (already installed):**
- `pypdf` (3.17.0) - PDF text extraction
- `pydantic` (2.13.4) - Data validation
- Standard library modules

### Verify Installation

```bash
# Test the module loads
python -c "from app.intelligent_document_parsing import DocumentAnalysisService; print('OK')"
```

## Python API Usage

### Basic Section Analysis

```python
from pathlib import Path
from app.intelligent_document_parsing import DocumentAnalysisService

# Initialize service
service = DocumentAnalysisService()

# Analyze a specific section
result = service.analyze_section(
    pdf_path=Path("C:\\TestRepo\\ORAN\\docs\\ts_103987v040300p.pdf"),
    section_number="4.1",           # Section to analyze
    subsection_depth=1              # Include direct subsections only
)

# Access results
print(f"Decisions: {len(result.decisions)}")
print(f"Action Items: {len(result.action_items)}")
print(f"Information Gaps: {len(result.information_gaps)}")

# Iterate over extractions
for decision in result.decisions:
    print(f"- {decision.title} (confidence: {decision.confidence:.2f})")
    print(f"  Type: {decision.decision_type.value}")
    print(f"  Keywords: {', '.join(decision.keywords)}")

# Export to JSON
json_output = result.to_json()
print(json_output)
```

### Full Document Analysis

```python
# Analyze entire document
result = service.analyze_document(
    pdf_path=Path("spec.pdf")
)

print(f"Total decisions: {len(result.decisions)}")
print(f"Total actions: {len(result.action_items)}")
print(f"Average confidence: {result._avg_confidence():.2f}")
```

### Save Results to File

```python
from pathlib import Path

output_path = Path("analysis_results.json")
service.export_analysis_results(result, output_path)
print(f"Results saved to {output_path}")
```

## HTTP API Usage

### Start Server

```bash
cd demo-web/backend
python -m app.main
```

Server runs at `http://localhost:8000`

API docs at `http://localhost:8000/api/docs`

### Analyze Section (HTTP)

```bash
curl -X POST "http://localhost:8000/api/v1/document-analysis/section" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_path": "C:\\TestRepo\\ORAN\\docs\\ts_103987v040300p.pdf",
    "section_number": "4.1",
    "subsection_depth": 1
  }'
```

**Response:**
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
      "section": "4.1",
      "page": 45
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

### Analyze Full Document

```bash
curl -X POST "http://localhost:8000/api/v1/document-analysis/document?pdf_path=spec.pdf"
```

### Get Health Status

```bash
curl http://localhost:8000/api/v1/document-analysis/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "intelligent-document-analysis",
  "version": "0.1.0"
}
```

## Custom Rules

### Add Rule via Python API

```python
from app.intelligent_document_parsing import ExtractionRule

# Define custom rule
rule = ExtractionRule(
    id="a1_interface_rule",
    name="A1 Interface Decisions",
    rule_type="decision",          # "decision", "action", or "gap"
    pattern=r"(?i)(A1\s+interface|A1\s+protocol|information\s+service)",
    confidence_boost=0.3           # Boost confidence when matched (0.0-1.0)
)

# Add to service
service.add_custom_extraction_rule(rule)

# Re-analyze with new rule
result = service.analyze_section(
    pdf_path=Path("spec.pdf"),
    section_number="4.1"
)
```

### Add Rule via HTTP API

```bash
curl -X POST "http://localhost:8000/api/v1/document-analysis/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_id": "my_rule_1",
    "rule_name": "Custom Domain Rule",
    "rule_type": "decision",
    "pattern": "(?i)(specific_term|important_phrase)",
    "confidence_boost": 0.25
  }'
```

### Rule Pattern Tips

- Use `(?i)` for case-insensitive matching
- Escape special regex characters: `\.`, `\(`, `\)`, `\*`, `\+`
- Test patterns: https://regex101.com/

**Example Patterns:**
```
# Match A1 interface mentions
(?i)(A1\s+interface|A1\s+protocol)

# Match action verbs
(?i)(implement|develop|create|test|verify)

# Match question phrases
(?i)(\bhow\s+|when\s+|what\s+)

# Match constraint keywords
(?i)(must\s+not|shall\s+not|cannot)
```

## User Feedback Loop

### Record Valid Extraction

```python
# User confirmed extraction is correct
service.validate_extraction(
    item_id="dec_123",
    is_valid=True,
    item_type="decision",
    feedback="Correctly identified this as a requirement"
)
```

### Record Invalid Extraction (False Positive)

```python
# User marked extraction as incorrect
service.validate_extraction(
    item_id="dec_456",
    is_valid=False,
    item_type="decision",
    feedback="This is not a decision, just background info",
    suggestion="Exclude introductory paragraphs"  # Optional
)
```

### Get Accuracy Metrics

```python
# Get accuracy report
metrics = service.get_accuracy_metrics()

print("Decision Accuracy:")
print(f"  Total validations: {metrics['decision']['total']}")
print(f"  Valid: {metrics['decision']['valid']}")
print(f"  Invalid: {metrics['decision']['invalid']}")
print(f"  Accuracy: {metrics['decision']['accuracy']:.2%}")

print("\nAction Items Accuracy:")
print(f"  Total: {metrics['action']['total']}")
print(f"  Accuracy: {metrics['action']['accuracy']:.2%}")
```

### Get Suggested Rules

```python
# Get AI-suggested rules from user feedback
suggestions = service.get_suggested_rules()

for suggestion in suggestions:
    print(f"Type: {suggestion['type']}")
    print(f"Pattern: {suggestion['pattern']}")
    print(f"Reason: {suggestion['reason']}")
    print(f"Confidence: {suggestion['confidence']:.2f}")
```

### Submit Feedback via HTTP

```bash
# Valid extraction
curl -X POST "http://localhost:8000/api/v1/document-analysis/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "dec_123",
    "item_type": "decision",
    "is_valid": true,
    "feedback_text": "Correct identification"
  }'

# Invalid extraction with suggestion
curl -X POST "http://localhost:8000/api/v1/document-analysis/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "act_456",
    "item_type": "action",
    "is_valid": false,
    "feedback_text": "Not an actionable item",
    "suggestion": "Exclude passive descriptions"
  }'
```

### Get Metrics via HTTP

```bash
curl http://localhost:8000/api/v1/document-analysis/metrics
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
    "action": {
      "total": 10,
      "valid": 9,
      "invalid": 1,
      "accuracy": 0.9
    },
    "gap": {
      "total": 5,
      "valid": 4,
      "invalid": 1,
      "accuracy": 0.8
    }
  }
}
```

## Database Integration (Optional)

### Store Feedback (Example with SQLAlchemy)

```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ExtractionFeedback(Base):
    __tablename__ = "extraction_feedback"
    
    id = Column(String, primary_key=True)
    item_id = Column(String, index=True)
    item_type = Column(String)  # "decision", "action", "gap"
    is_valid = Column(Boolean)
    feedback_text = Column(String)
    suggestion = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    @classmethod
    def from_feedback(cls, feedback: UserFeedback):
        return cls(
            id=f"{feedback.item_id}_{int(datetime.utcnow().timestamp())}",
            item_id=feedback.item_id,
            item_type=feedback.item_type,
            is_valid=feedback.is_valid,
            feedback_text=feedback.feedback_text,
            suggestion=feedback.suggested_correction
        )

# Save to database
db_session.add(ExtractionFeedback.from_feedback(feedback))
db_session.commit()
```

## Monitoring & Metrics

### Key Metrics to Track

```python
metrics = service.get_accuracy_metrics()

# Calculate quality score (0-100)
quality_score = 0
for item_type in ["decision", "action", "gap"]:
    accuracy = metrics[item_type]["accuracy"]
    quality_score += accuracy * 100 / 3

print(f"Overall Quality Score: {quality_score:.1f}/100")
```

### Export Metrics

```python
from pathlib import Path

output_path = Path("metrics_report.json")
service.export_feedback_metrics(output_path)
```

### Monitor via HTTP

```bash
# Get metrics every hour
while true; do
    curl http://localhost:8000/api/v1/document-analysis/metrics >> metrics_history.json
    sleep 3600
done
```

## Troubleshooting

### Issue: "PDF file not found"

```python
# Verify path exists
from pathlib import Path

pdf_path = Path("C:\\TestRepo\\ORAN\\docs\\ts_103987v040300p.pdf")
if not pdf_path.exists():
    print(f"File not found: {pdf_path}")
else:
    print(f"File found: {pdf_path}")
```

### Issue: "Section number not found"

```python
# Check available sections
from app.intelligent_document_parsing.core import SectionParser
from app.parsers.pdf_parser import PdfParser

pdf_parser = PdfParser()
text = pdf_parser.parse_file(Path("spec.pdf"))

section_parser = SectionParser()
section_parser.parse(text)

# Print all sections
section_parser.print_hierarchy()
```

### Issue: Low extraction confidence

```python
# Adjust heuristic method weights
from app.intelligent_document_parsing import ExtractionMethod

engine = service.extractor.heuristic_engine
engine.set_method_weights({
    ExtractionMethod.REGEX_KEYWORD: 0.3,      # Increase keyword weight
    ExtractionMethod.SENTENCE_PATTERN: 0.2,
    ExtractionMethod.TF_IDF_SCORING: 0.2,
    ExtractionMethod.RULE_BASED: 0.3,         # Increase rule weight
})

# Re-analyze
result = service.analyze_section(pdf_path, section_number)
```

### Issue: Too many false positives

```python
# Add exclusion rule
rule = ExtractionRule(
    id="exclude_background",
    name="Exclude Background",
    rule_type="decision",
    pattern=r"(?i)(background|note|example|illustration)",
    confidence_boost=-0.5  # Negative boost to decrease confidence
)

service.add_custom_extraction_rule(rule)

# Or collect feedback and get suggested rules
suggestions = service.get_suggested_rules()
```

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("app.intelligent_document_parsing")
logger.setLevel(logging.DEBUG)

# Now analyze - will show detailed logs
result = service.analyze_section(pdf_path, section_number)
```

## Performance Tips

### Optimize for Large Documents

```python
# Instead of analyzing entire document at once:
# ❌ service.analyze_document(path)

# Do this:
# ✅ Analyze sections individually
result = service.analyze_section(path, "4.1")  # Fast
result = service.analyze_section(path, "4.2")  # Fast
```

### Cache Results

```python
# Save expensive analyses
output_path = Path("cached_analysis_4_1.json")
if output_path.exists():
    with open(output_path) as f:
        cached_result = json.load(f)
else:
    result = service.analyze_section(path, "4.1")
    service.export_analysis_results(result, output_path)
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

def analyze_section(section_num):
    return service.analyze_section(Path("spec.pdf"), section_num)

# Analyze multiple sections in parallel
sections = ["4.1", "4.2", "4.3", "4.4"]
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(analyze_section, sections))
```

## Next Steps

1. **Test with Real Documents** - Try with actual PDF specs
2. **Collect User Feedback** - Record validations to improve accuracy
3. **Define Custom Rules** - Create domain-specific extraction patterns
4. **Integrate with UI** - Build web interface for analysis
5. **Monitor Metrics** - Track accuracy over time
6. **Database Persistence** - Store feedback for long-term learning

## Support

For issues or questions:
- Check logs: Enable DEBUG logging (see Troubleshooting)
- Review examples: `app/intelligent_document_parsing/examples/`
- Read source: Well-documented with docstrings
- Run tests: `pytest tests/test_intelligent_document_parsing.py`
