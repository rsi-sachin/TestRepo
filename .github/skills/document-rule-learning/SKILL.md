---
name: document-rule-learning
description: "Learn and reuse document-type interpretation rules for methodology extraction. Use when analyzing a new spec and when applying previously learned extraction, scoring, and domain rules to similar specs or protocols."
argument-hint: "document type or protocol family"
user-invocable: true
---

# Document Rule Learning

## Purpose
Store reusable document-type rules and apply them automatically to similar documents in future runs.

## Use When
- A new document type is analyzed and extraction behavior should be captured for reuse.
- A similar document appears and prior extraction/interpretation/domain rules should be applied automatically.
- Protocol or interface changes but section structure and writing style are similar.

## Rule Groups
Capture three reusable rule groups:

1. Extraction rules
- Section boundary patterns
- Heading/title patterns
- Candidate phrase patterns

2. Interpretation rules
- Confidence weighting signals
- Ranking and tie-break strategy
- Deduplication thresholds and normalization

3. Domain rules
- Keyword-to-module mappings
- Generic phrase blocklists
- Preferred title/action verb patterns

## Procedure
1. Detect document fingerprint
- Spec family, interface/protocol context, numbering style, heading depth profile.

2. Find closest learned rule pack
- Match by spec family first, then by structure similarity and top keywords.

3. Apply learned rule pack
- Run extraction and scoring using selected rule groups.

4. Validate extraction quality
- Compare section/module/title output volume and confidence against expected ranges.

5. Store learning metadata
- Persist fingerprint, quality signals, and extracted rule behavior.

6. Reuse on future docs
- Auto-select latest matching rule pack for similar documents.

## Expected Metadata Fields
- metadata_id
- created_at
- document_fingerprint
- learned_rules
- quality_signals
- reuse_hints

## Integration Notes
- Keep reusable rule metadata in version-controlled project files where possible.
- Also persist runtime snapshots after each analysis for continuous learning.
- Prefer deterministic rules first; use heuristic ranking as a secondary signal.
