"""Test hierarchical extractor with detailed logging"""
import sys
import os
from pathlib import Path
import logging

# Set working directory
backend_dir = Path(__file__).parent.parent
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.repositories.rule_pack_repository import RulePackRepository
from app.services.hierarchical_extractor_service import HierarchicalExtractorService

print("Testing Hierarchical Extractor with Logging...")
print()

# Load rule pack
repo = RulePackRepository()
packs = repo.list_rule_packs()
if not packs:
    print("No rule packs found!")
    sys.exit(1)

# Load the full rule pack
rule_pack = repo.load_rule_pack(packs[-1].id)
print(f"Rule Pack: {rule_pack.name}")
print(f"ID: {rule_pack.id}")
print(f"Max Depth: {rule_pack.hierarchy_config.max_depth}")
print()

# Test hierarchical extraction
extractor = HierarchicalExtractorService()
pdf_path = Path(r"C:\TestRepo\ORAN\docs\ts_103989v040200p.pdf")

print(f"Extracting hierarchy from {pdf_path.name}...")
print("This may take a minute...")
print()

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
        child_count = len(node.children) if node.children else 0
        print(f"    - {node.section_number} {node.title} ({child_count} children)")
        # Show some children
        if node.children:
            for child in node.children[:2]:
                grandchild_count = len(child.children) if child.children else 0
                print(f"        - {child.section_number} {child.title} ({grandchild_count} children)")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
