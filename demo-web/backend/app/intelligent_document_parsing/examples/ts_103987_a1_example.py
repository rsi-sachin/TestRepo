"""
Example: Analyze ETSI TS 103987 Section 4 (A1 Application Protocol)
"""

from pathlib import Path
from app.intelligent_document_parsing import (
    DocumentAnalysisService,
    DecisionExtractor,
    ExtractionRule,
)


def example_basic_analysis():
    """Basic example: Analyze Section 4.1 of ts_103987v040300p.pdf"""
    print("=" * 70)
    print("Example 1: Basic Section Analysis")
    print("=" * 70)
    
    service = DocumentAnalysisService()
    
    pdf_path = Path("C:\\TestRepo\\ORAN\\docs\\ts_103987v040300p.pdf")
    
    # Analyze Section 4.1 Introduction
    result = service.analyze_section(
        pdf_path=pdf_path,
        section_number="4.1",
        subsection_depth=1
    )
    
    print(f"\nDocument: {result.document_name}")
    print(f"Section Analyzed: {result.analyzed_section}")
    print(f"Subsections Found: {len(result.sections)}")
    
    print(f"\n\nDecisions Found: {len(result.decisions)}")
    for i, decision in enumerate(result.decisions[:3], 1):
        print(f"\n  [{i}] {decision.title}")
        print(f"      Type: {decision.decision_type.value}")
        print(f"      Confidence: {decision.confidence:.2f}")
        print(f"      Keywords: {', '.join(decision.keywords)}")
    
    print(f"\n\nAction Items Found: {len(result.action_items)}")
    for i, action in enumerate(result.action_items[:3], 1):
        print(f"\n  [{i}] {action.title}")
        print(f"      Priority: {action.priority.value}")
        print(f"      Confidence: {action.confidence:.2f}")
    
    print(f"\n\nInformation Gaps Found: {len(result.information_gaps)}")
    for i, gap in enumerate(result.information_gaps[:3], 1):
        print(f"\n  [{i}] {gap.title}")
        print(f"      Impact: {gap.impact}")
        print(f"      Confidence: {gap.confidence:.2f}")
    
    # Export results
    output_path = Path("C:\\TestRepo\\demo-web\\backend\\examples\\analysis_output.json")
    service.export_analysis_results(result, output_path)
    print(f"\n\nResults exported to: {output_path}")
    
    return result


def example_custom_rules():
    """Example: Add custom extraction rules"""
    print("\n" + "=" * 70)
    print("Example 2: Custom Extraction Rules")
    print("=" * 70)
    
    service = DocumentAnalysisService()
    
    # Add custom rule for A1 interface specifics
    rule = ExtractionRule(
        id="a1_interface_rule",
        name="A1 Interface Decisions",
        rule_type="decision",
        pattern=r"(?i)(A1\s+interface|A1\s+protocol|information\s+service)",
        confidence_boost=0.3
    )
    
    service.add_custom_extraction_rule(rule)
    print(f"Added custom rule: {rule.name}")
    
    # Re-analyze with custom rule
    pdf_path = Path("C:\\TestRepo\\ORAN\\docs\\ts_103987v040300p.pdf")
    result = service.analyze_section(
        pdf_path=pdf_path,
        section_number="4.1"
    )
    
    print(f"\nWith custom rule applied:")
    print(f"  Decisions found: {len(result.decisions)}")
    print(f"  Average confidence: {result._avg_confidence():.2f}")
    
    return result


def example_user_feedback():
    """Example: Collect and analyze user feedback"""
    print("\n" + "=" * 70)
    print("Example 3: User Feedback & Rule Refinement")
    print("=" * 70)
    
    service = DocumentAnalysisService()
    
    # Simulate user validating extractions
    print("\nRecording user feedback...")
    
    service.validate_extraction(
        item_id="dec_abc123",
        is_valid=True,
        item_type="decision",
        feedback="Correctly identified this as a requirement"
    )
    
    service.validate_extraction(
        item_id="dec_xyz789",
        is_valid=False,
        item_type="decision",
        feedback="This is not a decision, just background",
        suggestion="Exclude background paragraphs"
    )
    
    service.validate_extraction(
        item_id="act_def456",
        is_valid=True,
        item_type="action",
        feedback="Good action extraction"
    )
    
    # Get accuracy metrics
    metrics = service.get_accuracy_metrics()
    print("\nAccuracy Report:")
    for item_type, stats in metrics.items():
        print(f"\n  {item_type.upper()}:")
        print(f"    Total validations: {stats['total']}")
        print(f"    Valid: {stats['valid']}")
        print(f"    Invalid: {stats['invalid']}")
        print(f"    Accuracy: {stats['accuracy']:.2%}")
    
    # Get suggested rules
    suggestions = service.get_suggested_rules()
    print(f"\n\nSuggested Rules from Feedback ({len(suggestions)}):")
    for i, rule in enumerate(suggestions, 1):
        print(f"\n  [{i}] {rule.get('reason', 'N/A')}")
        print(f"      Pattern: {rule.get('pattern', 'N/A')[:50]}...")
    
    # Export metrics
    output_path = Path("C:\\TestRepo\\demo-web\\backend\\examples\\feedback_metrics.json")
    service.export_feedback_metrics(output_path)
    print(f"\n\nMetrics exported to: {output_path}")


def example_full_document_analysis():
    """Example: Analyze entire document"""
    print("\n" + "=" * 70)
    print("Example 4: Full Document Analysis")
    print("=" * 70)
    
    service = DocumentAnalysisService()
    
    pdf_path = Path("C:\\TestRepo\\ORAN\\docs\\ts_103987v040300p.pdf")
    
    print(f"Analyzing full document: {pdf_path.name}")
    result = service.analyze_document(pdf_path)
    
    print(f"\nAnalysis Summary:")
    print(f"  Document: {result.document_name}")
    print(f"  Total sections: {len(result.sections)}")
    print(f"  Decisions: {len(result.decisions)}")
    print(f"  Actions: {len(result.action_items)}")
    print(f"  Gaps: {len(result.information_gaps)}")
    print(f"  Avg Confidence: {result._avg_confidence():.2f}")
    
    # Group decisions by type
    from collections import Counter
    decision_types = Counter(d.decision_type.value for d in result.decisions)
    print(f"\nDecisions by Type:")
    for dtype, count in decision_types.most_common():
        print(f"  {dtype}: {count}")


if __name__ == "__main__":
    # Run examples
    example_basic_analysis()
    example_custom_rules()
    example_user_feedback()
    example_full_document_analysis()
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)
