"""
Script to generate baseline rule pack from ts_103989v040200p.pdf

This script:
1. Loads the default ETSI test specification document
2. Runs the rule learner service to analyze its structure
3. Generates and saves the baseline rule pack
4. Verifies the output

Usage:
    python scripts/generate_baseline_rules.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rule_learner_service import RuleLearnerService
from app.services.document_classifier_service import DocumentType
from app.repositories.rule_pack_repository import RulePackRepository
from app.services.spec_parser_service import SpecParserService
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Generate baseline rule pack"""
    
    # Path to the default test specification document
    pdf_path = Path("C:/TestRepo/ORAN/docs/ts_103989v040200p.pdf")
    
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        logger.error("Please ensure the file exists before running this script")
        return 1
    
    logger.info("=" * 80)
    logger.info("GENERATING BASELINE RULE PACK FOR ETSI TEST SPECIFICATION")
    logger.info("=" * 80)
    logger.info(f"Source document: {pdf_path.name}")
    logger.info("")
    
    try:
        # Initialize services
        logger.info("Initializing rule learner service...")
        rule_learner = RuleLearnerService()
        
        logger.info("Initializing rule pack repository...")
        repository = RulePackRepository()
        
        logger.info("Initializing spec parser service...")
        spec_parser = SpecParserService(spec_dir=pdf_path.parent)
        
        # Learn rules from document
        logger.info("")
        logger.info("Step 1: Analyzing document structure...")
        logger.info("-" * 80)
        
        rule_pack = rule_learner.learn_from_document(
            pdf_path=pdf_path,
            doc_type=DocumentType.TEST_SPECIFICATION,
            max_depth=4
        )
        
        logger.info("")
        logger.info("Step 2: Rule pack generated successfully!")
        logger.info("-" * 80)
        logger.info(f"  Rule Pack ID: {rule_pack.id}")
        logger.info(f"  Name: {rule_pack.name}")
        logger.info(f"  Document Type: {rule_pack.document_type}")
        logger.info(f"  Max Depth: {rule_pack.hierarchy_config.max_depth}")
        logger.info(f"  Extraction Rules: {len(rule_pack.extraction_rules)}")
        logger.info("")
        
        # Display hierarchy configuration
        logger.info("Hierarchy Configuration:")
        for level, name in sorted(rule_pack.hierarchy_config.level_definitions.items()):
            logger.info(f"  Level {level}: {name}")
        logger.info("")
        
        # Display extraction rules
        logger.info("Extraction Rules Generated:")
        for rule in rule_pack.extraction_rules:
            logger.info(f"  Level {rule.level} ({rule.level_name}):")
            logger.info(f"    - Pattern: {rule.pattern}")
            logger.info(f"    - Keywords: {rule.keywords[:5]}")
            logger.info(f"    - Method: {rule.extraction_method.value}")
            logger.info(f"    - Required: {rule.required}")
            logger.info(f"    - Min Confidence: {rule.min_confidence}")
            if rule.section_range:
                logger.info(f"    - Section Range: {rule.section_range}")
            logger.info("")
        
        # Save rule pack
        logger.info("Step 3: Saving rule pack...")
        logger.info("-" * 80)
        
        success = repository.save_rule_pack(rule_pack)
        
        if success:
            logger.info(f"✓ Rule pack saved successfully!")
            logger.info(f"  Location: data/oran_learning/rule_packs/{rule_pack.id}.json")
            logger.info("")
            
            # Also persist fingerprint via spec_parser_service
            logger.info("Step 3a: Persisting document fingerprint...")
            logger.info("-" * 80)
            try:
                # This triggers fingerprint persistence
                from app.models.oran import SpecType
                extraction_result = spec_parser.extract_methodology_plan(
                    file_path=pdf_path,
                    spec_type=SpecType.TS_103_989,
                    max_modules=12
                )
                logger.info(f"✓ Fingerprint persisted!")
                logger.info(f"  Location: data/oran_learning/document_fingerprints.json")
                logger.info("")
            except Exception as e:
                logger.warning(f"Failed to persist fingerprint: {e}")
            
            # Verify saved rule pack
            logger.info("Step 4: Verifying saved rule pack...")
            logger.info("-" * 80)
            
            loaded_pack = repository.load_rule_pack(rule_pack.id)
            if loaded_pack:
                logger.info(f"✓ Rule pack loaded successfully!")
                logger.info(f"  Verified ID: {loaded_pack.id}")
                logger.info(f"  Verified Name: {loaded_pack.name}")
                logger.info("")
                
                # Display statistics
                logger.info("Repository Statistics:")
                stats = repository.get_statistics()
                logger.info(f"  Total Rule Packs: {stats['total_rule_packs']}")
                logger.info(f"  By Document Type:")
                for doc_type, count in stats['by_document_type'].items():
                    logger.info(f"    - {doc_type}: {count}")
                logger.info("")
                
                logger.info("=" * 80)
                logger.info("✓ BASELINE RULE PACK GENERATION COMPLETE!")
                logger.info("=" * 80)
                logger.info("")
                logger.info("Next steps:")
                logger.info("  1. The rule pack is now available for hierarchical extraction")
                logger.info("  2. Use this rule pack to extract structure from similar documents")
                logger.info("  3. The system will automatically match similar documents to this rule pack")
                logger.info("")
                
                return 0
            else:
                logger.error("✗ Failed to verify saved rule pack")
                return 1
        else:
            logger.error("✗ Failed to save rule pack")
            return 1
            
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error generating baseline rule pack: {e}")
        logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
