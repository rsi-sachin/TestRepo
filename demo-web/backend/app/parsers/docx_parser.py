"""
DOCX Parser for O-RAN Specifications
Extracts text from Microsoft Word documents using python-docx library
"""

from docx import Document
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class DocxParser:
    """Parser for DOCX specification documents"""
    
    @staticmethod
    def parse_file(docx_path: Path) -> str:
        """
        Extract all text from DOCX file
        
        Args:
            docx_path: Path to DOCX file
            
        Returns:
            Full text content of document
            
        Raises:
            FileNotFoundError: If DOCX file doesn't exist
            Exception: If DOCX cannot be read
        """
        if not docx_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")
        
        try:
            doc = Document(str(docx_path))
            
            # Extract all paragraphs
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paragraphs)
            
            logger.info(f"Successfully extracted {len(text)} characters from {docx_path.name}")
            logger.info(f"Total paragraphs: {len(paragraphs)}")
            
            return text
            
        except Exception as e:
            logger.error(f"Error reading DOCX {docx_path}: {e}")
            raise Exception(f"Failed to parse DOCX: {e}")
    
    @staticmethod
    def extract_paragraphs(docx_path: Path) -> List[str]:
        """
        Extract paragraphs as list
        
        Args:
            docx_path: Path to DOCX file
            
        Returns:
            List of paragraph texts
        """
        if not docx_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")
        
        try:
            doc = Document(str(docx_path))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            
            logger.info(f"Extracted {len(paragraphs)} paragraphs from {docx_path.name}")
            return paragraphs
            
        except Exception as e:
            logger.error(f"Error reading DOCX {docx_path}: {e}")
            raise Exception(f"Failed to extract paragraphs: {e}")
    
    @staticmethod
    def extract_with_formatting(docx_path: Path) -> List[Dict[str, str]]:
        """
        Extract paragraphs with formatting information
        
        Args:
            docx_path: Path to DOCX file
            
        Returns:
            List of dicts with 'text' and 'style' keys
        """
        if not docx_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")
        
        try:
            doc = Document(str(docx_path))
            formatted_paragraphs = []
            
            for p in doc.paragraphs:
                if p.text.strip():
                    formatted_paragraphs.append({
                        'text': p.text,
                        'style': p.style.name if p.style else 'Normal'
                    })
            
            logger.info(f"Extracted {len(formatted_paragraphs)} formatted paragraphs from {docx_path.name}")
            return formatted_paragraphs
            
        except Exception as e:
            logger.error(f"Error extracting formatted text from {docx_path}: {e}")
            raise Exception(f"Failed to extract formatted text: {e}")
    
    @staticmethod
    def extract_tables(docx_path: Path) -> List[List[List[str]]]:
        """
        Extract all tables from DOCX
        
        Args:
            docx_path: Path to DOCX file
            
        Returns:
            List of tables, each table is list of rows, each row is list of cell texts
        """
        if not docx_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")
        
        try:
            doc = Document(str(docx_path))
            tables = []
            
            for table in doc.tables:
                table_data = []
                for row in table.rows:
                    row_data = [cell.text for cell in row.cells]
                    table_data.append(row_data)
                tables.append(table_data)
            
            logger.info(f"Extracted {len(tables)} tables from {docx_path.name}")
            return tables
            
        except Exception as e:
            logger.error(f"Error extracting tables from {docx_path}: {e}")
            raise Exception(f"Failed to extract tables: {e}")
