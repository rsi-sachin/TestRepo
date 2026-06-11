"""Test hierarchical extractor directly to get full error details"""
import sys
import os
from pathlib import Path
import traceback

# Set working directory
backend_dir = Path(__file__).parent.parent
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

from app.repositories.rule_pack_repository import RulePackRepository
from app.services.hierarchical_extractor_service import HierarchicalExtractorService

print("Testing Hierarchical Extractor...")
print()

# Load rule pack
repo = RulePackRepository()
packs = repo.list_rule_packs()
if not packs:
    print("No rule packs found!")
    sys.exit(1)

# Load the full rule pack
rule_pack = repo.load_rule_pack(packs[-1].id)  # Get the newest one
print(f"Rule Pack: {rule_pack.name}")
print(f"ID: {rule_pack.id}")
print()

# Test hierarchical extraction
extractor = HierarchicalExtractorService()
pdf_path = Path(r"C:\TestRepo\ORAN\docs\ts_103989v040200p.pdf")

print(f"Extracting hierarchy from {pdf_path.name}...")
try:
    hierarchy_tree = extractor.extract_hierarchy(
        pdf_path=pdf_path,
        rule_pack=rule_pack
    )
    
    print(f"\n✓ Success!")
    print(f"  Total Nodes: {hierarchy_tree.total_nodes}")
    print(f"  Max Depth: {hierarchy_tree.max_depth}")
    print(f"  Avg Confidence: {hierarchy_tree.avg_confidence:.2f}")
    
    # Show root nodes
    print(f"\n  Root Nodes: {len(hierarchy_tree.root_nodes)}")
    for node in hierarchy_tree.root_nodes[:3]:
        print(f"    - {node.section_number} {node.title} ({node.child_count} children)")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print(f"\nFull traceback:")
    traceback.print_exc()
