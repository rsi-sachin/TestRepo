"""
Create a corrected baseline rule pack with patterns that actually match the document
"""
import sys
import os
from pathlib import Path

# Set working directory
backend_dir = Path(__file__).parent.parent
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

from app.services.rule_learner_service import RuleLearnerService
from app.services.document_classifier_service import DocumentType
from app.repositories.rule_pack_repository import RulePackRepository

print("Generating corrected baseline rule pack...")
print()

# Paths
pdf_path = Path(r"C:\TestRepo\ORAN\docs\ts_103989v040200p.pdf")

# Initialize services
learner = RuleLearnerService()
repo = RulePackRepository()

# Learn rules
print(f"Learning from: {pdf_path.name}")
rule_pack = learner.learn_from_document(
    pdf_path=pdf_path,
    doc_type=DocumentType.TEST_SPECIFICATION,
    max_depth=4
)

print(f"\nRule Pack Created:")
print(f"  ID: {rule_pack.id}")
print(f"  Name: {rule_pack.name}")
print(f"  Document Type: {rule_pack.document_type}")
print(f"  Max Depth: {rule_pack.hierarchy_config.max_depth}")
print(f"\nExtraction Rules:")
for rule in rule_pack.extraction_rules:
    print(f"  Level {rule.level} ({rule.level_name}):")
    print(f"    Method: {rule.extraction_method}")
    print(f"    Pattern: {repr(rule.pattern)}")
    if rule.keywords:
        print(f"    Keywords (first 3): {rule.keywords[:3]}")

# Save
print(f"\nSaving rule pack...")
success = repo.save_rule_pack(rule_pack)
if success:
    print(f"✓ Saved successfully")
else:
    print(f"✗ Failed to save")

print(f"\nTotal rule packs now: {len(repo.list_rule_packs())}")
