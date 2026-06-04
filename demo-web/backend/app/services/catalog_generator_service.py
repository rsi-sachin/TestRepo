"""
Catalog Generator Service
Generates O-RAN test catalogs from enriched test cases
"""

from pathlib import Path
from typing import List, Dict, Set
import logging
import json
from datetime import datetime
import uuid

from app.models.oran import (
    OranTestCatalog, OranTestCase, EnrichedTestCase,
    SpecType, HttpMethod
)

logger = logging.getLogger(__name__)


class CatalogGeneratorService:
    """Service for generating O-RAN test catalogs"""
    
    def __init__(self, output_dir: Path):
        """
        Initialize catalog generator
        
        Args:
            output_dir: Directory to save generated catalogs
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_catalog(
        self,
        enriched_cases: List[EnrichedTestCase],
        catalog_name: str,
        description: str = "",
        apply_section_limit: bool = True
    ) -> OranTestCatalog:
        """
        Generate test catalog from enriched test cases
        
        Args:
            enriched_cases: List of enriched test cases
            catalog_name: Name for the catalog
            description: Optional description
            apply_section_limit: If True, limit to 1 test per unique section (MVP constraint)
            
        Returns:
            Generated OranTestCatalog
        """
        logger.info(f"Generating catalog: {catalog_name}")
        logger.info(f"Input: {len(enriched_cases)} enriched test cases")
        
        # Apply section limit if enabled
        if apply_section_limit:
            enriched_cases = self._apply_section_limit(enriched_cases)
            logger.info(f"After section limit: {len(enriched_cases)} test cases")
        
        # Convert to OranTestCase objects
        test_cases = []
        for i, enriched in enumerate(enriched_cases, start=1):
            test_case = self._convert_to_test_case(enriched, i)
            test_cases.append(test_case)
        
        # Create catalog
        catalog_id = f"catalog-{uuid.uuid4().hex[:12]}"
        catalog = OranTestCatalog(
            catalog_id=catalog_id,
            name=catalog_name,
            description=description,
            generated_at=datetime.now(),
            total_tests=len(test_cases),
            test_cases=test_cases,
            spec_sources=self._get_spec_sources(enriched_cases)
        )
        
        logger.info(f"Generated catalog {catalog_id} with {len(test_cases)} tests")
        return catalog
    
    def _apply_section_limit(
        self, enriched_cases: List[EnrichedTestCase]
    ) -> List[EnrichedTestCase]:
        """
        Apply MVP constraint: Keep only 1 test per unique section
        
        Args:
            enriched_cases: List of enriched test cases
            
        Returns:
            Filtered list with 1 test per section
        """
        seen_sections: Set[str] = set()
        filtered_cases: List[EnrichedTestCase] = []
        
        for case in enriched_cases:
            section = case.base_clause.clause_number
            
            if section not in seen_sections:
                filtered_cases.append(case)
                seen_sections.add(section)
                logger.debug(f"Keeping section {section}: {case.base_clause.title}")
            else:
                logger.debug(f"Skipping duplicate section {section}")
        
        logger.info(
            f"Section limit: {len(enriched_cases)} → {len(filtered_cases)} tests "
            f"({len(seen_sections)} unique sections)"
        )
        return filtered_cases
    
    def _convert_to_test_case(
        self, enriched: EnrichedTestCase, index: int
    ) -> OranTestCase:
        """
        Convert EnrichedTestCase to OranTestCase
        
        Args:
            enriched: Enriched test case
            index: Test index for ID generation
            
        Returns:
            OranTestCase object
        """
        base = enriched.base_clause
        sem = enriched.semantics
        
        # Generate test ID
        test_id = f"oran-a1-{base.clause_number.replace('.', '-')}"
        
        # Create test case
        test_case = OranTestCase(
            test_id=test_id,
            scenario=base.title,
            description=base.description or base.title,
            method=sem.http_method,
            endpoint=sem.endpoint,
            expected_status=sem.expected_status,
            complexity=enriched.complexity,
            source_spec=base.spec_type,
            source_section=base.clause_number,
            source_page=base.page_number,
            enrichment_sources=enriched.enrichment_sources
        )
        
        return test_case
    
    def _get_spec_sources(
        self, enriched_cases: List[EnrichedTestCase]
    ) -> Dict[str, str]:
        """
        Get specification sources used in catalog
        
        Args:
            enriched_cases: List of enriched test cases
            
        Returns:
            Dict mapping spec type to file info
        """
        sources = {}
        seen_specs = set()
        
        for case in enriched_cases:
            spec_type = case.base_clause.spec_type
            if spec_type not in seen_specs:
                sources[spec_type.value] = f"{spec_type.value}"
                seen_specs.add(spec_type)
        
        return sources
    
    def save_catalog(self, catalog: OranTestCatalog) -> Path:
        """
        Save catalog to JSON file
        
        Args:
            catalog: OranTestCatalog to save
            
        Returns:
            Path to saved file
        """
        output_path = self.output_dir / f"{catalog.catalog_id}.json"
        
        # Convert to dict for JSON serialization
        catalog_dict = catalog.model_dump(mode='json')
        
        with open(output_path, 'w') as f:
            json.dump(catalog_dict, f, indent=2, default=str)
        
        logger.info(f"Saved catalog to {output_path}")
        return output_path
    
    def load_catalog(self, catalog_id: str) -> OranTestCatalog:
        """
        Load catalog from JSON file
        
        Args:
            catalog_id: ID of catalog to load
            
        Returns:
            Loaded OranTestCatalog
        """
        catalog_path = self.output_dir / f"{catalog_id}.json"
        
        if not catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found: {catalog_id}")
        
        with open(catalog_path, 'r') as f:
            catalog_dict = json.load(f)
        
        catalog = OranTestCatalog(**catalog_dict)
        logger.info(f"Loaded catalog {catalog_id} with {catalog.total_tests} tests")
        return catalog
    
    def list_catalogs(self) -> List[Dict[str, any]]:
        """
        List all available catalogs
        
        Returns:
            List of catalog metadata dicts
        """
        catalogs = []
        
        for catalog_file in self.output_dir.glob("*.json"):
            try:
                with open(catalog_file, 'r') as f:
                    catalog_dict = json.load(f)
                
                catalogs.append({
                    'catalog_id': catalog_dict['catalog_id'],
                    'name': catalog_dict['name'],
                    'description': catalog_dict.get('description', ''),
                    'generated_at': catalog_dict['generated_at'],
                    'total_tests': catalog_dict['total_tests']
                })
            except Exception as e:
                logger.error(f"Error loading catalog {catalog_file}: {e}")
        
        # Sort by generated_at descending
        catalogs.sort(key=lambda x: x['generated_at'], reverse=True)
        
        logger.info(f"Found {len(catalogs)} catalogs")
        return catalogs
    
    def delete_catalog(self, catalog_id: str):
        """
        Delete a catalog
        
        Args:
            catalog_id: ID of catalog to delete
        """
        catalog_path = self.output_dir / f"{catalog_id}.json"
        
        if not catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found: {catalog_id}")
        
        catalog_path.unlink()
        logger.info(f"Deleted catalog {catalog_id}")
    
    def get_catalog_statistics(self, catalog: OranTestCatalog) -> Dict[str, any]:
        """
        Get statistics about a catalog
        
        Args:
            catalog: OranTestCatalog to analyze
            
        Returns:
            Dict with statistics
        """
        stats = {
            'total_tests': catalog.total_tests,
            'by_method': {},
            'by_complexity': {},
            'by_spec': {},
            'by_status_code': {}
        }
        
        for test in catalog.test_cases:
            # Count by method
            method = test.method.value
            stats['by_method'][method] = stats['by_method'].get(method, 0) + 1
            
            # Count by complexity
            complexity = test.complexity
            stats['by_complexity'][complexity] = stats['by_complexity'].get(complexity, 0) + 1
            
            # Count by source spec
            spec = test.source_spec.value
            stats['by_spec'][spec] = stats['by_spec'].get(spec, 0) + 1
            
            # Count by status code
            status = test.expected_status
            stats['by_status_code'][status] = stats['by_status_code'].get(status, 0) + 1
        
        return stats
