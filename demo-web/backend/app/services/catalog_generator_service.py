"""
Catalog Generator Service
Generates O-RAN test catalogs from enriched test cases
"""

from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import logging
import json
from datetime import datetime
import uuid

from app.models.oran import (
    OranTestCatalog, OranTestCase, EnrichedTestCase,
    SpecType, HttpMethod
)
from app.models.hierarchy_tree import HierarchyTree, HierarchyNode

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
    ) -> Tuple[OranTestCatalog, List[EnrichedTestCase]]:
        """
        Generate test catalog from enriched test cases
        
        Args:
            enriched_cases: List of enriched test cases
            catalog_name: Name for the catalog
            description: Optional description
            apply_section_limit: If True, limit to 1 test per unique section (MVP constraint)
            
        Returns:
            Tuple of (Generated OranTestCatalog, deduplicated enriched cases for DB save)
        """
        logger.info(f"Generating catalog: {catalog_name}")
        logger.info(f"Input: {len(enriched_cases)} enriched test cases")
        
        # Apply section limit if enabled and store deduplicated list
        deduplicated_cases = enriched_cases
        if apply_section_limit:
            deduplicated_cases = self._apply_section_limit(enriched_cases)
            logger.info(f"After section limit: {len(deduplicated_cases)} test cases")
        
        # Convert to OranTestCase objects
        test_cases = []
        for i, enriched in enumerate(deduplicated_cases, start=1):
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
            spec_sources=self._get_spec_sources(deduplicated_cases)
        )
        
        logger.info(f"Generated catalog {catalog_id} with {len(test_cases)} tests")
        return catalog, deduplicated_cases
    
    def generate_catalog_from_hierarchy(
        self,
        hierarchy_tree: HierarchyTree,
        catalog_name: str,
        description: str = "",
        spec_type: Optional[SpecType] = None
    ) -> OranTestCatalog:
        """
        Generate test catalog from hierarchical structure
        
        Args:
            hierarchy_tree: Extracted HierarchyTree
            catalog_name: Name for the catalog
            description: Optional description
            spec_type: Specification type (e.g., TS_103_989)
            
        Returns:
            Generated OranTestCatalog
        """
        logger.info(f"Generating catalog from hierarchy tree: {catalog_name}")
        logger.info(f"Tree has {hierarchy_tree.total_nodes} nodes across {hierarchy_tree.max_depth} levels")
        
        # Extract test cases from Level 4 (Test Cases level)
        level_4_nodes = hierarchy_tree.find_nodes_by_level(4)
        logger.info(f"Found {len(level_4_nodes)} Level 4 test case nodes")
        
        # If no Level 4 nodes, try Level 3 (Modules)
        if not level_4_nodes:
            level_4_nodes = hierarchy_tree.find_nodes_by_level(3)
            logger.info(f"Falling back to Level 3: {len(level_4_nodes)} module nodes")
        
        # Convert nodes to test cases
        test_cases = []
        for node in level_4_nodes:
            test_case = self._convert_node_to_test_case(
                node=node,
                hierarchy_tree=hierarchy_tree,
                spec_type=spec_type
            )
            test_cases.append(test_case)
        
        # Group by Feature (Level 2) and Module (Level 3) for metadata
        by_complexity = self._calculate_complexity_distribution(test_cases)
        
        # Create catalog
        catalog_id = f"catalog-{uuid.uuid4().hex[:12]}"
        catalog = OranTestCatalog(
            catalog_id=catalog_id,
            name=catalog_name,
            description=description or f"Generated from {hierarchy_tree.document_name}",
            generated_at=datetime.now(),
            total_tests=len(test_cases),
            test_cases=test_cases,
            spec_sources={
                hierarchy_tree.document_name: hierarchy_tree.document_hash
            },
            by_complexity=by_complexity
        )
        
        logger.info(f"Generated catalog {catalog_id} with {len(test_cases)} test cases")
        return catalog
    
    def _convert_node_to_test_case(
        self,
        node: HierarchyNode,
        hierarchy_tree: HierarchyTree,
        spec_type: Optional[SpecType] = None
    ) -> OranTestCase:
        """
        Convert a HierarchyNode to OranTestCase
        
        Args:
            node: HierarchyNode representing a test case
            hierarchy_tree: Parent tree for context
            spec_type: Specification type
            
        Returns:
            OranTestCase object
        """
        # Generate test ID from section number
        test_id_suffix = node.section_number.replace('.', '-') if node.section_number else f"node-{node.id[:8]}"
        test_id = f"A1_TC_{test_id_suffix}"
        
        # Determine complexity based on parent levels
        complexity = self._infer_complexity(node, hierarchy_tree)
        
        # Get parent context for enrichment sources
        enrichment_sources = self._get_node_lineage(node, hierarchy_tree)
        
        # Infer HTTP method from title/content (basic heuristics)
        http_method = self._infer_http_method(node)
        
        # Infer endpoint from title/content
        endpoint = self._infer_endpoint(node)
        
        # Create test case
        test_case = OranTestCase(
            test_id=test_id,
            scenario=node.title,
            description=node.content_text[:200] if node.content_text else node.title,
            method=http_method,
            endpoint=endpoint,
            expected_status=200,  # Default, should be extracted from content
            complexity=complexity,
            source_spec=spec_type,
            source_section=node.section_number,
            enrichment_sources=enrichment_sources
        )
        
        return test_case
    
    def _infer_complexity(self, node: HierarchyNode, hierarchy_tree: HierarchyTree) -> str:
        """
        Infer test complexity based on node properties and lineage
        
        Args:
            node: Test case node
            hierarchy_tree: Parent tree
            
        Returns:
            Complexity level (BASIC, INTERMEDIATE, ADVANCED)
        """
        # Check title for complexity indicators
        title_lower = node.title.lower()
        
        if any(word in title_lower for word in ['basic', 'simple', 'positive', 'create', 'query']):
            return "BASIC"
        elif any(word in title_lower for word in ['negative', 'error', 'invalid', 'update', 'delete']):
            return "INTERMEDIATE"
        elif any(word in title_lower for word in ['complex', 'advanced', 'concurrent', 'stress']):
            return "ADVANCED"
        
        # Default based on confidence
        if node.metadata.confidence >= 0.8:
            return "BASIC"
        elif node.metadata.confidence >= 0.6:
            return "INTERMEDIATE"
        else:
            return "ADVANCED"
    
    def _infer_http_method(self, node: HierarchyNode) -> HttpMethod:
        """
        Infer HTTP method from node title/content
        
        Args:
            node: Test case node
            
        Returns:
            HttpMethod enum
        """
        text = (node.title + " " + (node.content_text or "")).lower()
        
        if any(word in text for word in ['create', 'post', 'register']):
            return HttpMethod.POST
        elif any(word in text for word in ['update', 'put', 'modify']):
            return HttpMethod.PUT
        elif any(word in text for word in ['delete', 'remove']):
            return HttpMethod.DELETE
        elif any(word in text for word in ['query', 'get', 'retrieve', 'fetch']):
            return HttpMethod.GET
        
        # Default to GET
        return HttpMethod.GET
    
    def _infer_endpoint(self, node: HierarchyNode) -> str:
        """
        Infer API endpoint from node title/content
        
        Args:
            node: Test case node
            
        Returns:
            Endpoint path
        """
        text = (node.title + " " + (node.content_text or "")).lower()
        
        # Common A1 interface endpoints
        if 'policy' in text or 'policies' in text:
            return "/a1-p/policies/{policy_id}"
        elif 'ei' in text or 'job' in text:
            return "/a1-ei/jobs/{job_id}"
        elif 'status' in text:
            return "/a1-p/policystatus/{policy_id}"
        elif 'type' in text:
            return "/a1-p/policytypes/{type_id}"
        
        # Default generic endpoint
        return "/a1/{resource_id}"
    
    def _get_node_lineage(self, node: HierarchyNode, hierarchy_tree: HierarchyTree) -> Dict[str, str]:
        """
        Get lineage of a node (parent Feature and Module)
        
        Args:
            node: Test case node
            hierarchy_tree: Parent tree
            
        Returns:
            Dictionary with lineage information
        """
        lineage = {
            "test_case": f"Section {node.section_number}: {node.title}"
        }
        
        # Find parent (Level 3 - Module)
        if node.parent_id:
            parent = hierarchy_tree.find_node_by_id(node.parent_id)
            if parent:
                lineage["module"] = f"Section {parent.section_number}: {parent.title}"
                
                # Find grandparent (Level 2 - Feature)
                if parent.parent_id:
                    grandparent = hierarchy_tree.find_node_by_id(parent.parent_id)
                    if grandparent:
                        lineage["feature"] = f"Section {grandparent.section_number}: {grandparent.title}"
        
        return lineage
    
    def _calculate_complexity_distribution(self, test_cases: List[OranTestCase]) -> Dict[str, int]:
        """
        Calculate distribution of tests by complexity
        
        Args:
            test_cases: List of test cases
            
        Returns:
            Dictionary mapping complexity to count
        """
        distribution = {}
        for test_case in test_cases:
            complexity = test_case.complexity
            distribution[complexity] = distribution.get(complexity, 0) + 1
        
        return distribution
    
    def validate_catalog(self, catalog: OranTestCatalog) -> Dict[str, object]:
        """
        Validate test catalog and return validation report
        
        Args:
            catalog: OranTestCatalog to validate
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating catalog: {catalog.catalog_id}")
        
        issues = []
        warnings = []
        
        # Check if catalog has test cases
        if not catalog.test_cases:
            issues.append("Catalog has no test cases")
        
        # Validate each test case
        test_ids = set()
        for i, test_case in enumerate(catalog.test_cases):
            # Check for duplicate test IDs
            if test_case.test_id in test_ids:
                issues.append(f"Duplicate test ID: {test_case.test_id}")
            test_ids.add(test_case.test_id)
            
            # Check required fields
            if not test_case.scenario:
                issues.append(f"Test {test_case.test_id}: Missing scenario")
            if not test_case.description:
                warnings.append(f"Test {test_case.test_id}: Missing description")
            if not test_case.endpoint:
                warnings.append(f"Test {test_case.test_id}: Missing endpoint")
        
        # Check total_tests matches actual count
        if catalog.total_tests != len(catalog.test_cases):
            warnings.append(
                f"total_tests ({catalog.total_tests}) doesn't match "
                f"actual count ({len(catalog.test_cases)})"
            )
        
        # Calculate quality score
        quality_score = self._calculate_catalog_quality(catalog)
        
        is_valid = len(issues) == 0
        
        logger.info(
            f"Validation complete: valid={is_valid}, "
            f"quality={quality_score:.2f}, "
            f"issues={len(issues)}, warnings={len(warnings)}"
        )
        
        return {
            "valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "test_count": len(catalog.test_cases),
            "quality_score": quality_score,
            "unique_test_ids": len(test_ids),
            "validation_timestamp": datetime.now().isoformat()
        }
    
    def _calculate_catalog_quality(self, catalog: OranTestCatalog) -> float:
        """
        Calculate quality score for a catalog
        
        Args:
            catalog: OranTestCatalog to score
            
        Returns:
            Quality score (0.0-1.0)
        """
        if not catalog.test_cases:
            return 0.0
        
        score = 0.0
        max_score = 0.0
        
        for test_case in catalog.test_cases:
            max_score += 1.0
            case_score = 0.0
            
            # Required fields (0.5 points)
            if test_case.scenario and test_case.description:
                case_score += 0.5
            
            # API details (0.3 points)
            if test_case.method and test_case.endpoint:
                case_score += 0.3
            
            # Source tracking (0.2 points)
            if test_case.source_section:
                case_score += 0.2
            
            score += case_score
        
        return min(score / max_score if max_score > 0 else 0.0, 1.0)
    
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
    
    def save_to_database(
        self,
        enriched_cases: List[EnrichedTestCase],
        catalog_id: str,
        db_session
    ) -> int:
        """
        Save enriched test cases to database (Phase 3)
        
        MVP constraint: Save only ONE test case per unique section number.
        When multiple enriched variants exist for the same section, save the
        most complete one (most enrichment sources).
        
        Args:
            enriched_cases: List of enriched test cases
            catalog_id: ID of catalog these tests belong to
            db_session: SQLAlchemy database session
            
        Returns:
            Number of test cases saved
        """
        from app.services.test_case_service import test_case_service
        
        logger.info(f"Filtering {len(enriched_cases)} enriched test cases (MVP: 1 per section)")
        
        # Group by section number (MVP constraint: 1 test per section)
        section_map = {}
        for enriched in enriched_cases:
            section_key = (
                enriched.base_clause.spec_type.value,
                enriched.base_clause.clause_number
            )
            
            # Keep the test with most enrichment sources (most complete)
            if section_key not in section_map:
                section_map[section_key] = enriched
            else:
                existing = section_map[section_key]
                if len(enriched.enrichment_sources) > len(existing.enrichment_sources):
                    section_map[section_key] = enriched
        
        unique_cases = list(section_map.values())
        logger.info(f"Deduplicated to {len(unique_cases)} unique test cases")
        
        saved_count = 0
        failed_count = 0
        
        for enriched in unique_cases:
            try:
                test_case = test_case_service.create_from_enriched(
                    db_session,
                    enriched,
                    catalog_id
                )
                # Commit each test case individually to avoid cascade failures
                db_session.commit()
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to save test case {enriched.base_clause.clause_number}: {e}")
                failed_count += 1
                # Rollback this failed transaction
                db_session.rollback()
        
        logger.info(f"Successfully saved {saved_count}/{len(unique_cases)} test cases (failed: {failed_count})")
        return saved_count
    
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
