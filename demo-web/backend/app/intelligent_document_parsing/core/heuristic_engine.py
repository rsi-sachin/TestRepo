"""
Heuristic engine for extracting decisions, action items, and information gaps.

Uses 4 complementary methods:
1. Regex keyword matching
2. Sentence structure pattern matching
3. TF-IDF based scoring
4. Rule-based heuristics
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

from ..models.analysis_models import ExtractionMethod, DecisionType, ItemPriority
from ..utils.text_utils import (
    KeywordMatcher, PatternMatcher, TfIdfScorer, 
    TextTokenizer, TextNormalizer
)

logger = logging.getLogger(__name__)


@dataclass
class ExtractionRule:
    """User-defined extraction rule."""
    id: str
    name: str
    rule_type: str  # "decision", "action", "gap"
    pattern: str  # regex pattern
    decision_type: Optional[str] = None
    priority: Optional[str] = None
    confidence_boost: float = 0.2


class HeuristicEngine:
    """Multi-method heuristic extraction engine."""
    
    def __init__(self):
        self.custom_rules: List[ExtractionRule] = []
        self.method_weights = {
            ExtractionMethod.REGEX_KEYWORD: 0.25,
            ExtractionMethod.SENTENCE_PATTERN: 0.25,
            ExtractionMethod.TF_IDF_SCORING: 0.25,
            ExtractionMethod.RULE_BASED: 0.25,
        }
    
    def add_custom_rule(self, rule: ExtractionRule):
        """Add a custom extraction rule."""
        self.custom_rules.append(rule)
        logger.info(f"Added custom rule: {rule.name}")
    
    def extract_decisions(self, text: str) -> List[Tuple[str, float, List[str]]]:
        """
        Extract potential decisions from text.
        Returns list of (text, confidence, methods_used).
        """
        sentences = TextNormalizer.extract_sentences(text)
        results = []
        
        for sentence in sentences:
            if len(sentence) < 10:
                continue
            
            scores = []
            methods_used = []
            
            # Method 1: Keyword matching
            kw_score, keywords = KeywordMatcher.score_decision_keywords(sentence)
            if kw_score > 0:
                scores.append(kw_score)
                methods_used.append(ExtractionMethod.REGEX_KEYWORD)
            
            # Method 2: Pattern matching
            pattern_score, _ = PatternMatcher.match_patterns(
                sentence, 
                PatternMatcher.REQUIREMENT_PATTERNS
            )
            if pattern_score > 0:
                scores.append(pattern_score)
                methods_used.append(ExtractionMethod.SENTENCE_PATTERN)
            
            # Method 3: TF-IDF (semantic importance)
            tokens = TextTokenizer.tokenize_meaningful(sentence)
            if tokens:
                # Use all sentences for IDF context
                all_sentences = [TextTokenizer.tokenize_meaningful(s) for s in sentences]
                idf = TfIdfScorer.calculate_idf(all_sentences)
                tfidf = TfIdfScorer.calculate_tfidf(tokens, idf)
                avg_tfidf = sum(tfidf.values()) / len(tfidf) if tfidf else 0
                if avg_tfidf > 0.01:
                    scores.append(min(0.7, avg_tfidf * 2))
                    methods_used.append(ExtractionMethod.TF_IDF_SCORING)
            
            # Method 4: Custom rules
            rule_score = self._apply_custom_rules(sentence, "decision")
            if rule_score > 0:
                scores.append(rule_score)
                methods_used.append(ExtractionMethod.RULE_BASED)
            
            # Calculate combined confidence
            if scores:
                combined_confidence = self._combine_scores(scores)
                if combined_confidence >= 0.3:  # Threshold
                    results.append((sentence, combined_confidence, methods_used))
        
        return results
    
    def extract_action_items(self, text: str) -> List[Tuple[str, float, List[str], str]]:
        """
        Extract action items from text.
        Returns list of (text, confidence, methods_used, priority_hint).
        """
        sentences = TextNormalizer.extract_sentences(text)
        results = []
        
        for sentence in sentences:
            if len(sentence) < 10:
                continue
            
            scores = []
            methods_used = []
            
            # Method 1: Action keyword matching
            kw_score, keywords = KeywordMatcher.score_action_keywords(sentence)
            if kw_score > 0:
                scores.append(kw_score)
                methods_used.append(ExtractionMethod.REGEX_KEYWORD)
            
            # Method 2: Action pattern matching
            pattern_score, _ = PatternMatcher.match_patterns(
                sentence,
                PatternMatcher.ACTION_PATTERNS
            )
            if pattern_score > 0:
                scores.append(pattern_score)
                methods_used.append(ExtractionMethod.SENTENCE_PATTERN)
            
            # Method 3: Importance via TF-IDF
            tokens = TextTokenizer.tokenize_meaningful(sentence)
            if tokens:
                all_sentences = [TextTokenizer.tokenize_meaningful(s) for s in sentences]
                idf = TfIdfScorer.calculate_idf(all_sentences)
                tfidf = TfIdfScorer.calculate_tfidf(tokens, idf)
                avg_tfidf = sum(tfidf.values()) / len(tfidf) if tfidf else 0
                if avg_tfidf > 0.01:
                    scores.append(min(0.7, avg_tfidf * 2))
                    methods_used.append(ExtractionMethod.TF_IDF_SCORING)
            
            # Method 4: Custom rules
            rule_score = self._apply_custom_rules(sentence, "action")
            if rule_score > 0:
                scores.append(rule_score)
                methods_used.append(ExtractionMethod.RULE_BASED)
            
            # Infer priority
            priority = self._infer_priority(sentence)
            
            if scores:
                combined_confidence = self._combine_scores(scores)
                if combined_confidence >= 0.3:
                    results.append((sentence, combined_confidence, methods_used, priority))
        
        return results
    
    def extract_information_gaps(self, text: str) -> List[Tuple[str, float, List[str]]]:
        """
        Extract information gaps from text.
        Returns list of (text, confidence, methods_used).
        """
        sentences = TextNormalizer.extract_sentences(text)
        results = []
        
        for sentence in sentences:
            if len(sentence) < 10:
                continue
            
            scores = []
            methods_used = []
            
            # Method 1: Gap keyword matching
            kw_score, keywords = KeywordMatcher.score_gap_keywords(sentence)
            if kw_score > 0:
                scores.append(kw_score)
                methods_used.append(ExtractionMethod.REGEX_KEYWORD)
            
            # Method 2: Gap pattern matching
            pattern_score, _ = PatternMatcher.match_patterns(
                sentence,
                PatternMatcher.GAP_PATTERNS
            )
            if pattern_score > 0:
                scores.append(pattern_score)
                methods_used.append(ExtractionMethod.SENTENCE_PATTERN)
            
            # Method 3: TF-IDF (highlight infrequent terms = potentially important gaps)
            tokens = TextTokenizer.tokenize_meaningful(sentence)
            if tokens:
                all_sentences = [TextTokenizer.tokenize_meaningful(s) for s in sentences]
                idf = TfIdfScorer.calculate_idf(all_sentences)
                tfidf = TfIdfScorer.calculate_tfidf(tokens, idf)
                avg_tfidf = sum(tfidf.values()) / len(tfidf) if tfidf else 0
                if avg_tfidf > 0.02:  # High specificity
                    scores.append(min(0.7, avg_tfidf * 2))
                    methods_used.append(ExtractionMethod.TF_IDF_SCORING)
            
            # Method 4: Custom rules
            rule_score = self._apply_custom_rules(sentence, "gap")
            if rule_score > 0:
                scores.append(rule_score)
                methods_used.append(ExtractionMethod.RULE_BASED)
            
            if scores:
                combined_confidence = self._combine_scores(scores)
                if combined_confidence >= 0.2:  # Lower threshold for gaps
                    results.append((sentence, combined_confidence, methods_used))
        
        return results
    
    def _combine_scores(self, scores: list) -> float:
        """Combine scores from multiple methods.
        
        When 2+ independent methods agree, add an agreement bonus
        that rewards corroboration over individual method noise.
        """
        if not scores:
            return 0.0
        base = sum(scores) / len(scores)
        agreement_bonus = 0.05 * (len(scores) - 1)  # +0.05 per extra method
        return min(1.0, base + agreement_bonus)

    def _apply_custom_rules(self, text: str, rule_type: str) -> float:
        """Apply custom rules and return confidence boost."""
        max_score = 0.0
        for rule in self.custom_rules:
            if rule.rule_type == rule_type:
                try:
                    if re.search(rule.pattern, text, re.IGNORECASE):
                        max_score = max(max_score, rule.confidence_boost)
                except re.error:
                    logger.warning(f"Invalid regex in rule {rule.id}: {rule.pattern}")
        return max_score
    
    def _infer_priority(self, text: str) -> str:
        """Infer priority level from text."""
        text_lower = text.lower()
        
        critical_words = {'critical', 'blocking', 'urgent', 'immediately', 'asap'}
        high_words = {'important', 'required', 'must', 'shall', 'essential'}
        medium_words = {'should', 'recommended', 'consider', 'prefer'}
        
        if any(word in text_lower for word in critical_words):
            return ItemPriority.CRITICAL.value
        elif any(word in text_lower for word in high_words):
            return ItemPriority.HIGH.value
        elif any(word in text_lower for word in medium_words):
            return ItemPriority.MEDIUM.value
        else:
            return ItemPriority.LOW.value
    
    def set_method_weights(self, weights: Dict[ExtractionMethod, float]):
        """Adjust weights for different heuristic methods."""
        total = sum(weights.values())
        if total > 0:
            self.method_weights = {k: v / total for k, v in weights.items()}
