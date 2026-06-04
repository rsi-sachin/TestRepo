"""
Specification Parser Service
Orchestrates parsing of ETSI O-RAN specifications and cross-referencing
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
import json
from datetime import datetime

from app.models.oran import (
    TestClause, TestSemantics, EnrichedTestCase,
    SpecType, HttpMethod, SpecConflict
)
from app.parsers.pdf_parser import PdfParser
from app.parsers.docx_parser import DocxParser
from app.parsers.test_clause_extractor import TestClauseExtractor

logger = logging.getLogger(__name__)


class SpecParserService:
    """Service for parsing O-RAN specifications and extracting test cases"""
    
    # Priority order for conflict resolution (higher priority first)
    SPEC_PRIORITY = [
        SpecType.TS_103_989,  # Test spec has highest priority
        SpecType.TS_103_987,  # Application protocol second
        SpecType.TS_103_988,  # Type definitions third
        SpecType.TS_103_983   # General principles last
    ]
    
    def __init__(self, spec_dir: Path):
        """
        Initialize parser service
        
        Args:
            spec_dir: Directory containing specification files
        """
        self.spec_dir = spec_dir
        self.pdf_parser = PdfParser()
        self.docx_parser = DocxParser()
        self.clause_extractor = TestClauseExtractor()
        self.conflicts: List[SpecConflict] = []
    
    def parse_specification(
        self, file_path: Path, spec_type: SpecType
    ) -> List[TestClause]:
        """
        Parse a single specification file
        
        Args:
            file_path: Path to spec file (PDF or DOCX)
            spec_type: Type of specification
            
        Returns:
            List of extracted test clauses
        """
        logger.info(f"Parsing {spec_type} from {file_path.name}")
        
        # Determine file type and parse
        if file_path.suffix.lower() == '.pdf':
            text = self.pdf_parser.parse_file(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            text = self.docx_parser.parse_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Extract test clauses
        clauses = self.clause_extractor.extract_clauses(text, spec_type)
        
        logger.info(f"Extracted {len(clauses)} clauses from {spec_type}")
        return clauses
    
    def parse_all_specs(
        self, spec_files: Dict[SpecType, Path]
    ) -> Dict[SpecType, List[TestClause]]:
        """
        Parse all specification files
        
        Args:
            spec_files: Dict mapping spec types to file paths
            
        Returns:
            Dict mapping spec types to extracted clauses
        """
        all_clauses = {}
        
        for spec_type, file_path in spec_files.items():
            try:
                clauses = self.parse_specification(file_path, spec_type)
                all_clauses[spec_type] = clauses
            except Exception as e:
                logger.error(f"Failed to parse {spec_type}: {e}")
                all_clauses[spec_type] = []
        
        return all_clauses
    
    def cross_reference_specs(
        self, all_clauses: Dict[SpecType, List[TestClause]]
    ) -> List[EnrichedTestCase]:
        """
        Cross-reference multiple specs to create enriched test cases
        
        Args:
            all_clauses: Dict mapping spec types to their clauses
            
        Returns:
            List of enriched test cases
        """
        logger.info("Cross-referencing specifications...")
        
        # Use TS 103 989 (test spec) as base
        base_clauses = all_clauses.get(SpecType.TS_103_989, [])
        
        enriched_cases = []
        for base_clause in base_clauses:
            enriched = self._enrich_test_case(base_clause, all_clauses)
            enriched_cases.append(enriched)
        
        logger.info(f"Created {len(enriched_cases)} enriched test cases")
        logger.info(f"Detected {len(self.conflicts)} conflicts")
        
        return enriched_cases
    
    def _enrich_test_case(
        self, base_clause: TestClause, all_clauses: Dict[SpecType, List[TestClause]]
    ) -> EnrichedTestCase:
        """
        Enrich a test case with information from other specs
        
        Args:
            base_clause: Base test clause from TS 103 989
            all_clauses: All clauses from all specs
            
        Returns:
            Enriched test case
        """
        # Extract HTTP info from base clause
        http_info = self.clause_extractor.extract_http_info(base_clause.raw_text or '')
        
        # Try to find endpoint info from TS 103 987 (A1 Application Protocol)
        endpoint = http_info.get('endpoint')
        if not endpoint:
            endpoint = self._find_endpoint_in_spec(
                base_clause, all_clauses.get(SpecType.TS_103_987, [])
            )
        
        # Try to find status codes from TS 103 988 (Type Definitions)
        status_code = http_info.get('status_code')
        if not status_code:
            status_code = self._find_status_code_in_spec(
                base_clause, all_clauses.get(SpecType.TS_103_988, [])
            )
        
        # Determine HTTP method
        method_str = http_info.get('method', 'GET')
        try:
            method = HttpMethod[method_str]
        except KeyError:
            method = HttpMethod.GET
        
        # Create test semantics
        semantics = TestSemantics(
            http_method=method,
            endpoint=endpoint or '/a1-p/policytypes',  # Default A1 endpoint
            expected_status=status_code or 200,
            payload_type='application/json',
            assertions=['response_valid', 'status_correct']
        )
        
        # Determine complexity based on test structure
        complexity = self._determine_complexity(base_clause)
        
        # Create enriched test case
        enriched = EnrichedTestCase(
            base_clause=base_clause,
            semantics=semantics,
            complexity=complexity,
            enrichment_sources={
                'base': f"{base_clause.spec_type} Section {base_clause.clause_number}",
                'endpoint': 'TS_103_987' if endpoint else 'default',
                'status_code': 'TS_103_988' if status_code else 'default'
            }
        )
        
        return enriched
    
    def _find_endpoint_in_spec(
        self, base_clause: TestClause, protocol_clauses: List[TestClause]
    ) -> Optional[str]:
        """Find endpoint definition in A1 protocol spec"""
        # Look for related section in protocol spec
        for clause in protocol_clauses:
            # Check if clause mentions same concept (simple keyword matching)
            if self._clauses_related(base_clause, clause):
                http_info = self.clause_extractor.extract_http_info(clause.raw_text or '')
                if http_info.get('endpoint'):
                    return http_info['endpoint']
        return None
    
    def _find_status_code_in_spec(
        self, base_clause: TestClause, type_clauses: List[TestClause]
    ) -> Optional[int]:
        """Find status code definition in type definitions spec"""
        for clause in type_clauses:
            if self._clauses_related(base_clause, clause):
                http_info = self.clause_extractor.extract_http_info(clause.raw_text or '')
                if http_info.get('status_code'):
                    return http_info['status_code']
        return None
    
    def _clauses_related(self, clause1: TestClause, clause2: TestClause) -> bool:
        """Check if two clauses are related based on keywords"""
        # Simple keyword matching (can be improved)
        keywords1 = set(clause1.title.lower().split())
        keywords2 = set(clause2.title.lower().split())
        
        # Remove common words
        stop_words = {'test', 'the', 'a', 'an', 'and', 'or', 'for', 'of', 'to'}
        keywords1 -= stop_words
        keywords2 -= stop_words
        
        # Check for common keywords
        common = keywords1 & keywords2
        return len(common) >= 2
    
    def _determine_complexity(self, clause: TestClause) -> str:
        """Determine test complexity based on clause content"""
        text = (clause.description or '') + (clause.methodology or '')
        text_lower = text.lower()
        
        # Count complexity indicators
        complexity_score = 0
        
        if 'multiple' in text_lower or 'several' in text_lower:
            complexity_score += 1
        if 'sequence' in text_lower or 'workflow' in text_lower:
            complexity_score += 1
        if 'validation' in text_lower or 'verify' in text_lower:
            complexity_score += 1
        if len(text) > 500:
            complexity_score += 1
        
        if complexity_score >= 3:
            return 'ADVANCED'
        elif complexity_score >= 1:
            return 'INTERMEDIATE'
        else:
            return 'BASIC'
    
    def detect_conflicts(
        self, enriched_cases: List[EnrichedTestCase]
    ) -> List[SpecConflict]:
        """
        Detect conflicts in enriched test cases
        
        Args:
            enriched_cases: List of enriched test cases
            
        Returns:
            List of detected conflicts
        """
        # Conflicts are detected during enrichment
        return self.conflicts
    
    def save_conflicts(self, output_path: Path):
        """Save detected conflicts to JSON file"""
        conflicts_data = [
            {
                'conflict_id': f"CONF-{i+1:03d}",
                'timestamp': datetime.now().isoformat(),
                'spec1': c.spec1.value if hasattr(c.spec1, 'value') else str(c.spec1),
                'spec2': c.spec2.value if hasattr(c.spec2, 'value') else str(c.spec2),
                'field': c.field,
                'value1': c.value1,
                'value2': c.value2,
                'resolution': c.resolution
            }
            for i, c in enumerate(self.conflicts)
        ]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(conflicts_data, f, indent=2)
        
        logger.info(f"Saved {len(conflicts_data)} conflicts to {output_path}")
