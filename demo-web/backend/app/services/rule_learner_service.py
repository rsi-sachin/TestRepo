"""
Rule Learner Service
Automatically learns extraction rules from example documents
"""

import re
import uuid
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter
import logging

from app.parsers.pdf_parser import PdfParser
from app.parsers.docx_parser import DocxParser
from app.services.document_classifier_service import DocumentClassifier, DocumentType
from app.models.rule_pack import (
    RulePack, ExtractionRule, HierarchyConfig, PatternMatcher,
    ExtractionMethod, MatchStatistics
)

logger = logging.getLogger(__name__)


class SectionInfo:
    """Information about a document section"""
    def __init__(self, section_number: str, title: str, level: int, position: int, content: str = ""):
        self.section_number = section_number
        self.title = title
        self.level = level  # Depth in hierarchy (1, 2, 3, etc.)
        self.position = position
        self.content = content


class RuleLearnerService:
    """Service for learning extraction rules from documents"""
    
    # Common patterns for test methodology sections
    METHODOLOGY_PATTERNS = [
        r"test\s+methodology",
        r"testing\s+methodology",
        r"test\s+approach",
        r"methodology",
    ]
    
    # Common patterns for features/test areas
    FEATURE_PATTERNS = [
        r"conformance\s+testing",
        r"test\s+cases?\s+for",
        r"testing\s+of",
    ]
    
    # Common patterns for modules
    MODULE_PATTERNS = [
        r"test\s+cases?\s+for",
        r"conformance\s+test",
        r"validation\s+test",
    ]
    
    # Test case identifier patterns
    TEST_CASE_PATTERNS = [
        r"TC[_\-]?\w+",
        r"TEST[_\-]?\d+",
        r"\d+\.\d+\.\d+\.\d+",  # Deep numbered sections like 5.3.1.1
    ]
    
    def __init__(self):
        self.pdf_parser = PdfParser()
        self.docx_parser = DocxParser()
        self.classifier = DocumentClassifier()
    
    def learn_from_document(
        self,
        pdf_path: Path,
        doc_type: Optional[DocumentType] = None,
        max_depth: int = 4
    ) -> RulePack:
        """
        Learn extraction rules from a document
        
        Args:
            pdf_path: Path to PDF document
            doc_type: Document type (auto-detected if None)
            max_depth: Maximum hierarchy depth to extract
            
        Returns:
            Learned RulePack
        """
        logger.info(f"Learning rules from {pdf_path.name}")
        
        # Parse document
        if pdf_path.suffix.lower() == '.pdf':
            text = self.pdf_parser.parse_file(pdf_path)
        elif pdf_path.suffix.lower() in ['.docx', '.doc']:
            text = self.docx_parser.parse_file(pdf_path)
        else:
            raise ValueError(f"Unsupported file type: {pdf_path.suffix}")
        
        # Classify document if not provided
        if doc_type is None:
            doc_type, confidence = self.classifier.classify_from_text(text)
            logger.info(f"Document classified as {doc_type} (confidence: {confidence:.2f})")
        
        # Extract document structure
        sections = self._extract_sections(text)
        logger.info(f"Extracted {len(sections)} sections")
        
        # Detect hierarchy levels
        hierarchy_config = self._detect_hierarchy(sections, max_depth)
        logger.info(f"Detected {hierarchy_config.max_depth} hierarchy levels")
        
        # Generate extraction rules for each level
        extraction_rules = self._generate_extraction_rules(sections, hierarchy_config)
        logger.info(f"Generated {len(extraction_rules)} extraction rules")
        
        # Calculate document hash
        import hashlib
        text_hash = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]
        
        # Create rule pack
        rule_pack = RulePack(
            id=str(uuid.uuid4()),
            name=f"{doc_type.value.replace('_', ' ').title()} Baseline",
            description=f"Learned from {pdf_path.name}",
            source_document_hash=text_hash,
            source_document_name=pdf_path.name,
            document_type=doc_type.value,
            hierarchy_config=hierarchy_config,
            extraction_rules=extraction_rules,
            match_statistics=MatchStatistics(),
            tags=[doc_type.value.lower(), "auto-learned"],
            version="1.0"
        )
        
        logger.info(f"Created rule pack: {rule_pack.name} (ID: {rule_pack.id})")
        return rule_pack
    
    def _extract_sections(self, text: str) -> List[SectionInfo]:
        """
        Extract all sections from document text
        
        Args:
            text: Full document text
            
        Returns:
            List of SectionInfo objects
        """
        sections = []
        
        # Pattern for numbered sections (e.g., "4.2", "5.3.1", "4. Introduction")
        # Handles various formats: "4.2 Title", "4.2. Title", "4.2 - Title"
        section_pattern = r'^(\d+(?:\.\d+)*)\s*[.\-]?\s+([A-Z][^\n]{0,200}?)(?:\n|$)'
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            match = re.match(section_pattern, line.strip(), re.MULTILINE)
            if match:
                section_number = match.group(1)
                title = match.group(2).strip()
                
                # Calculate level from section number (e.g., "4" = 1, "4.2" = 2, "4.2.1" = 3)
                level = len(section_number.split('.'))
                
                # Extract some content (next few lines)
                content_lines = []
                for j in range(i + 1, min(i + 10, len(lines))):
                    content_lines.append(lines[j])
                content = '\n'.join(content_lines)[:500]
                
                sections.append(SectionInfo(
                    section_number=section_number,
                    title=title,
                    level=level,
                    position=i,
                    content=content
                ))
        
        logger.debug(f"Extracted {len(sections)} sections via pattern matching")
        return sections
    
    def _detect_hierarchy(self, sections: List[SectionInfo], max_depth: int) -> HierarchyConfig:
        """
        Detect hierarchy structure from sections
        
        Args:
            sections: List of extracted sections
            max_depth: Maximum depth to detect
            
        Returns:
            HierarchyConfig with detected levels
        """
        level_definitions = {}
        
        # Level 1: Look for "Test Methodology" or similar
        for section in sections:
            if section.level == 1:
                title_lower = section.title.lower()
                for pattern in self.METHODOLOGY_PATTERNS:
                    if re.search(pattern, title_lower, re.IGNORECASE):
                        level_definitions[1] = "Test Methodology"
                        logger.info(f"Level 1 detected: Section {section.section_number} - {section.title}")
                        break
                if 1 in level_definitions:
                    break
        
        # If no methodology found at level 1, use generic name
        if 1 not in level_definitions:
            level_definitions[1] = "Main Sections"
        
        # Level 2: Subsections under level 1 (Features/Test Areas)
        level_2_titles = []
        for section in sections:
            if section.level == 2:
                title_lower = section.title.lower()
                # Check if it matches feature patterns
                for pattern in self.FEATURE_PATTERNS:
                    if re.search(pattern, title_lower, re.IGNORECASE):
                        level_2_titles.append(section.title)
                        break
        
        if level_2_titles:
            level_definitions[2] = "Features"
            logger.info(f"Level 2 detected: {len(level_2_titles)} feature sections")
        else:
            level_definitions[2] = "Subsections"
        
        # Level 3: Look for module/test collection patterns
        level_3_sections = [s for s in sections if s.level == 3]
        if level_3_sections:
            # Check for "test cases" patterns
            module_count = 0
            for section in level_3_sections:
                title_lower = section.title.lower()
                if "test" in title_lower or "conformance" in title_lower:
                    module_count += 1
            
            if module_count > 0:
                level_definitions[3] = "Modules"
                logger.info(f"Level 3 detected: {module_count} module sections")
            else:
                level_definitions[3] = "Detailed Sections"
        
        # Level 4: Test cases (deepest level or test case identifiers)
        level_4_sections = [s for s in sections if s.level == 4]
        if level_4_sections or max_depth >= 4:
            level_definitions[4] = "Test Cases"
            logger.info(f"Level 4 detected: Test case level")
        
        # Ensure we have definitions up to actual max depth
        actual_max_depth = min(max_depth, max((s.level for s in sections), default=1))
        for i in range(1, actual_max_depth + 1):
            if i not in level_definitions:
                level_definitions[i] = f"Level {i}"
        
        return HierarchyConfig(
            max_depth=actual_max_depth,
            level_definitions=level_definitions,
            extract_content=True,
            max_content_length=500
        )
    
    def _generate_extraction_rules(
        self,
        sections: List[SectionInfo],
        hierarchy_config: HierarchyConfig
    ) -> List[ExtractionRule]:
        """
        Generate extraction rules for each hierarchy level
        
        Args:
            sections: List of extracted sections
            hierarchy_config: Detected hierarchy configuration
            
        Returns:
            List of ExtractionRule objects
        """
        rules = []
        
        for level in range(1, hierarchy_config.max_depth + 1):
            level_name = hierarchy_config.level_definitions.get(level, f"Level {level}")
            
            # Get sections at this level
            level_sections = [s for s in sections if s.level == level]
            if not level_sections:
                continue
            
            # Analyze common patterns
            patterns, keywords = self._analyze_level_patterns(level, level_sections, level_name)
            
            # Determine extraction method
            if level == 1:
                method = ExtractionMethod.HEADING_MATCH
                required = True
                min_confidence = 0.8
            elif level <= 3:
                method = ExtractionMethod.COMBINED
                required = False
                min_confidence = 0.6
            else:
                method = ExtractionMethod.KEYWORD_SCAN
                required = False
                min_confidence = 0.5
            
            # Create pattern matchers
            pattern_matchers = [
                PatternMatcher(
                    pattern=pattern,
                    flags="IGNORECASE",
                    examples=self._get_pattern_examples(pattern, level_sections)
                )
                for pattern in patterns[:3]  # Top 3 patterns
            ]
            
            # Generate section range if applicable
            section_range = None
            if level_sections:
                first_section = level_sections[0].section_number
                last_section = level_sections[-1].section_number
                if first_section and last_section:
                    first_major = first_section.split('.')[0]
                    last_major = last_section.split('.')[0]
                    if first_major == last_major:
                        section_range = f"{first_major}.x"
            
            rule = ExtractionRule(
                level=level,
                level_name=level_name,
                pattern=patterns[0] if patterns else None,
                keywords=keywords,
                required=required,
                extraction_method=method,
                parent_level=level - 1 if level > 1 else None,
                section_range=section_range,
                min_confidence=min_confidence,
                pattern_matchers=pattern_matchers
            )
            
            rules.append(rule)
            logger.info(f"Created rule for Level {level} ({level_name}): pattern='{patterns[0] if patterns else 'none'}', keywords={keywords[:3]}")
        
        return rules
    
    def _analyze_level_patterns(
        self,
        level: int,
        sections: List[SectionInfo],
        level_name: str
    ) -> Tuple[List[str], List[str]]:
        """
        Analyze patterns and keywords for a specific level
        
        Args:
            level: Hierarchy level
            sections: Sections at this level
            level_name: Name of the level
            
        Returns:
            Tuple of (patterns, keywords)
        """
        patterns = []
        all_keywords = []
        
        # Extract all title words
        for section in sections:
            title_lower = section.title.lower()
            words = re.findall(r'\b[a-z]{3,}\b', title_lower)  # Words 3+ chars
            all_keywords.extend(words)
        
        # Count keyword frequency
        keyword_counts = Counter(all_keywords)
        
        # Remove common words
        stopwords = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'are', 'was', 'were'}
        for stopword in stopwords:
            keyword_counts.pop(stopword, None)
        
        # Get top keywords
        top_keywords = [word for word, count in keyword_counts.most_common(10)]
        
        # Generate patterns based on level
        if level == 1 and "methodology" in level_name.lower():
            # Make dot optional, use case-insensitive matching
            patterns = [r"^\d+\.?\s*Test\s+Methodology", r"^\d+\.?\s*Methodology"]
        elif level == 2 and "feature" in level_name.lower():
            patterns = [r"^\d+\.\d+\s*Conformance\s+Testing", r"^\d+\.\d+\s*Testing"]
        elif level == 3 and "module" in level_name.lower():
            patterns = [r"^\d+\.\d+\s*.*Test\s+[Cc]ases", r"^\d+\.\d+\s*Conformance"]
        elif level == 4:
            # Look for test case identifiers or deeply nested sections
            patterns = [r"TC_\w+", r"\d+\.\d+\.\d+\.\d+\s", r"Test\s+[Cc]ase\s+\d+"]
        else:
            # Generic pattern for this level
            section_pattern = r"^\d+" + r"\.\d+" * (level - 1) + r"\s"
            patterns = [section_pattern]
        
        return patterns, top_keywords[:8]  # Return top 8 keywords
    
    def _get_pattern_examples(self, pattern: str, sections: List[SectionInfo]) -> List[str]:
        """
        Get example matches for a pattern
        
        Args:
            pattern: Regex pattern
            sections: Sections to search
            
        Returns:
            List of example matches
        """
        examples = []
        for section in sections[:5]:  # First 5 sections
            full_heading = f"{section.section_number} {section.title}"
            try:
                if re.search(pattern, full_heading, re.IGNORECASE):
                    examples.append(full_heading[:100])
            except re.error:
                continue
        
        return examples[:3]  # Return up to 3 examples
