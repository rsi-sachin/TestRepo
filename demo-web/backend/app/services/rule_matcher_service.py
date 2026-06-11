"""
Rule Matcher Service
Finds similar documents based on fingerprint similarity and selects best matching rule packs
"""

from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)


class MatchResult:
    """Result of a document similarity match"""
    
    def __init__(
        self,
        fingerprint: Dict,
        similarity_score: float,
        rule_pack_id: Optional[str] = None
    ):
        self.fingerprint = fingerprint
        self.similarity_score = similarity_score
        self.rule_pack_id = rule_pack_id
        self.file_name = fingerprint.get("file_name", "unknown")
        self.document_type = fingerprint.get("document_type", "UNKNOWN")
        self.text_hash = fingerprint.get("text_hash", "")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "file_name": self.file_name,
            "document_type": self.document_type,
            "similarity_score": round(self.similarity_score, 3),
            "rule_pack_id": self.rule_pack_id,
            "text_hash": self.text_hash
        }


class RuleMatcherService:
    """Service for matching documents to rule packs based on similarity"""
    
    # Similarity scoring weights (must sum to 1.0)
    WEIGHT_STRUCTURAL = 0.4  # Section numbering style, depth histogram
    WEIGHT_KEYWORDS = 0.3    # Keyword overlap (Jaccard similarity)
    WEIGHT_SECTIONS = 0.3    # Heading pattern similarity
    
    # Threshold for applying existing rules
    SIMILARITY_THRESHOLD = 0.6  # 60% similarity required
    
    def __init__(self, rule_pack_index_file: Optional[Path] = None):
        """
        Initialize rule matcher service
        
        Args:
            rule_pack_index_file: Path to rule pack index JSON file
        """
        self.rule_pack_index_file = rule_pack_index_file or Path("./data/oran_learning/rule_pack_index.json")
        self.rule_pack_index_file.parent.mkdir(parents=True, exist_ok=True)
    
    def find_similar_documents(
        self,
        new_fingerprint: Dict,
        existing_fingerprints: List[Dict],
        top_k: int = 5
    ) -> List[MatchResult]:
        """
        Find documents similar to the new fingerprint
        
        Args:
            new_fingerprint: Fingerprint of document to match
            existing_fingerprints: List of existing document fingerprints
            top_k: Number of top matches to return
            
        Returns:
            List of MatchResult objects, sorted by similarity (highest first)
        """
        if not existing_fingerprints:
            logger.info("No existing fingerprints to compare against")
            return []
        
        logger.info(f"Finding similar documents among {len(existing_fingerprints)} candidates")
        
        matches = []
        for existing_fp in existing_fingerprints:
            # Skip self-match
            if existing_fp.get("text_hash") == new_fingerprint.get("text_hash"):
                continue
            
            # Calculate similarity score
            score = self._calculate_similarity(new_fingerprint, existing_fp)
            
            # Only include if above threshold
            if score >= self.SIMILARITY_THRESHOLD:
                # Try to find associated rule pack
                rule_pack_id = self._get_rule_pack_for_fingerprint(existing_fp)
                matches.append(MatchResult(existing_fp, score, rule_pack_id))
        
        # Sort by similarity score (highest first)
        matches.sort(key=lambda m: m.similarity_score, reverse=True)
        
        logger.info(f"Found {len(matches)} similar documents above threshold {self.SIMILARITY_THRESHOLD}")
        
        return matches[:top_k]
    
    def get_best_rule_pack(
        self,
        new_fingerprint: Dict,
        existing_fingerprints: List[Dict]
    ) -> Optional[str]:
        """
        Get the best matching rule pack for a new document
        
        Args:
            new_fingerprint: Fingerprint of document to match
            existing_fingerprints: List of existing document fingerprints
            
        Returns:
            Rule pack ID of best match, or None if no match above threshold
        """
        matches = self.find_similar_documents(new_fingerprint, existing_fingerprints, top_k=1)
        
        if matches:
            best_match = matches[0]
            if best_match.rule_pack_id:
                logger.info(
                    f"Best rule pack match: {best_match.rule_pack_id} "
                    f"(similarity: {best_match.similarity_score:.2f}, "
                    f"source: {best_match.file_name})"
                )
                return best_match.rule_pack_id
        
        logger.info("No suitable rule pack found")
        return None
    
    def _calculate_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """
        Calculate similarity score between two fingerprints
        
        Args:
            fp1: First fingerprint
            fp2: Second fingerprint
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # 1. Structural similarity (40%)
        structural_score = self._structural_similarity(fp1, fp2)
        
        # 2. Keyword overlap (30%)
        keyword_score = self._keyword_similarity(fp1, fp2)
        
        # 3. Section pattern similarity (30%)
        section_score = self._section_pattern_similarity(fp1, fp2)
        
        # Weighted sum
        total_score = (
            self.WEIGHT_STRUCTURAL * structural_score +
            self.WEIGHT_KEYWORDS * keyword_score +
            self.WEIGHT_SECTIONS * section_score
        )
        
        return min(total_score, 1.0)  # Cap at 1.0
    
    def _structural_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """
        Compare structural features (numbering style, depth distribution, subsections)
        
        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.0
        components = 0
        
        # 1. Section numbering style (0.0 or 1.0)
        if fp1.get("section_numbering_style") == fp2.get("section_numbering_style"):
            score += 1.0
        components += 1
        
        # 2. Has numbered subsections (0.0 or 1.0)
        if fp1.get("has_numbered_subsections") == fp2.get("has_numbered_subsections"):
            score += 1.0
        components += 1
        
        # 3. Depth histogram similarity (Jaccard-like)
        depth_hist1 = fp1.get("depth_histogram", {})
        depth_hist2 = fp2.get("depth_histogram", {})
        if depth_hist1 or depth_hist2:
            depth_similarity = self._dict_similarity(depth_hist1, depth_hist2)
            score += depth_similarity
            components += 1
        
        # 4. Document type match
        if fp1.get("document_type") == fp2.get("document_type"):
            score += 1.0
        components += 1
        
        return score / components if components > 0 else 0.0
    
    def _keyword_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """
        Calculate keyword overlap using Jaccard similarity
        
        Returns:
            Score between 0.0 and 1.0
        """
        # Extract keywords from sample headings
        keywords1 = set()
        keywords2 = set()
        
        for heading in fp1.get("sample_headings", []):
            title = heading.get("title", "").lower()
            keywords1.update(title.split())
        
        for heading in fp2.get("sample_headings", []):
            title = heading.get("title", "").lower()
            keywords2.update(title.split())
        
        # Remove common words
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        keywords1 -= stopwords
        keywords2 -= stopwords
        
        # Jaccard similarity
        if not keywords1 and not keywords2:
            return 0.0
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        return intersection / union if union > 0 else 0.0
    
    def _section_pattern_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """
        Compare heading patterns (Level 1 sections)
        
        Returns:
            Score between 0.0 and 1.0
        """
        patterns1 = fp1.get("heading_patterns", [])
        patterns2 = fp2.get("heading_patterns", [])
        
        if not patterns1 and not patterns2:
            return 0.0
        if not patterns1 or not patterns2:
            return 0.0
        
        # Compare section numbers (e.g., both have sections 1, 2, 3, 4...)
        section_nums1 = {p.get("section_number", "") for p in patterns1}
        section_nums2 = {p.get("section_number", "") for p in patterns2}
        
        # Jaccard similarity on section numbers
        intersection = len(section_nums1 & section_nums2)
        union = len(section_nums1 | section_nums2)
        number_similarity = intersection / union if union > 0 else 0.0
        
        # Compare title keywords
        title_keywords1 = set()
        title_keywords2 = set()
        
        for p in patterns1:
            title_keywords1.update(p.get("title", "").lower().split())
        for p in patterns2:
            title_keywords2.update(p.get("title", "").lower().split())
        
        # Remove stopwords
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        title_keywords1 -= stopwords
        title_keywords2 -= stopwords
        
        if title_keywords1 and title_keywords2:
            intersection_titles = len(title_keywords1 & title_keywords2)
            union_titles = len(title_keywords1 | title_keywords2)
            title_similarity = intersection_titles / union_titles if union_titles > 0 else 0.0
        else:
            title_similarity = 0.0
        
        # Average of both similarities
        return (number_similarity + title_similarity) / 2.0
    
    def _dict_similarity(self, dict1: Dict, dict2: Dict) -> float:
        """
        Calculate similarity between two dictionaries using Jaccard-like measure
        
        Returns:
            Score between 0.0 and 1.0
        """
        if not dict1 and not dict2:
            return 1.0  # Both empty is perfect match
        if not dict1 or not dict2:
            return 0.0
        
        all_keys = set(dict1.keys()) | set(dict2.keys())
        if not all_keys:
            return 0.0
        
        # Compare values for common keys
        common_keys = set(dict1.keys()) & set(dict2.keys())
        similar_count = 0
        
        for key in common_keys:
            val1 = dict1[key]
            val2 = dict2[key]
            # Values are similar if within 20% of each other
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if val2 != 0 and abs(val1 - val2) / max(abs(val1), abs(val2)) <= 0.2:
                    similar_count += 1
        
        return similar_count / len(all_keys) if all_keys else 0.0
    
    def _get_rule_pack_for_fingerprint(self, fingerprint: Dict) -> Optional[str]:
        """
        Find rule pack ID associated with a fingerprint
        
        Args:
            fingerprint: Document fingerprint
            
        Returns:
            Rule pack ID if found, None otherwise
        """
        # Load rule pack index
        index = self._load_rule_pack_index()
        
        # Look for rule pack by document type
        doc_type = fingerprint.get("document_type", "UNKNOWN")
        rule_pack_ids = index.get(doc_type, [])
        
        if rule_pack_ids:
            # Return first rule pack for this document type
            # In future, could match by text_hash for more precision
            return rule_pack_ids[0]
        
        return None
    
    def _load_rule_pack_index(self) -> Dict[str, List[str]]:
        """
        Load rule pack index mapping document types to rule pack IDs
        
        Returns:
            Dictionary mapping document type -> list of rule pack IDs
        """
        if not self.rule_pack_index_file.exists():
            return {}
        
        try:
            with open(self.rule_pack_index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load rule pack index: {e}")
            return {}
