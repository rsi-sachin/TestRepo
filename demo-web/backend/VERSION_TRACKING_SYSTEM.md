# Semantic Version Tracking & Module Impact Analysis

## Overview

This feature enables detection of ETSI specification version changes and automatic identification of source code modules that may require updates based on version semantics.

## Architecture

### Components

1. **SemanticVersionTracker** (`app/services/semantic_version_tracker.py`)
   - Tracks specification versions across multiple documents
   - Detects version changes (major/minor/patch)
   - Assesses backward compatibility per TS 103987 Section 4.2 rules
   - Generates version history and diff reports

2. **ModuleImpactAnalyzer** (`app/services/module_impact_analyzer.py`)
   - Maps specification sections to source code modules/functions
   - Analyzes impact of version changes on codebase
   - Generates impact reports with severity levels
   - Estimates effort for required updates

3. **SpecParserService Integration**
   - `detect_and_analyze_version_changes()` placeholder method
   - Integrates version tracking into spec processing workflow
   - Triggered when processing new/updated specification files

## Version Semantics (TS 103987 Section 4.2)

Version format: `MAJOR.MINOR.PATCH` (e.g., `4.3.0`)

### Versioning Rules

| Component | Increment | Meaning | Compatibility |
|-----------|-----------|---------|---|
| **MAJOR** (1st digit) | New major feature OR incompatible change | Breaking change | ❌ Breaking |
| **MINOR** (2nd digit) | Optional features, clarifications, corrections | Backward compatible | ✅ Backward compatible |
| **PATCH** (3rd digit) | Bug fixes | Backward compatible | ✅ Backward compatible |

### Compatibility Assessment

- **FULLY_COMPATIBLE**: Same major version, identical versions
- **PARTIALLY_COMPATIBLE**: Same major, different minor/patch
- **BREAKING**: Different major versions

## Module Mapping

### Spec Dependencies Structure

```
SpecDependency:
  spec_type: "TS_103987"
  spec_section: "6.2"
  section_title: "A1-P (policy management)"
  module_references:
    - ModuleReference(
        module_path: "app/api/a1_policy.py"
        function_name: "put_policy"
        spec_clause: "6.2.2"
        implementation_type: "endpoint"
      )
```

### Implementation Types

- **endpoint**: FastAPI route/controller
- **service**: Business logic service
- **model**: Pydantic data model
- **validator**: Input/output validator

## Impact Analysis

### Impact Severity

- **CRITICAL**: Breaking change affects API contract
- **HIGH**: Affects core functionality
- **MEDIUM**: Affects implementation details
- **LOW**: Documentation/comments update

### Update Types

- **API_SIGNATURE**: Function signature changed
- **BEHAVIOR_CHANGE**: Implementation changed
- **NEW_FEATURE**: New endpoint/function needed
- **DEPRECATION**: Function deprecated
- **DATA_MODEL**: Data structure changed
- **VALIDATION**: Validation rules changed
- **ERROR_HANDLING**: Error codes/responses changed

## Usage

### Basic Version Tracking

```python
from app.services.semantic_version_tracker import SemanticVersionTracker, SemanticVersion

tracker = SemanticVersionTracker()

# Register a document version
version = SemanticVersion.parse("v4.3.0", "TS_103987")
tracker.register_document("TS_103987", version)

# Save history
tracker.save_history()

# Get version report
report = tracker.get_version_diff_report()
```

### Impact Analysis

```python
from app.services.module_impact_analyzer import ModuleImpactAnalyzer

analyzer = ModuleImpactAnalyzer()

# Analyze impact of a version change
impact = analyzer.analyze_impact(
    spec_type="TS_103987",
    from_version="4.2.0",
    to_version="4.3.0",
    change_type="major"
)

# Generate readable report
report = analyzer.generate_impact_report(impact)
print(report)
```

### Integration with SpecParserService

```python
from app.services.spec_parser_service import SpecParserService
from pathlib import Path

parser = SpecParserService(spec_dir=Path("./specs"))

# Detect version changes when processing new specs
result = parser.detect_and_analyze_version_changes(
    file_path=Path("ts_103987v040300p.pdf"),
    spec_type="TS_103987"
)

if result:
    print(f"Version: {result['from_version']} → {result['to_version']}")
    print(f"Breaking: {result['is_breaking']}")
    print(result['impact_report'])
```

## Data Persistence

### Version History File

Location: `data/oran_learning/version_history.json`

Format:
```json
{
  "timestamp": "2026-06-24T12:00:00",
  "documents": {
    "TS_103987": {
      "current_version": "4.3.0",
      "version_history": ["4.2.0", "4.1.0"],
      "changes": [
        {
          "change_type": "minor",
          "from_version": "4.2.0",
          "to_version": "4.3.0",
          "compatibility": "partially_compatible",
          "breaking": false,
          "timestamp": "2026-06-24T12:00:00"
        }
      ]
    }
  }
}
```

## Current Status

### ✅ Implemented (Placeholder)

- [x] SemanticVersionTracker class with full version tracking logic
- [x] ModuleImpactAnalyzer class with impact analysis logic
- [x] Module mapping framework for spec sections → code modules
- [x] Integration stubs in SpecParserService
- [x] Version persistence (JSON-based)

### 🔄 TODO

- [ ] Extract actual API endpoint mappings from codebase
- [ ] Implement `detect_and_analyze_version_changes()` in SpecParserService
- [ ] Add API endpoints for querying version history and impact analysis
- [ ] Create CLI commands for generating reports
- [ ] Database models for persistent storage (optional)
- [ ] Test coverage with real specification files
- [ ] Integration with CI/CD pipeline for version validation

## Example Output

### Version Diff Report

```
================================================================================
DOCUMENT VERSIONS TRACKED
================================================================================
TS_103987: 4.2.0 → 4.3.0 (MINOR change)
TS_103988: 2.1.0 (no change)
TS_103989: 1.0.0 → 2.0.0 (MAJOR change - BREAKING)

Total version changes: 2
Total breaking changes: 1
```

### Impact Report

```
================================================================================
MODULE IMPACT ANALYSIS: TS_103987
Version Change: 4.2.0 → 4.3.0
Change Type: MINOR
================================================================================

Affected Modules (3):
  • app/api/a1_policy.py
    - put_policy [medium] (new_feature)
    - get_policy [medium] (new_feature)
  • app/models/policy_model.py
    - PolicyObject [medium] (data_model)

Estimated Effort: 1 story point

Affected APIs:
  • app/api/a1_policy.py:put_policy
  • app/api/a1_policy.py:get_policy
  • app/models/policy_model.py:PolicyObject
```

## Integration Points

1. **Spec Upload Workflow**
   - Trigger version detection after PDF/DOCX upload
   - Flag breaking changes in UI

2. **CI/CD Pipeline**
   - Validate spec versions match released versions
   - Trigger code review for breaking changes

3. **Documentation**
   - Auto-generate migration guides for major versions
   - Link to affected source code in release notes

4. **Monitoring**
   - Track spec version compliance across deployments
   - Alert on breaking changes
