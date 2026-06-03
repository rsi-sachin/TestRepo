"""
Test Clause Extractor for ETSI O-RAN Specifications
Extracts test cases from specification text using regex patterns
"""

import re
from typing import List, Optional, Dict, Tuple
from pathlib import Path
import logging

from app.models.oran import TestClause, SpecType

logger = logging.getLogger(__name__)


class TestClauseExtractor:
    """Extracts test clauses from ETSI specification text"""
    
    # Regex patterns for ETSI test clause structure
    SECTION_PATTERN = r'^(\d+(?:\.\d+)*)\s+(.+)$'  # Match: "5.3.2 Test Title"
    TEST_TITLE_KEYWORDS = ['test', 'verification', 'check', 'validate', 'conformance']
    
    def __init__(self):
        self.section_pattern = re.compile(self.SECTION_PATTERN, re.MULTILINE)
    
    def extract_clauses(self, text: str, spec_type: SpecType) -> List[TestClause]:
        """
        Extract test clauses from specification text
        
        Args:
            text: Full text content from specification
            spec_type: Type of specification (TS_103_989, etc.)
            
        Returns:
            List of extracted test clauses
        """
        logger.info(f"Extracting test clauses from {spec_type}")
        
        # Split text into sections
        sections = self._split_into_sections(text)
        
        # Filter sections that look like test cases
        test_sections = self._filter_test_sections(sections)
        
        # Convert to TestClause objects
        clauses = []
        for section_num, section_title, section_text, page_num in test_sections:
            clause = self._parse_test_clause(
                section_num, section_title, section_text, spec_type, page_num
            )
            if clause:
                clauses.append(clause)
        
        logger.info(f"Extracted {len(clauses)} test clauses from {spec_type}")
        return clauses
    
    def _split_into_sections(self, text: str) -> List[Tuple[str, str, str, int]]:
        """
        Split text into numbered sections
        
        Returns:
            List of tuples: (section_number, title, body_text, page_number)
        """
        sections = []
        lines = text.split('\n')
        current_section_num = None
        current_title = None
        current_text = []
        current_page = 1
        
        for line in lines:
            # Track page numbers
            if '--- Page' in line:
                match = re.search(r'Page (\d+)', line)
                if match:
                    current_page = int(match.group(1))
                continue
            
            # Check if line is a section header
            match = self.section_pattern.match(line.strip())
            if match:
                # Save previous section
                if current_section_num and current_title:
                    sections.append((
                        current_section_num,
                        current_title,
                        '\n'.join(current_text).strip(),
                        current_page
                    ))
                
                # Start new section
                current_section_num = match.group(1)
                current_title = match.group(2).strip()
                current_text = []
            else:
                # Add to current section body
                if current_section_num:
                    current_text.append(line)
        
        # Save last section
        if current_section_num and current_title:
            sections.append((
                current_section_num,
                current_title,
                '\n'.join(current_text).strip(),
                current_page
            ))
        
        logger.debug(f"Split text into {len(sections)} sections")
        return sections
    
    def _filter_test_sections(
        self, sections: List[Tuple[str, str, str, int]]
    ) -> List[Tuple[str, str, str, int]]:
        """
        Filter sections that appear to be test cases
        
        Args:
            sections: List of (section_num, title, text, page) tuples
            
        Returns:
            Filtered list of test sections
        """
        test_sections = []
        
        for section_num, title, text, page in sections:
            # Check if title contains test-related keywords
            title_lower = title.lower()
            is_test = any(keyword in title_lower for keyword in self.TEST_TITLE_KEYWORDS)
            
            # Check if section number looks like test section (e.g., 5.x.x)
            # ETSI typically has tests in sections 5-7
            if section_num.startswith(('5.', '6.', '7.')):
                is_test = True
            
            # Check if body text contains test-related structure
            text_lower = text.lower()
            has_test_structure = (
                'test purpose' in text_lower or
                'expected result' in text_lower or
                'pre-condition' in text_lower or
                'test configuration' in text_lower
            )
            
            if is_test or has_test_structure:
                test_sections.append((section_num, title, text, page))
        
        logger.debug(f"Filtered to {len(test_sections)} test sections")
        return test_sections
    
    def _parse_test_clause(
        self,
        section_num: str,
        title: str,
        text: str,
        spec_type: SpecType,
        page_num: int
    ) -> Optional[TestClause]:
        """
        Parse a test section into TestClause object
        
        Args:
            section_num: Section number (e.g., "5.3.2")
            title: Section title
            text: Section body text
            spec_type: Specification type
            page_num: Page number where section starts
            
        Returns:
            TestClause object or None if parsing fails
        """
        try:
            # Extract test purpose/description
            description = self._extract_field(text, [
                'test purpose', 'description', 'objective'
            ])
            
            # Extract entrance criteria / pre-conditions
            entrance_criteria = self._extract_field(text, [
                'pre-condition', 'entrance criteria', 'initial condition'
            ])
            
            # Extract test methodology / procedure
            methodology = self._extract_field(text, [
                'test procedure', 'methodology', 'test steps', 'procedure'
            ])
            
            # Extract expected result
            expected_result = self._extract_field(text, [
                'expected result', 'pass criteria', 'verdict'
            ])
            
            # Create TestClause
            clause = TestClause(
                clause_number=section_num,
                title=title,
                description=description or title,
                spec_type=spec_type,
                page_number=page_num,
                entrance_criteria=entrance_criteria,
                methodology=methodology,
                expected_result=expected_result,
                raw_text=text[:1000]  # Store first 1000 chars
            )
            
            logger.debug(f"Parsed test clause: {section_num} - {title}")
            return clause
            
        except Exception as e:
            logger.error(f"Error parsing test clause {section_num}: {e}")
            return None
    
    def _extract_field(self, text: str, field_names: List[str]) -> Optional[str]:
        """
        Extract a specific field from text using multiple possible field names
        
        Args:
            text: Text to search
            field_names: List of possible field name patterns
            
        Returns:
            Extracted field value or None
        """
        for field_name in field_names:
            # Try to find field with colon separator
            pattern = rf'{field_name}\s*:\s*(.+?)(?=\n\n|\n[A-Z]|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                value = match.group(1).strip()
                # Clean up value (remove excessive whitespace)
                value = ' '.join(value.split())
                if len(value) > 10:  # Only return if meaningful content
                    return value[:500]  # Limit to 500 chars
        
        return None
    
    def extract_http_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract HTTP-related information from test text
        
        Args:
            text: Test clause text
            
        Returns:
            Dict with 'method', 'endpoint', 'status_code' keys
        """
        http_info = {
            'method': None,
            'endpoint': None,
            'status_code': None
        }
        
        # Extract HTTP method
        method_pattern = r'\b(GET|POST|PUT|DELETE|PATCH)\b'
        method_match = re.search(method_pattern, text, re.IGNORECASE)
        if method_match:
            http_info['method'] = method_match.group(1).upper()
        
        # Extract endpoint/URL path
        endpoint_pattern = r'(/[a-zA-Z0-9/_\-]+(?:\{[a-zA-Z0-9_]+\})?)'
        endpoint_match = re.search(endpoint_pattern, text)
        if endpoint_match:
            http_info['endpoint'] = endpoint_match.group(1)
        
        # Extract status code
        status_pattern = r'\b(200|201|204|400|401|403|404|500|503)\b'
        status_match = re.search(status_pattern, text)
        if status_match:
            http_info['status_code'] = int(status_match.group(1))
        
        return http_info
