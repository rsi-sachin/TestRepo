"""
PDF Parser for ETSI O-RAN Specifications
Extracts text from PDF files using pypdf library
"""

import pypdf
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PdfParser:
    """Parser for PDF specification documents"""
    
    @staticmethod
    def parse_file(pdf_path: Path) -> str:
        """
        Extract all text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Full text content of PDF
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF cannot be read
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            reader = pypdf.PdfReader(str(pdf_path))
            text = ""
            
            logger.info(f"Reading PDF: {pdf_path.name}, Pages: {len(reader.pages)}")
            
            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num} ---\n{page_text}\n"
                
            logger.info(f"Successfully extracted {len(text)} characters from {pdf_path.name}")
            return text
            
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            raise Exception(f"Failed to parse PDF: {e}")
    
    @staticmethod
    def extract_by_page(pdf_path: Path) -> Dict[int, str]:
        """
        Extract text from PDF page by page
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary mapping page numbers (1-indexed) to text content
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            reader = pypdf.PdfReader(str(pdf_path))
            pages = {}
            
            for page_num, page in enumerate(reader.pages, start=1):
                pages[page_num] = page.extract_text()
                
            logger.info(f"Extracted {len(pages)} pages from {pdf_path.name}")
            return pages
            
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            raise Exception(f"Failed to parse PDF: {e}")
    
    @staticmethod
    def get_page_count(pdf_path: Path) -> int:
        """
        Get total number of pages in PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Number of pages
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            reader = pypdf.PdfReader(str(pdf_path))
            return len(reader.pages)
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            raise Exception(f"Failed to get page count: {e}")
    
    @staticmethod
    def extract_page_range(pdf_path: Path, start_page: int, end_page: int) -> str:
        """
        Extract text from specific page range
        
        Args:
            pdf_path: Path to PDF file
            start_page: Starting page number (1-indexed)
            end_page: Ending page number (1-indexed, inclusive)
            
        Returns:
            Text content from specified page range
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            reader = pypdf.PdfReader(str(pdf_path))
            
            if start_page < 1 or end_page > len(reader.pages):
                raise ValueError(f"Invalid page range: {start_page}-{end_page}")
            
            text = ""
            for page_num in range(start_page - 1, end_page):
                page_text = reader.pages[page_num].extract_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                
            return text
            
        except Exception as e:
            logger.error(f"Error extracting page range from {pdf_path}: {e}")
            raise Exception(f"Failed to extract page range: {e}")
