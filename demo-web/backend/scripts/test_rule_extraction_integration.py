"""
Test script for rule-based hierarchical extraction integration

Tests the complete pipeline:
1. Document classification
2. Fingerprint matching
3. Rule pack selection
4. Hierarchical extraction
5. Quality scoring
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.spec_parser_service import SpecParserService
from app.models.oran import SpecType
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Test rule-based extraction integration"""
    
    pdf_path = Path("C:/TestRepo/ORAN/docs/ts_103989v040200p.pdf")
    
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        return 1
    
    logger.info("=" * 80)
    logger.info("TESTING RULE-BASED EXTRACTION INTEGRATION")
    logger.info("=" * 80)
    logger.info("")
    
    # Initialize parser service
    spec_dir = pdf_path.parent
    parser_service = SpecParserService(spec_dir)
    
    # Test extraction with rules
    logger.info("Test 1: Extract hierarchy with rule-based method")
    logger.info("-" * 80)
    
    try:
        result = parser_service.extract_hierarchy_with_rules(
            file_path=pdf_path,
            spec_type=SpecType.TS_103_989,
            force_heuristic=False
        )
        
        logger.info("")
        logger.info("Extraction Results:")
        logger.info(f"  File: {result['file_name']}")
        logger.info(f"  Document Type: {result['document_type']} (confidence: {result['document_type_confidence']})")
        logger.info(f"  Extraction Method: {result['extraction_method']}")
        logger.info(f"  Rule Pack ID: {result['rule_pack_id']}")
        logger.info(f"  Quality Score: {result['quality_score']:.2f}")
        logger.info(f"  Fallback Used: {result['fallback_used']}")
        
        if result['hierarchy_tree']:
            tree = result['hierarchy_tree']
            logger.info("")
            logger.info("Hierarchy Tree Statistics:")
            logger.info(f"  Total Nodes: {tree.total_nodes}")
            logger.info(f"  Max Depth: {tree.max_depth}")
            logger.info(f"  Avg Confidence: {tree.avg_confidence:.2f}")
            logger.info(f"  Root Nodes: {len(tree.root_nodes)}")
            
            # Show node distribution by level
            logger.info("")
            logger.info("Nodes by Level:")
            for level in range(1, tree.max_depth + 1):
                nodes_at_level = tree.find_nodes_by_level(level)
                logger.info(f"  Level {level}: {len(nodes_at_level)} nodes")
                
                # Show first 3 node titles
                for i, node in enumerate(nodes_at_level[:3]):
                    logger.info(f"    - {node.section_number} {node.title[:60]}")
            
            # Validation
            logger.info("")
            logger.info("Tree Validation:")
            validation = tree.validate()
            logger.info(f"  Valid: {validation['valid']}")
            if validation['issues']:
                logger.info(f"  Issues: {validation['issues']}")
            if validation['warnings']:
                logger.info(f"  Warnings: {validation['warnings'][:3]}")  # Show first 3
        
        logger.info("")
        logger.info("✓ Rule-based extraction test PASSED")
        
    except Exception as e:
        logger.error(f"✗ Rule-based extraction test FAILED: {e}")
        logger.exception("Full traceback:")
        return 1
    
    # Test with heuristic fallback
    logger.info("")
    logger.info("=" * 80)
    logger.info("Test 2: Extract with forced heuristic fallback")
    logger.info("-" * 80)
    
    try:
        result2 = parser_service.extract_hierarchy_with_rules(
            file_path=pdf_path,
            spec_type=SpecType.TS_103_989,
            force_heuristic=True
        )
        
        logger.info("")
        logger.info("Heuristic Extraction Results:")
        logger.info(f"  Extraction Method: {result2['extraction_method']}")
        logger.info(f"  Methodology Sections: {len(result2.get('methodology_sections', []))}")
        logger.info(f"  Modules: {len(result2.get('modules', []))}")
        logger.info(f"  Quality Score: {result2['quality_score']:.2f}")
        
        logger.info("")
        logger.info("✓ Heuristic fallback test PASSED")
        
    except Exception as e:
        logger.error(f"✗ Heuristic fallback test FAILED: {e}")
        logger.exception("Full traceback:")
        return 1
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("✓ ALL INTEGRATION TESTS PASSED!")
    logger.info("=" * 80)
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
