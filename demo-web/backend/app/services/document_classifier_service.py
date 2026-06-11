"""
Document Classifier Service
Classifies specification documents by type based on first page title patterns
"""

import re
from pathlib import Path
from typing import Tuple
from enum import Enum
import logging

from ..parsers.pdf_parser import PdfParser

logger = logging.getLogger(__name__)


class DocumentType(str, Enum):
    """Document classification types"""
    TEST_SPECIFICATION = "TEST_SPECIFICATION"
    PROTOCOL_SPECIFICATION = "PROTOCOL_SPECIFICATION"
    TYPE_DEFINITION = "TYPE_DEFINITION"
    GENERAL_PRINCIPLES = "GENERAL_PRINCIPLES"
    UNKNOWN = "UNKNOWN"


class DocumentClassifier:
    """Classifies documents based on structural patterns"""
    
    # Classification patterns (case-insensitive)
    PATTERNS = {
        DocumentType.TEST_SPECIFICATION: [
            r"test\s+specification",
            r"conformance\s+test",
            r"test\s+suite",
            r"testing\s+specification",
        ],
        DocumentType.PROTOCOL_SPECIFICATION: [
            r"application\s+protocol",
            r"interface\s+specification",
            r"protocol\s+specification",
            r"api\s+specification",
        ],
        DocumentType.TYPE_DEFINITION: [
            r"information\s+element",
            r"data\s+type",
            r"type\s+definition",
            r"schema\s+definition",
        ],
        DocumentType.GENERAL_PRINCIPLES: [
            r"general\s+principle",
            r"overview",
            r"introduction",
            r"architecture",
        ],
    }
    
    @staticmethod
    def classify_document(pdf_path: Path) -> Tuple[DocumentType, float]:
        """
        Classify document type by analyzing first page title
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (DocumentType, confidence_score)
            confidence_score is between 0.0 (no match) and 1.0 (strong match)
        """
        try:
            # Extract first page only for efficiency
            pages = PdfParser.extract_by_page(pdf_path)
            if not pages:
                logger.warning(f"No pages extracted from {pdf_path}")
                return (DocumentType.UNKNOWN, 0.0)
            
            first_page_text = pages.get(1, "")
            
            # Extract title area (first 500 chars of first page)
            title_area = first_page_text[:500].lower()
            
            logger.info(f"Classifying document: {pdf_path.name}")
            logger.debug(f"Title area: {title_area[:100]}...")
            
            # Score each document type
            scores = {}
            for doc_type, patterns in DocumentClassifier.PATTERNS.items():
                score = 0.0
                matches = []
                
                for pattern in patterns:
                    if re.search(pattern, title_area, re.IGNORECASE):
                        score += 1.0
                        matches.append(pattern)
                
                # Normalize score by number of patterns for this type
                normalized_score = score / len(patterns) if patterns else 0.0
                scores[doc_type] = normalized_score
                
                if matches:
                    logger.debug(f"{doc_type}: score={normalized_score:.2f}, matches={matches}")
            
            # Find highest scoring type
            if scores:
                best_type = max(scores, key=scores.get)
                best_score = scores[best_type]
                
                # If no patterns matched, return UNKNOWN
                if best_score == 0.0:
                    logger.info(f"No patterns matched for {pdf_path.name}")
                    return (DocumentType.UNKNOWN, 0.0)
                
                # Boost confidence if multiple patterns matched
                confidence = min(best_score + (0.1 * (best_score - 0.25)), 1.0)
                
                logger.info(f"Classified {pdf_path.name} as {best_type} (confidence: {confidence:.2f})")
                return (best_type, confidence)
            else:
                return (DocumentType.UNKNOWN, 0.0)
                
        except Exception as e:
            logger.error(f"Error classifying document {pdf_path}: {e}")
            return (DocumentType.UNKNOWN, 0.0)
    
    @staticmethod
    def classify_from_text(text: str) -> Tuple[DocumentType, float]:
        """
        Classify document type from extracted text
        Useful when PDF has already been parsed
        
        Args:
            text: First page text content
            
        Returns:
            Tuple of (DocumentType, confidence_score)
        """
        title_area = text[:500].lower()
        
        scores = {}
        for doc_type, patterns in DocumentClassifier.PATTERNS.items():
            score = 0.0
            for pattern in patterns:
                if re.search(pattern, title_area, re.IGNORECASE):
                    score += 1.0
            
            normalized_score = score / len(patterns) if patterns else 0.0
            scores[doc_type] = normalized_score
        
        if scores:
            best_type = max(scores, key=scores.get)
            best_score = scores[best_type]
            
            if best_score == 0.0:
                return (DocumentType.UNKNOWN, 0.0)
            
            confidence = min(best_score + (0.1 * (best_score - 0.25)), 1.0)
            return (best_type, confidence)
        else:
            return (DocumentType.UNKNOWN, 0.0)
    
    @staticmethod
    def get_classification_info(doc_type: DocumentType) -> dict:
        """
        Get information about a document type classification
        
        Args:
            doc_type: Document type to get info for
            
        Returns:
            Dictionary with classification metadata
        """
        info = {
            "type": doc_type.value,
            "patterns": DocumentClassifier.PATTERNS.get(doc_type, []),
            "description": ""
        }
        
        descriptions = {
            DocumentType.TEST_SPECIFICATION: "Document containing test cases, test procedures, and conformance testing specifications",
            DocumentType.PROTOCOL_SPECIFICATION: "Document describing communication protocols, API specifications, or interface definitions",
            DocumentType.TYPE_DEFINITION: "Document defining data types, information elements, or schema definitions",
            DocumentType.GENERAL_PRINCIPLES: "Document providing overview, architecture, or general principles",
            DocumentType.UNKNOWN: "Document type could not be determined"
        }
        
        info["description"] = descriptions.get(doc_type, "")
        return info
