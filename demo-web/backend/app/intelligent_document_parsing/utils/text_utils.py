"""
Utility functions for intelligent document parsing.
"""

import re
from typing import List, Dict, Tuple, Set
from collections import Counter
import math


class TextNormalizer:
    """Normalize and clean text for processing."""
    
    @staticmethod
    def normalize(text: str) -> str:
        """Basic text normalization."""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)  # Collapse whitespace
        return text
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        cleaned = [re.sub(r'[.!?]+$', '', s.strip()) for s in sentences]
        return [s for s in cleaned if s]
    
    @staticmethod
    def extract_paragraphs(text: str) -> List[str]:
        """Split text into paragraphs."""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
    
    @staticmethod
    def remove_page_markers(text: str) -> str:
        """Remove page markers like '--- Page 5 ---'."""
        return re.sub(r'---\s*Page\s+\d+\s*---', '', text)


class KeywordMatcher:
    """Keyword and pattern-based matching for extraction."""
    
    DECISION_KEYWORDS = {
        'shall', 'should', 'must', 'will', 'is', 'are', 'require', 'required',
        'need', 'needed', 'define', 'defined', 'specify', 'specified',
        'implement', 'implemented', 'configure', 'configured', 'establish',
        'restriction', 'constraint', 'limitation', 'rule', 'policy',
    }
    
    ACTION_KEYWORDS = {
        'implement', 'develop', 'create', 'build', 'test', 'verify', 'validate',
        'configure', 'setup', 'install', 'deploy', 'document', 'update', 'review',
        'assess', 'evaluate', 'monitor', 'track', 'manage', 'handle',
        'handle', 'ensure', 'maintain', 'check', 'confirm',
        'must', 'need', 'needs', 'should', 'shall', 'required',
    }
    
    GAP_KEYWORDS = {
        'unclear', 'ambiguous', 'missing', 'undefined', 'unknown', 'uncertain',
        'todo', 'fixme', 'note', 'pending', 'unresolved', 'question',
        'further research', 'investigation needed', 'clarification needed',
        'not specified', 'not defined', 'not clear',
    }
    
    @staticmethod
    def score_decision_keywords(text: str) -> Tuple[float, List[str]]:
        """Score text based on decision keywords. Returns (score, matched_keywords)."""
        text_lower = text.lower()
        matched = []
        for keyword in KeywordMatcher.DECISION_KEYWORDS:
            if keyword in text_lower:
                matched.append(keyword)
        
        score = min(1.0, len(matched) * 0.15)
        return score, matched
    
    @staticmethod
    def score_action_keywords(text: str) -> Tuple[float, List[str]]:
        """Score text based on action keywords. Returns (score, matched_keywords)."""
        text_lower = text.lower()
        matched = []
        for keyword in KeywordMatcher.ACTION_KEYWORDS:
            if keyword in text_lower:
                matched.append(keyword)
        
        score = min(1.0, len(matched) * 0.15)
        return score, matched
    
    @staticmethod
    def score_gap_keywords(text: str) -> Tuple[float, List[str]]:
        """Score text based on gap keywords. Returns (score, matched_keywords)."""
        text_lower = text.lower()
        matched = []
        for keyword in KeywordMatcher.GAP_KEYWORDS:
            if keyword in text_lower:
                matched.append(keyword)
        
        score = min(1.0, len(matched) * 0.2)
        return score, matched


class PatternMatcher:
    """Sentence structure and pattern-based matching."""
    
    REQUIREMENT_PATTERNS = [
        r'\b(?:shall|must|should)\s+\w+',  # "shall implement"
        r'\bretained\s+(?:must|shall|should)',  # "X must be retained"
        r'\brequired\s+(?:to|for)',  # "required to do"
        r'\bmandatory\s+',  # "mandatory X"
    ]
    
    ACTION_PATTERNS = [
        r'(?:implement|develop|create|build)\s+\w+',
        r'(?:test|verify|validate)\s+(?:the|a|all)\s+\w+',
        r'(?:ensure|verify)\s+that\s+',
        r'(?:configure|setup)\s+(?:the|a)\s+\w+',
    ]
    
    GAP_PATTERNS = [
        r'(?:unclear|ambiguous|not\s+(?:clear|specified|defined))\s+',
        r'(?:further|additional)\s+(?:research|investigation|clarification)',
        r'todo|fixme|pending|unresolved',
    ]
    
    @staticmethod
    def match_patterns(text: str, patterns: List[str]) -> Tuple[float, int]:
        """Match text against list of regex patterns. Returns (score, match_count)."""
        text_lower = text.lower()
        match_count = 0
        for pattern in patterns:
            if re.search(pattern, text_lower):
                match_count += 1
        
        score = min(1.0, match_count * 0.3)
        return score, match_count


class TfIdfScorer:
    """TF-IDF based scoring for document analysis."""
    
    @staticmethod
    def calculate_term_frequency(tokens: List[str]) -> Dict[str, float]:
        """Calculate term frequency."""
        if not tokens:
            return {}
        counter = Counter(tokens)
        total = len(tokens)
        return {term: count / total for term, count in counter.items()}
    
    @staticmethod
    def calculate_idf(documents: List[List[str]]) -> Dict[str, float]:
        """Calculate inverse document frequency."""
        if not documents:
            return {}
        
        doc_count = len(documents)
        term_doc_count: Dict[str, int] = {}
        
        for doc in documents:
            unique_terms = set(doc)
            for term in unique_terms:
                term_doc_count[term] = term_doc_count.get(term, 0) + 1
        
        idf = {}
        for term, count in term_doc_count.items():
            idf[term] = math.log(doc_count / count) if count > 0 else 0
        
        return idf
    
    @staticmethod
    def calculate_tfidf(tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
        """Calculate TF-IDF scores."""
        tf = TfIdfScorer.calculate_term_frequency(tokens)
        tfidf = {}
        for term, freq in tf.items():
            tfidf[term] = freq * idf.get(term, 0)
        return tfidf


class TextTokenizer:
    """Basic text tokenization."""
    
    STOPWORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that',
        'the', 'to', 'was', 'will', 'with', 'this', 'these', 'those',
    }
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text into words."""
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    @staticmethod
    def tokenize_meaningful(text: str) -> List[str]:
        """Tokenize text, removing stopwords."""
        tokens = TextTokenizer.tokenize(text)
        return [t for t in tokens if t not in TextTokenizer.STOPWORDS and len(t) > 2]
    
    @staticmethod
    def extract_noun_phrases(text: str) -> List[str]:
        """Simple extraction of multi-word phrases."""
        # Simple pattern: Adjective/Noun combinations
        phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        return [p for p in phrases if len(p.split()) <= 3]


class SectionExtractor:
    """Extract section numbers and titles."""
    
    SECTION_PATTERN = re.compile(r'^(?P<num>\d+(?:\.\d+)*)\s+(?P<title>.+)$', re.MULTILINE)
    
    @staticmethod
    def extract_sections(text: str) -> List[Tuple[str, str, int]]:
        """
        Extract sections and their titles.
        Returns list of (section_number, title, depth).
        """
        sections = []
        for match in SectionExtractor.SECTION_PATTERN.finditer(text):
            num = match.group('num')
            title = match.group('title').strip()
            depth = len(num.split('.'))
            sections.append((num, title, depth))
        return sections
    
    @staticmethod
    def get_section_depth(section_num: str) -> int:
        """Get depth of a section number (4.1.2 = depth 3)."""
        return len(section_num.split('.'))
    
    @staticmethod
    def filter_by_depth(sections: List[Tuple[str, str, int]], depth: int) -> List[Tuple[str, str, int]]:
        """Filter sections to specific depth."""
        return [s for s in sections if s[2] == depth]
