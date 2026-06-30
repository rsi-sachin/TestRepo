"""
Specification Parser Service
Orchestrates parsing of ETSI O-RAN specifications and cross-referencing
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
import json
import hashlib
from datetime import datetime

from app.models.oran import (
    TestClause, TestSemantics, EnrichedTestCase,
    SpecType, HttpMethod, SpecConflict, ScenarioType
)
from app.parsers.pdf_parser import PdfParser
from app.parsers.docx_parser import DocxParser
from app.parsers.methodology_extractor import MethodologyExtractor
from app.parsers.test_clause_extractor import TestClauseExtractor
from app.services.document_classifier_service import DocumentClassifier, DocumentType
from app.services.rule_matcher_service import RuleMatcherService
from app.services.hierarchical_extractor_service import HierarchicalExtractorService
from app.repositories.rule_pack_repository import RulePackRepository
from app.services.semantic_version_tracker import SemanticVersionTracker, SemanticVersion
from app.services.module_impact_analyzer import ModuleImpactAnalyzer

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
    
    def __init__(self, spec_dir: Path, learning_metadata_dir: Optional[Path] = None):
        """
        Initialize parser service
        
        Args:
            spec_dir: Directory containing specification files
        """
        self.spec_dir = spec_dir
        self.pdf_parser = PdfParser()
        self.docx_parser = DocxParser()
        self.clause_extractor = TestClauseExtractor()
        self.methodology_extractor = MethodologyExtractor()
        self.conflicts: List[SpecConflict] = []
        self.learning_metadata_dir = learning_metadata_dir or Path("./data/oran_learning")
        self.learning_metadata_dir.mkdir(parents=True, exist_ok=True)
        self.learning_metadata_file = self.learning_metadata_dir / "learning_metadata.jsonl"
        self.learning_metadata_latest_dir = self.learning_metadata_dir / "latest"
        self.learning_metadata_latest_dir.mkdir(parents=True, exist_ok=True)
        self.fingerprints_file = self.learning_metadata_dir / "document_fingerprints.json"
        
        # Rule-based extraction services
        self.rule_matcher = RuleMatcherService()
        self.hierarchical_extractor = HierarchicalExtractorService()
        self.rule_pack_repository = RulePackRepository()
        
        # Version tracking and impact analysis (TODO: Feature in development)
        self.version_tracker = SemanticVersionTracker(
            self.learning_metadata_dir / "version_history.json"
        )
        self.impact_analyzer = ModuleImpactAnalyzer()
    
    def parse_specification(
        self, file_path: Path, spec_type: SpecType, max_tests: Optional[int] = None
    ) -> List[TestClause]:
        """
        Parse a single specification file
        
        Args:
            file_path: Path to spec file (PDF or DOCX)
            spec_type: Type of specification
            max_tests: Maximum tests to extract per spec (MVP constraint)
            
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
        
        # Extract test clauses with limit
        clauses = self.clause_extractor.extract_clauses(text, spec_type, max_tests)
        
        logger.info(f"Extracted {len(clauses)} clauses from {spec_type}")
        return clauses
    
    def parse_all_specs(
        self, spec_files: Dict[SpecType, Path], max_tests_per_spec: Optional[int] = None
    ) -> Dict[SpecType, List[TestClause]]:
        """
        Parse all specification files
        
        Args:
            spec_files: Dict mapping spec types to file paths
            max_tests_per_spec: Maximum tests to extract per spec (MVP constraint)
            
        Returns:
            Dict mapping spec types to extracted clauses
        """
        all_clauses = {}
        
        for spec_type, file_path in spec_files.items():
            try:
                clauses = self.parse_specification(file_path, spec_type, max_tests_per_spec)
                all_clauses[spec_type] = clauses
            except Exception as e:
                logger.error(f"Failed to parse {spec_type}: {e}")
                all_clauses[spec_type] = []
        
        return all_clauses

    def extract_methodology_plan(
        self,
        file_path: Path,
        spec_type: SpecType,
        max_modules: int = 12,
    ) -> Dict[str, object]:
        """Extract methodology sections and machine-assisted module/title candidates."""
        if file_path.suffix.lower() == '.pdf':
            text = self.pdf_parser.parse_file(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            text = self.docx_parser.parse_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        sections = self.methodology_extractor.extract_methodology_sections(text)
        modules = self.methodology_extractor.generate_module_candidates(sections, text, max_modules=max_modules)
        titles = self.methodology_extractor.generate_test_title_candidates(modules, sections)

        learning_saved = False
        try:
            learning_metadata = self._build_learning_metadata(
                spec_type=spec_type,
                file_path=file_path,
                text=text,
                sections=sections,
                modules=modules,
                titles=titles,
            )
            self._persist_learning_metadata(learning_metadata)
            learning_saved = True
        except Exception as e:
            logger.warning(f"Failed to persist learning metadata for {spec_type.value}: {e}")

        return {
            'spec_type': spec_type,
            'spec_file': file_path.name,
            'methodology_sections': sections,
            'modules': modules,
            'titles': titles,
            'summary': {
                'methodology_sections_found': len(sections),
                'test_modules_found': len(modules),
                'test_titles_found': len(titles),
                'learning_metadata_saved': 1 if learning_saved else 0,
            }
        }

    def _build_learning_metadata(
        self,
        spec_type: SpecType,
        file_path: Path,
        text: str,
        sections: List,
        modules: List,
        titles: List,
    ) -> Dict[str, object]:
        """Build reusable metadata that captures document-specific extraction behavior."""
        timestamp = datetime.now().isoformat()
        module_confidences = [float(getattr(module, "confidence", 0.0)) for module in modules]

        depth_histogram: Dict[str, int] = {}
        for section in sections:
            depth_key = str(getattr(section, "depth", 0))
            depth_histogram[depth_key] = depth_histogram.get(depth_key, 0) + 1

        keyword_frequency: Dict[str, int] = {}
        for module in modules:
            for keyword in getattr(module, "keywords", []):
                key = str(keyword).strip().lower()
                if not key:
                    continue
                keyword_frequency[key] = keyword_frequency.get(key, 0) + 1

        top_keywords = [
            key for key, _ in sorted(
                keyword_frequency.items(),
                key=lambda item: (-item[1], item[0])
            )[:12]
        ]

        # Enhanced fingerprinting for similarity matching
        # Extract Level 1 heading patterns (section titles with positions)
        heading_patterns = []
        for i, section in enumerate(sections[:20]):  # First 20 sections
            section_num = getattr(section, "section_number", "")
            title = getattr(section, "title", "")
            # Estimate level from section numbering (e.g., "4" = level 1, "4.2" = level 2)
            level = len(section_num.split('.')) if '.' in section_num else (1 if section_num else 0)
            if level == 1:  # Level 1 headings only
                heading_patterns.append({
                    "position": i,
                    "section_number": section_num,
                    "title": title[:100],  # Truncate long titles
                    "level": level
                })
        
        # Calculate average section length
        section_lengths = []
        for section in sections:
            content = getattr(section, "content", "")
            if content:
                section_lengths.append(len(content))
        avg_section_length = int(sum(section_lengths) / len(section_lengths)) if section_lengths else 0
        
        # Check for numbered subsections (e.g., 4.2.1, 5.3.2)
        has_numbered_subsections = any(
            len(getattr(section, "section_number", "").split('.')) >= 3
            for section in sections
        )
        
        # Classify document type
        doc_type, doc_type_confidence = DocumentClassifier.classify_from_text(text)

        fingerprint = {
            "spec_type": spec_type.value,
            "file_name": file_path.name,
            "file_extension": file_path.suffix.lower(),
            "text_hash": hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16],
            "section_numbering_style": "dotted_numeric" if any("." in getattr(section, "section_number", "") for section in sections) else "numeric",
            "depth_histogram": depth_histogram,
            "sample_headings": [
                {
                    "section_number": getattr(section, "section_number", ""),
                    "title": getattr(section, "title", ""),
                }
                for section in sections[:8]
            ],
            # Enhanced fingerprinting fields
            "document_type": doc_type.value,
            "document_type_confidence": round(doc_type_confidence, 2),
            "heading_patterns": heading_patterns,
            "avg_section_length": avg_section_length,
            "has_numbered_subsections": has_numbered_subsections,
            "total_sections": len(sections),
        }

        quality_signals = {
            "methodology_sections_found": len(sections),
            "module_candidates_found": len(modules),
            "title_candidates_found": len(titles),
            "avg_module_confidence": round(sum(module_confidences) / len(module_confidences), 3) if module_confidences else 0.0,
            "max_module_confidence": round(max(module_confidences), 3) if module_confidences else 0.0,
        }

        learned_rules = {
            "extraction": {
                "section_pattern": self.methodology_extractor.SECTION_RE.pattern,
                "page_pattern": self.methodology_extractor.PAGE_RE.pattern,
                "methodology_hints": list(self.methodology_extractor.METHODOLOGY_HINTS),
            },
            "interpretation": {
                "module_rank_strategy": "section-title scoring plus phrase scoring with module_id deduplication",
                "title_rank_strategy": "module-based title candidates plus evidence-derived phrases",
                "confidence_observed": quality_signals,
            },
            "domain": {
                "top_keywords": top_keywords,
                "domain_hints": self.methodology_extractor.DOMAIN_HINTS,
                "generic_blocklist": sorted(self.methodology_extractor.GENERIC_BLOCKLIST),
                "module_names_seen": [getattr(module, "module_name", "") for module in modules[:20]],
            },
        }

        return {
            "metadata_id": f"{spec_type.value}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "created_at": timestamp,
            "document_fingerprint": fingerprint,
            "learned_rules": learned_rules,
            "quality_signals": quality_signals,
            "reuse_hints": {
                "applies_to": "similar ETSI/O-RAN style numbered specification documents",
                "recommended_reuse_fields": [
                    "extraction.section_pattern",
                    "extraction.methodology_hints",
                    "interpretation.module_rank_strategy",
                    "domain.top_keywords",
                    "domain.domain_hints",
                ],
            },
        }

    def _persist_learning_metadata(self, metadata: Dict[str, object]) -> None:
        """Append metadata history and keep latest snapshot per spec type for quick reuse."""
        with open(self.learning_metadata_file, "a", encoding="utf-8") as file_handle:
            file_handle.write(json.dumps(metadata, ensure_ascii=True) + "\n")

        spec_type = str(
            metadata.get("document_fingerprint", {}).get("spec_type", "unknown")
        )
        latest_file = self.learning_metadata_latest_dir / f"{spec_type}.json"
        with open(latest_file, "w", encoding="utf-8") as file_handle:
            json.dump(metadata, file_handle, indent=2, ensure_ascii=True)
        
        # Also persist fingerprint for similarity matching
        self._persist_fingerprint(metadata.get("document_fingerprint", {}))
    
    def _persist_fingerprint(self, fingerprint: Dict[str, object]) -> None:
        """Persist document fingerprint to the fingerprints index file."""
        # Load existing fingerprints
        fingerprints = self._load_fingerprints()
        
        # Add or update fingerprint (keyed by text_hash for deduplication)
        text_hash = fingerprint.get("text_hash", "")
        if text_hash:
            fingerprints[text_hash] = {
                **fingerprint,
                "indexed_at": datetime.now().isoformat()
            }
            
            # Save back to file
            with open(self.fingerprints_file, "w", encoding="utf-8") as f:
                json.dump(fingerprints, f, indent=2, ensure_ascii=True)
            
            logger.info(f"Persisted fingerprint for {fingerprint.get('file_name', 'unknown')}")
    
    def _load_fingerprints(self) -> Dict[str, Dict]:
        """Load all document fingerprints from the index file."""
        if not self.fingerprints_file.exists():
            return {}
        
        try:
            with open(self.fingerprints_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load fingerprints: {e}")
            return {}
    
    def get_all_fingerprints(self) -> List[Dict]:
        """Get all document fingerprints as a list."""
        fingerprints_dict = self._load_fingerprints()
        return list(fingerprints_dict.values())
    
    def extract_hierarchy_with_rules(
        self,
        file_path: Path,
        spec_type: Optional[SpecType] = None,
        force_heuristic: bool = False
    ) -> Dict[str, object]:
        """
        Extract hierarchical structure using rule-based extraction with fallback
        
        Args:
            file_path: Path to specification file
            spec_type: Optional specification type
            force_heuristic: If True, skip rule-based extraction and use heuristic
            
        Returns:
            Dictionary containing extraction results and metadata
        """
        logger.info(f"Extracting hierarchy from {file_path.name} (rule-based: {not force_heuristic})")
        
        # Parse document
        if file_path.suffix.lower() == '.pdf':
            text = self.pdf_parser.parse_file(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            text = self.docx_parser.parse_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Classify document
        doc_type, doc_confidence = DocumentClassifier.classify_from_text(text)
        logger.info(f"Document classified as {doc_type.value} (confidence: {doc_confidence:.2f})")
        
        result = {
            'file_name': file_path.name,
            'document_type': doc_type.value,
            'document_type_confidence': round(doc_confidence, 2),
            'extraction_method': None,
            'rule_pack_id': None,
            'hierarchy_tree': None,
            'quality_score': 0.0,
            'fallback_used': False,
            'error': None
        }
        
        # Try rule-based extraction first (unless forced to use heuristic)
        if not force_heuristic:
            try:
                # Generate fingerprint for this document
                sections = self.methodology_extractor.extract_methodology_sections(text)
                learning_metadata = self._build_learning_metadata(
                    spec_type=spec_type or SpecType.TS_103_989,
                    file_path=file_path,
                    text=text,
                    sections=sections,
                    modules=[],
                    titles=[]
                )
                fingerprint = learning_metadata.get('document_fingerprint', {})
                
                # Find matching rule pack
                existing_fingerprints = self.get_all_fingerprints()
                rule_pack_id = self.rule_matcher.get_best_rule_pack(
                    fingerprint,
                    existing_fingerprints
                )
                
                if rule_pack_id:
                    logger.info(f"Found matching rule pack: {rule_pack_id}")
                    
                    # Load rule pack
                    rule_pack = self.rule_pack_repository.load_rule_pack(rule_pack_id)
                    
                    if rule_pack:
                        # Extract hierarchy using rule pack
                        logger.info(f"Applying rule pack: {rule_pack.name}")
                        hierarchy_tree = self.hierarchical_extractor.extract_hierarchy(
                            pdf_path=file_path,
                            rule_pack=rule_pack
                        )
                        
                        # Calculate quality score
                        quality_score = self._calculate_extraction_quality(hierarchy_tree)
                        
                        result['extraction_method'] = 'rule-based'
                        result['rule_pack_id'] = rule_pack_id
                        result['hierarchy_tree'] = hierarchy_tree
                        result['quality_score'] = quality_score
                        
                        logger.info(
                            f"Rule-based extraction complete: {hierarchy_tree.total_nodes} nodes, "
                            f"quality: {quality_score:.2f}"
                        )
                        
                        # If quality is acceptable, return
                        if quality_score >= 0.7:
                            # Update rule pack statistics
                            rule_pack.update_statistics(success=True, quality_score=quality_score)
                            self.rule_pack_repository.update_rule_pack(rule_pack)
                            return result
                        else:
                            logger.warning(
                                f"Quality score {quality_score:.2f} below threshold 0.7, "
                                "will try heuristic fallback"
                            )
                            # Update statistics as failure
                            rule_pack.update_statistics(success=False, quality_score=quality_score)
                            self.rule_pack_repository.update_rule_pack(rule_pack)
                    else:
                        logger.warning(f"Failed to load rule pack {rule_pack_id}")
                else:
                    logger.info("No matching rule pack found, will use heuristic extraction")
                    
            except Exception as e:
                logger.error(f"Rule-based extraction failed: {e}")
                logger.exception("Full traceback:")
                result['error'] = str(e)
        
        # Fallback to heuristic extraction
        logger.info("Using heuristic extraction (fallback)")
        try:
            sections = self.methodology_extractor.extract_methodology_sections(text)
            modules = self.methodology_extractor.generate_module_candidates(
                sections, text, max_modules=12
            )
            titles = self.methodology_extractor.generate_test_title_candidates(
                modules, sections
            )
            
            result['extraction_method'] = 'heuristic'
            result['fallback_used'] = True
            result['methodology_sections'] = sections
            result['modules'] = modules
            result['titles'] = titles
            result['quality_score'] = self._calculate_heuristic_quality(sections, modules)
            
            logger.info(
                f"Heuristic extraction complete: {len(sections)} sections, "
                f"{len(modules)} modules"
            )
            
        except Exception as e:
            logger.error(f"Heuristic extraction also failed: {e}")
            result['error'] = str(e)
        
        return result
    
    def _calculate_extraction_quality(self, hierarchy_tree) -> float:
        """
        Calculate quality score for rule-based extraction
        
        Args:
            hierarchy_tree: Extracted HierarchyTree
            
        Returns:
            Quality score (0.0-1.0)
        """
        if not hierarchy_tree:
            return 0.0
        
        # Base score from average confidence
        base_score = hierarchy_tree.avg_confidence
        
        # Bonus for having nodes at all levels
        nodes_by_level = {}
        for node in hierarchy_tree.get_all_nodes():
            level = node.level
            nodes_by_level[level] = nodes_by_level.get(level, 0) + 1
        
        level_coverage = len(nodes_by_level) / hierarchy_tree.max_depth if hierarchy_tree.max_depth > 0 else 0
        
        # Bonus for reasonable node count (not too few, not too many)
        node_count_score = 0.0
        if 5 <= hierarchy_tree.total_nodes <= 500:
            node_count_score = 0.1
        elif hierarchy_tree.total_nodes > 0:
            node_count_score = 0.05
        
        # Combined quality score
        quality = base_score * 0.6 + level_coverage * 0.3 + node_count_score
        
        return min(quality, 1.0)
    
    def _calculate_heuristic_quality(self, sections: List, modules: List) -> float:
        """
        Calculate quality score for heuristic extraction
        
        Args:
            sections: Methodology sections
            modules: Module candidates
            
        Returns:
            Quality score (0.0-1.0)
        """
        if not sections:
            return 0.0
        
        # Calculate based on number of sections and modules found
        section_score = min(len(sections) / 10.0, 1.0) * 0.5
        module_score = min(len(modules) / 8.0, 1.0) * 0.5
        
        return section_score + module_score
    
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

        scenario_type = self._determine_scenario_type(base_clause)
        configurable_request_parts = self._determine_configurable_request_parts(scenario_type)
        
        # Create test semantics
        semantics = TestSemantics(
            scenario_type=scenario_type,
            simulator_required=scenario_type == ScenarioType.CONFORMANCE,
            configurable_request_parts=configurable_request_parts,
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
            scenario_type=scenario_type,
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

    def _determine_scenario_type(self, clause: TestClause) -> ScenarioType:
        """Determine whether a clause is a conformance or interoperability scenario."""
        if clause.scenario_type is not None:
            return clause.scenario_type

        text = " ".join(filter(None, [clause.title, clause.description, clause.methodology, clause.expected_result])).lower()
        if "interoperability" in text:
            return ScenarioType.INTEROPERABILITY
        return ScenarioType.CONFORMANCE

    def _determine_configurable_request_parts(self, scenario_type: ScenarioType) -> List[str]:
        """Return request parts that the harness must keep configurable for the scenario type."""
        if scenario_type == ScenarioType.CONFORMANCE:
            return ['uri', 'headers', 'body']
        return ['uri', 'headers', 'body']
    
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
    
    # ==================== VERSION TRACKING & IMPACT ANALYSIS ====================
    # TODO: Feature in development - Semantic version tracking and module impact analysis
    # Feature: Detect version changes in specifications and identify source code modules
    #          that may require updates based on specification version changes.
    # Integration: Triggered from spec upload/processing workflow
    
    def detect_and_analyze_version_changes(
        self, file_path: Path, spec_type: str
    ) -> Optional[Dict]:
        """
        Detect version changes in a spec and analyze impact on source code.
        
        This is a placeholder implementation for the version tracking feature.
        Currently it:
        1. Extracts version from document text
        2. Compares with previously tracked version
        3. Analyzes impact on source code modules if version changed
        4. Generates human-readable impact report
        
        Args:
            file_path: Path to specification file (PDF or DOCX)
            spec_type: Specification type (e.g., "TS_103987")
            
        Returns:
            Dictionary with version tracking and impact analysis details, or None if no version detected
            
        Example:
            result = parser_service.detect_and_analyze_version_changes(
                file_path=Path("ts_103987v040300p.pdf"),
                spec_type="TS_103987"
            )
            if result and result['is_breaking']:
                print(f"BREAKING CHANGE: {result['impact_report']}")
        
        TODO Implementation Steps:
        1. Extract text from PDF/DOCX
        2. Call version_tracker.extract_version_from_text() to parse version
        3. Check version_tracker.documents[spec_type] for previous version
        4. If changed, determine change_type (major/minor/patch)
        5. Call impact_analyzer.analyze_impact() to get affected modules
        6. Call impact_analyzer.generate_impact_report() for human-readable output
        7. Update version_tracker.register_document() with new version
        8. Call version_tracker.save_history() to persist changes
        9. Return comprehensive result dict with impact analysis
        """
        logger.info(
            f"[PLACEHOLDER] Detecting version changes for {spec_type} from {file_path.name}"
        )
        
        # TODO: Extract text
        # if file_path.suffix.lower() == '.pdf':
        #     text = self.pdf_parser.parse_file(file_path)[:5000]
        # else:
        #     text = self.docx_parser.parse_file(file_path)[:5000]
        
        # TODO: Extract version
        # current_version = self.version_tracker.extract_version_from_text(text, spec_type)
        # if not current_version:
        #     logger.warning(f"Could not extract version from {file_path.name}")
        #     return None
        
        # TODO: Check for previous version and detect change
        # TODO: Analyze impact using self.impact_analyzer
        # TODO: Generate report
        # TODO: Persist history
        
        return None
