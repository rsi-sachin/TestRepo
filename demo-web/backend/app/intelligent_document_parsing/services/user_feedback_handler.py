"""
User feedback handler for validating extractions and refining rules.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class UserFeedback:
    """User validation feedback on an extraction."""
    item_id: str
    item_type: str  # "decision", "action", "gap"
    is_valid: bool
    feedback_text: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    user_id: str = "user"
    suggested_correction: Optional[str] = None


@dataclass
class FeedbackStats:
    """Statistics on extraction accuracy."""
    total_validations: int = 0
    valid_count: int = 0
    invalid_count: int = 0
    accuracy: float = 0.0


class UserFeedbackHandler:
    """Manage user feedback and rule refinement."""
    
    def __init__(self):
        self.feedback_history: List[UserFeedback] = []
        self.stats_by_type: Dict[str, FeedbackStats] = {
            "decision": FeedbackStats(),
            "action": FeedbackStats(),
            "gap": FeedbackStats(),
        }
        self.suggested_rules: List[Dict] = []
    
    def record_feedback(self, feedback: UserFeedback):
        """Record user validation feedback."""
        self.feedback_history.append(feedback)
        
        # Update stats
        stats = self.stats_by_type.get(feedback.item_type)
        if stats:
            stats.total_validations += 1
            if feedback.is_valid:
                stats.valid_count += 1
            else:
                stats.invalid_count += 1
            
            stats.accuracy = stats.valid_count / stats.total_validations if stats.total_validations > 0 else 0.0
        
        logger.info(
            f"Feedback recorded: {feedback.item_type} {feedback.item_id} - "
            f"Valid: {feedback.is_valid}"
        )
        
        # If invalid, suggest rule refinement
        if not feedback.is_valid and feedback.suggested_correction:
            self._suggest_rule_refinement(feedback)
    
    def get_accuracy_report(self) -> Dict[str, Dict]:
        """Get accuracy report by item type."""
        report = {}
        for item_type, stats in self.stats_by_type.items():
            report[item_type] = {
                "total": stats.total_validations,
                "valid": stats.valid_count,
                "invalid": stats.invalid_count,
                "accuracy": round(stats.accuracy, 2) if stats.total_validations > 0 else 0.0,
            }
        return report
    
    def get_false_positives(self) -> List[UserFeedback]:
        """Get extractions marked as invalid (false positives)."""
        return [f for f in self.feedback_history if not f.is_valid]
    
    def get_false_negatives_hints(self) -> List[str]:
        """Get hints from feedback about false negatives."""
        hints = []
        for feedback in self.feedback_history:
            if feedback.feedback_text and "missed" in feedback.feedback_text.lower():
                hints.append(feedback.feedback_text)
        return hints
    
    def suggest_rules_from_feedback(self) -> List[Dict]:
        """Analyze feedback to suggest new extraction rules."""
        suggestions = []
        
        # Analyze false positives
        false_positives = self.get_false_positives()
        for fp in false_positives:
            if fp.suggested_correction:
                suggestion = {
                    "type": "exclusion_rule",
                    "item_type": fp.item_type,
                    "pattern": f"NOT({fp.suggested_correction})",
                    "reason": f"False positive - {fp.feedback_text}",
                    "confidence": 0.7,
                }
                suggestions.append(suggestion)
        
        # Analyze false negatives
        fn_hints = self.get_false_negatives_hints()
        for hint in fn_hints:
            suggestion = {
                "type": "inclusion_rule",
                "pattern": hint,
                "reason": "Missed in extraction",
                "confidence": 0.6,
            }
            suggestions.append(suggestion)
        
        self.suggested_rules = suggestions
        return suggestions
    
    def generate_refined_rules(self) -> str:
        """Generate refined rules in JSON format for model training."""
        refined = {
            "timestamp": datetime.now().isoformat(),
            "accuracy_report": self.get_accuracy_report(),
            "suggested_rules": self.suggested_rules,
            "feedback_count": len(self.feedback_history),
        }
        return json.dumps(refined, indent=2)
    
    def _suggest_rule_refinement(self, feedback: UserFeedback):
        """Suggest rules based on invalid feedback."""
        if feedback.item_type == "decision":
            suggestion = self._suggest_decision_rule(feedback)
        elif feedback.item_type == "action":
            suggestion = self._suggest_action_rule(feedback)
        elif feedback.item_type == "gap":
            suggestion = self._suggest_gap_rule(feedback)
        else:
            return
        
        if suggestion:
            logger.info(f"Suggested rule refinement: {suggestion}")
    
    def _suggest_decision_rule(self, feedback: UserFeedback) -> Optional[Dict]:
        """Suggest decision extraction rule."""
        if not feedback.suggested_correction:
            return None
        
        return {
            "rule_type": "decision",
            "pattern": f"(?i)({feedback.suggested_correction})",
            "confidence_boost": 0.1,
            "reason": f"Based on feedback: {feedback.feedback_text}",
        }
    
    def _suggest_action_rule(self, feedback: UserFeedback) -> Optional[Dict]:
        """Suggest action extraction rule."""
        if not feedback.suggested_correction:
            return None
        
        return {
            "rule_type": "action",
            "pattern": f"(?i)({feedback.suggested_correction})",
            "priority": "medium",
            "confidence_boost": 0.15,
            "reason": f"Based on feedback: {feedback.feedback_text}",
        }
    
    def _suggest_gap_rule(self, feedback: UserFeedback) -> Optional[Dict]:
        """Suggest gap extraction rule."""
        if not feedback.suggested_correction:
            return None
        
        return {
            "rule_type": "gap",
            "pattern": f"(?i)({feedback.suggested_correction})",
            "confidence_boost": 0.2,
            "reason": f"Based on feedback: {feedback.feedback_text}",
        }
    
    def export_feedback_log(self, filepath: str):
        """Export feedback log to JSON file."""
        logs = []
        for fb in self.feedback_history:
            logs.append({
                "item_id": fb.item_id,
                "type": fb.item_type,
                "valid": fb.is_valid,
                "feedback": fb.feedback_text,
                "timestamp": fb.timestamp,
                "user": fb.user_id,
            })
        
        with open(filepath, 'w') as f:
            json.dump(logs, f, indent=2)
        
        logger.info(f"Feedback log exported to {filepath}")
    
    def import_feedback_log(self, filepath: str):
        """Import feedback log from JSON file."""
        with open(filepath, 'r') as f:
            logs = json.load(f)
        
        for log in logs:
            feedback = UserFeedback(
                item_id=log["item_id"],
                item_type=log["type"],
                is_valid=log["valid"],
                feedback_text=log.get("feedback", ""),
                timestamp=log.get("timestamp", datetime.now().isoformat()),
                user_id=log.get("user", "user"),
            )
            self.record_feedback(feedback)
        
        logger.info(f"Feedback log imported from {filepath}")
