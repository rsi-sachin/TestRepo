"""
Hierarchical Extractor Service
Applies rule packs to extract hierarchical structures from documents
"""

import re
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import logging

from app.parsers.pdf_parser import PdfParser
from app.parsers.docx_parser import DocxParser
from app.models.rule_pack import RulePack, ExtractionRule, ExtractionMethod
from app.models.hierarchy_tree import HierarchyTree, HierarchyNode, ExtractionMetadata

logger = logging.getLogger(__name__)


class HierarchicalExtractorService:
    """Service for extracting hierarchical structures using rule packs"""
    
    def __init__(self):
        self.pdf_parser = PdfParser()
        self.docx_parser = DocxParser()
    
    def extract_hierarchy(
        self,
        pdf_path: Path,
        rule_pack: RulePack
    ) -> HierarchyTree:
        """
        Extract hierarchical structure from document using a rule pack
        
        Args:
            pdf_path: Path to document
            rule_pack: Rule pack to apply
            
        Returns:
            Extracted HierarchyTree
        """
        logger.info(f"Extracting hierarchy from {pdf_path.name} using rule pack {rule_pack.name}")
        
        # Parse document
        if pdf_path.suffix.lower() == '.pdf':
            text = self.pdf_parser.parse_file(pdf_path)
            pages = self.pdf_parser.extract_by_page(pdf_path)
        elif pdf_path.suffix.lower() in ['.docx', '.doc']:
            text = self.docx_parser.parse_file(pdf_path)
            pages = {1: text}  # DOCX doesn't have pages
        else:
            raise ValueError(f"Unsupported file type: {pdf_path.suffix}")
        
        # Calculate document hash
        text_hash = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]
        
        # Initialize tree
        tree = HierarchyTree(
            document_name=pdf_path.name,
            document_hash=text_hash,
            rule_pack_id=rule_pack.id,
            max_depth=rule_pack.hierarchy_config.max_depth,
            total_nodes=0,
            avg_confidence=0.0
        )
        
        # Extract hierarchy level by level
        self._extract_level_by_level(
            text=text,
            pages=pages,
            rule_pack=rule_pack,
            tree=tree
        )
        
        # Calculate final statistics
        tree._recalculate_stats()
        
        logger.info(
            f"Extraction complete: {tree.total_nodes} nodes extracted, "
            f"avg confidence: {tree.avg_confidence:.2f}"
        )
        
        return tree
    
    def _extract_level_by_level(
        self,
        text: str,
        pages: Dict[int, str],
        rule_pack: RulePack,
        tree: HierarchyTree
    ):
        """
        Extract hierarchy by applying rules level by level
        
        Args:
            text: Full document text
            pages: Dictionary of page number to page text
            rule_pack: Rule pack with extraction rules
            tree: Tree to populate (modified in place)
        """
        # Extract Level 1 (root level)
        level_1_rule = rule_pack.get_rule_by_level(1)
        if not level_1_rule:
            logger.warning("No Level 1 rule found in rule pack")
            return
        
        logger.info(f"Extracting Level 1: {level_1_rule.level_name}")
        level_1_nodes = self._extract_nodes_at_level(
            text=text,
            pages=pages,
            rule=level_1_rule,
            parent_context=None
        )
        
        for node in level_1_nodes:
            tree.add_root_node(node)
        
        logger.info(f"Found {len(level_1_nodes)} Level 1 nodes")
        
        # Recursively extract child levels
        for level in range(2, rule_pack.hierarchy_config.max_depth + 1):
            level_rule = rule_pack.get_rule_by_level(level)
            if not level_rule:
                logger.info(f"No rule for Level {level}, stopping extraction")
                break
            
            logger.info(f"Extracting Level {level}: {level_rule.level_name}")
            
            # Get parent nodes (from level - 1)
            parent_nodes = tree.find_nodes_by_level(level - 1)
            
            total_children_found = 0
            for parent in parent_nodes:
                # Extract children for this parent
                children = self._extract_nodes_at_level(
                    text=text,
                    pages=pages,
                    rule=level_rule,
                    parent_context=parent
                )
                
                # MVP limits: 1 module per feature, 2 test cases per module
                if level == 3:  # Modules level
                    max_children = 1
                elif level == 4:  # Test Cases level
                    max_children = 2
                else:
                    max_children = len(children)  # No limit
                
                for i, child in enumerate(children):
                    if i >= max_children:
                        break
                    parent.add_child(child)
                    total_children_found += 1
            
            logger.info(f"Found {total_children_found} Level {level} nodes (MVP limit applied)")
    
    def _extract_nodes_at_level(
        self,
        text: str,
        pages: Dict[int, str],
        rule: ExtractionRule,
        parent_context: Optional[HierarchyNode]
    ) -> List[HierarchyNode]:
        """
        Extract nodes at a specific level
        
        Args:
            text: Full document text
            pages: Dictionary of page content
            rule: Extraction rule for this level
            parent_context: Parent node (None for root level)
            
        Returns:
            List of extracted nodes
        """
        nodes = []
        
        if rule.extraction_method == ExtractionMethod.HEADING_MATCH:
            nodes = self._extract_by_heading_match(text, pages, rule, parent_context)
        elif rule.extraction_method == ExtractionMethod.KEYWORD_SCAN:
            nodes = self._extract_by_keyword_scan(text, pages, rule, parent_context)
        elif rule.extraction_method == ExtractionMethod.SECTION_RANGE:
            nodes = self._extract_by_section_range(text, pages, rule, parent_context)
        elif rule.extraction_method == ExtractionMethod.COMBINED:
            # Try heading match first, fall back to keyword scan
            nodes = self._extract_by_heading_match(text, pages, rule, parent_context)
            if not nodes or len(nodes) < 2:  # If too few results, try keywords
                keyword_nodes = self._extract_by_keyword_scan(text, pages, rule, parent_context)
                # Merge results, preferring heading matches
                nodes.extend(keyword_nodes)
                # Remove duplicates by section number
                seen = set()
                unique_nodes = []
                for node in nodes:
                    if node.section_number and node.section_number not in seen:
                        seen.add(node.section_number)
                        unique_nodes.append(node)
                nodes = unique_nodes
        
        # Filter by confidence threshold
        nodes = [n for n in nodes if n.metadata.confidence >= rule.min_confidence]
        
        return nodes
    
    def _extract_by_heading_match(
        self,
        text: str,
        pages: Dict[int, str],
        rule: ExtractionRule,
        parent_context: Optional[HierarchyNode]
    ) -> List[HierarchyNode]:
        """Extract nodes by matching heading patterns"""
        nodes = []
        
        # ALWAYS search the full document text
        # Parent context is only used for filtering, not limiting search scope
        search_text = text
        
        # Apply primary pattern
        if rule.pattern:
            nodes.extend(self._match_pattern(
                text=search_text,
                pages=pages,
                pattern=rule.pattern,
                rule=rule,
                parent_context=parent_context
            ))
        
        # Apply additional pattern matchers
        for pm in rule.pattern_matchers:
            matched_nodes = self._match_pattern(
                text=search_text,
                pages=pages,
                pattern=pm.pattern,
                rule=rule,
                parent_context=parent_context
            )
            nodes.extend(matched_nodes)
        
        # Remove duplicates by section number
        seen = set()
        unique_nodes = []
        for node in nodes:
            key = node.section_number or node.title
            if key not in seen:
                seen.add(key)
                unique_nodes.append(node)
        
        return unique_nodes
    
    def _match_pattern(
        self,
        text: str,
        pages: Dict[int, str],
        pattern: str,
        rule: ExtractionRule,
        parent_context: Optional[HierarchyNode]
    ) -> List[HierarchyNode]:
        """Match a specific pattern and create nodes"""
        nodes = []
        
        try:
            # Match pattern
            matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
            
            for match in matches:
                # Extract section number and title
                section_number, title = self._parse_heading(match.group(0))
                
                if not section_number and not title:
                    continue
                
                # Extract content
                content = self._extract_content_after_match(
                    text=text,
                    match=match,
                    max_length=500  # Default content length
                )
                
                # Calculate page range
                page_range = self._find_page_range(match.start(), text, pages)
                
                # Calculate confidence
                confidence = self._calculate_confidence(
                    title=title,
                    content=content,
                    keywords=rule.keywords,
                    base_confidence=0.7
                )
                
                # Boost confidence if keywords matched
                keywords_matched = [kw for kw in rule.keywords if kw.lower() in title.lower()]
                if keywords_matched:
                    confidence = min(confidence + 0.1 * len(keywords_matched), 1.0)
                
                # Create node
                node = HierarchyNode(
                    level=rule.level,
                    level_name=rule.level_name,
                    title=title,
                    section_number=section_number,
                    content_text=content[:500] if content else None,
                    metadata=ExtractionMetadata(
                        confidence=round(confidence, 3),
                        match_pattern=pattern,
                        match_method=rule.extraction_method.value,
                        page_range=page_range,
                        keywords_matched=keywords_matched
                    )
                )
                
                nodes.append(node)
                
        except re.error as e:
            logger.warning(f"Invalid regex pattern '{pattern}': {e}")
        
        return nodes
    
    def _extract_by_keyword_scan(
        self,
        text: str,
        pages: Dict[int, str],
        rule: ExtractionRule,
        parent_context: Optional[HierarchyNode]
    ) -> List[HierarchyNode]:
        """Extract nodes by scanning for keywords"""
        nodes = []
        
        # Split text into sections
        section_pattern = r'^(\d+(?:\.\d+)*)\s+([^\n]{3,200}?)(?:\n|$)'
        matches = list(re.finditer(section_pattern, text, re.MULTILINE))
        
        for match in matches:
            section_number = match.group(1)
            title = match.group(2).strip()
            
            # Check if section level matches expected level
            section_level = len(section_number.split('.'))
            if section_level != rule.level:
                continue
            
            # Check if any keywords match
            title_lower = title.lower()
            keywords_matched = [kw for kw in rule.keywords if kw.lower() in title_lower]
            
            if not keywords_matched:
                continue
            
            # Extract content
            content = self._extract_content_after_match(text, match, max_length=500)
            
            # Calculate confidence based on keyword matches
            confidence = min(0.5 + 0.1 * len(keywords_matched), 0.9)
            
            # Find page range
            page_range = self._find_page_range(match.start(), text, pages)
            
            node = HierarchyNode(
                level=rule.level,
                level_name=rule.level_name,
                title=title,
                section_number=section_number,
                content_text=content[:500] if content else None,
                metadata=ExtractionMetadata(
                    confidence=round(confidence, 3),
                    match_pattern=None,
                    match_method="KEYWORD_SCAN",
                    page_range=page_range,
                    keywords_matched=keywords_matched
                )
            )
            
            nodes.append(node)
        
        return nodes
    
    def _extract_by_section_range(
        self,
        text: str,
        pages: Dict[int, str],
        rule: ExtractionRule,
        parent_context: Optional[HierarchyNode]
    ) -> List[HierarchyNode]:
        """Extract nodes within a section number range"""
        # TODO: Implement section range extraction (e.g., 5.x-6.x)
        # For now, fall back to keyword scan
        return self._extract_by_keyword_scan(text, pages, rule, parent_context)
    
    def _parse_heading(self, heading_text: str) -> Tuple[Optional[str], str]:
        """
        Parse section number and title from heading text
        
        Returns:
            Tuple of (section_number, title)
        """
        # Pattern: "4.2 Title" or "4.2. Title" or "4.2 - Title"
        match = re.match(r'^(\d+(?:\.\d+)*)\s*[.\-]?\s*(.+?)$', heading_text.strip())
        if match:
            return match.group(1), match.group(2).strip()
        
        # No section number found
        return None, heading_text.strip()
    
    def _extract_content_after_match(
        self,
        text: str,
        match: re.Match,
        max_length: int = 500
    ) -> str:
        """Extract content text after a matched heading"""
        start_pos = match.end()
        end_pos = min(start_pos + max_length * 2, len(text))  # Get more than needed
        
        content = text[start_pos:end_pos]
        
        # Stop at next section heading
        next_section = re.search(r'\n(\d+(?:\.\d+)*)\s+[A-Z]', content)
        if next_section:
            content = content[:next_section.start()]
        
        return content.strip()
    
    def _find_page_range(
        self,
        position: int,
        full_text: str,
        pages: Dict[int, str]
    ) -> Optional[str]:
        """Find page range for a position in the text"""
        # Count page markers before this position
        page_markers = list(re.finditer(r'--- Page (\d+) ---', full_text[:position]))
        
        if page_markers:
            start_page = int(page_markers[-1].group(1))
            # Try to find end page
            remaining_text = full_text[position:position + 1000]
            end_markers = list(re.finditer(r'--- Page (\d+) ---', remaining_text))
            if end_markers:
                end_page = int(end_markers[0].group(1))
                if start_page == end_page:
                    return str(start_page)
                else:
                    return f"{start_page}-{end_page}"
            return str(start_page)
        
        return None
    
    def _calculate_confidence(
        self,
        title: str,
        content: str,
        keywords: List[str],
        base_confidence: float = 0.7
    ) -> float:
        """
        Calculate confidence score for an extracted node
        
        Args:
            title: Node title
            content: Node content
            keywords: Expected keywords
            base_confidence: Base confidence score
            
        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = base_confidence
        
        # Boost if title contains keywords
        title_lower = title.lower()
        keyword_matches = sum(1 for kw in keywords if kw.lower() in title_lower)
        if keyword_matches > 0:
            confidence += 0.05 * keyword_matches
        
        # Boost if content contains keywords
        if content:
            content_lower = content.lower()
            content_matches = sum(1 for kw in keywords if kw.lower() in content_lower)
            if content_matches > 0:
                confidence += 0.02 * content_matches
        
        return min(confidence, 1.0)
