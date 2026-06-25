"""
Section parser for extracting document sections at configurable depth levels.
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SectionNode:
    """Represents a document section."""
    number: str
    title: str
    depth: int
    page_number: Optional[int] = None
    start_line: int = 0
    end_line: int = 0
    text: str = ""
    children: List['SectionNode'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []


class SectionParser:
    """Parse PDF/document text to extract hierarchical sections."""
    
    SECTION_PATTERN = re.compile(r'^(\d+(?:\.\d+)*)\s+([^\n]+)$', re.MULTILINE)
    PAGE_MARKER_PATTERN = re.compile(r'---\s*Page\s+(\d+)\s*---')
    
    def __init__(self):
        self.sections: List[SectionNode] = []
        self.page_map: Dict[int, int] = {}  # line number -> page number
    
    def parse(self, text: str) -> List[SectionNode]:
        """
        Parse document text to extract sections.
        
        Args:
            text: Document text with section markers and page markers
            
        Returns:
            List of top-level section nodes (hierarchical tree)
        """
        self._build_page_map(text)
        text = self._remove_page_markers(text)
        
        lines = text.split('\n')
        sections = self._extract_section_headers(lines)
        
        if not sections:
            logger.warning("No sections found in document")
            return []
        
        # Build hierarchical tree
        self.sections = self._build_hierarchy(sections, lines)
        return self.sections
    
    def get_sections_at_depth(self, depth: int, parent: Optional[SectionNode] = None) -> List[SectionNode]:
        """Get all sections at a specific depth level."""
        if parent is None:
            search_list = self.sections
        else:
            search_list = parent.children
        
        result = []
        for section in search_list:
            if section.depth == depth:
                result.append(section)
            elif section.depth < depth:
                result.extend(self.get_sections_at_depth(depth, section))
        
        return result
    
    def get_section_by_number(self, section_num: str) -> Optional[SectionNode]:
        """Find a section by its number (e.g., '4.1.2')."""
        return self._find_section_recursive(section_num, self.sections)
    
    def get_section_text(self, section_num: str) -> str:
        """Get full text content of a section."""
        section = self.get_section_by_number(section_num)
        if not section:
            return ""
        return section.text
    
    def get_subsections(self, section_num: str, max_depth: int = 1) -> List[SectionNode]:
        """Get subsections of a given section up to max_depth levels deep."""
        parent = self.get_section_by_number(section_num)
        if not parent:
            return []
        
        return self._get_subsections_recursive(parent, max_depth, 1)
    
    def _build_page_map(self, text: str):
        """Build mapping of line numbers to page numbers."""
        self.page_map = {}
        current_page = 1
        for line_num, line in enumerate(text.split('\n')):
            if self.PAGE_MARKER_PATTERN.search(line):
                match = self.PAGE_MARKER_PATTERN.search(line)
                if match:
                    current_page = int(match.group(1))
            self.page_map[line_num] = current_page
    
    def _remove_page_markers(self, text: str) -> str:
        """Remove page markers from text."""
        return self.PAGE_MARKER_PATTERN.sub('', text)
    
    def _extract_section_headers(self, lines: List[str]) -> List[Tuple[int, str, str, int]]:
        """
        Extract section headers from lines.
        Returns list of (line_num, section_number, title, depth).
        """
        headers = []
        for line_num, line in enumerate(lines):
            match = self.SECTION_PATTERN.match(line)
            if match:
                section_num = match.group(1)
                title = match.group(2).strip()
                depth = len(section_num.split('.'))
                headers.append((line_num, section_num, title, depth))
        return headers
    
    def _build_hierarchy(
        self, 
        headers: List[Tuple[int, str, str, int]], 
        lines: List[str]
    ) -> List[SectionNode]:
        """Build hierarchical section tree from flat list of headers."""
        if not headers:
            return []
        
        nodes = []
        for i, (line_num, section_num, title, depth) in enumerate(headers):
            page_num = self.page_map.get(line_num, 1)
            
            # Calculate section text: from this line to next section header
            start_line = line_num
            if i + 1 < len(headers):
                end_line = headers[i + 1][0]
            else:
                end_line = len(lines)
            
            section_text = '\n'.join(lines[start_line + 1:end_line])
            
            node = SectionNode(
                number=section_num,
                title=title,
                depth=depth,
                page_number=page_num,
                start_line=line_num,
                end_line=end_line,
                text=section_text.strip()
            )
            nodes.append((depth, node))
        
        # Build tree structure
        return self._build_tree_from_nodes(nodes)
    
    def _build_tree_from_nodes(
        self, 
        nodes: List[Tuple[int, SectionNode]]
    ) -> List[SectionNode]:
        """Convert flat list of (depth, node) into hierarchical tree."""
        if not nodes:
            return []
        
        root_nodes = []
        stack = []  # Stack of (depth, node) tuples
        
        for depth, node in nodes:
            # Pop nodes from stack that are not parents of current node
            while stack and stack[-1][0] >= depth:
                stack.pop()
            
            # Add as child to current parent (if exists)
            if stack:
                parent_depth, parent_node = stack[-1]
                parent_node.children.append(node)
            else:
                # Top-level node
                root_nodes.append(node)
            
            stack.append((depth, node))
        
        return root_nodes
    
    def _find_section_recursive(
        self, 
        section_num: str, 
        sections: List[SectionNode]
    ) -> Optional[SectionNode]:
        """Recursively find section by number, preferring nodes with text content."""
        best: Optional[SectionNode] = None
        for section in sections:
            if section.number == section_num:
                # Prefer the node that has actual content over a TOC stub
                if best is None or (len(section.text) > len(best.text)):
                    best = section
            child_result = self._find_section_recursive(section_num, section.children)
            if child_result is not None:
                if best is None or (len(child_result.text) > len(best.text)):
                    best = child_result
        return best
    
    def _get_subsections_recursive(
        self, 
        parent: SectionNode, 
        max_depth: int, 
        current_depth: int
    ) -> List[SectionNode]:
        """Recursively get subsections up to max_depth."""
        if current_depth > max_depth:
            return []
        
        result = []
        for child in parent.children:
            result.append(child)
            if current_depth < max_depth:
                result.extend(
                    self._get_subsections_recursive(child, max_depth, current_depth + 1)
                )
        
        return result
    
    def print_hierarchy(self, sections: Optional[List[SectionNode]] = None, indent: int = 0):
        """Print section hierarchy for debugging."""
        if sections is None:
            sections = self.sections
        
        for section in sections:
            print("  " * indent + f"{section.number} {section.title}")
            self.print_hierarchy(section.children, indent + 1)
