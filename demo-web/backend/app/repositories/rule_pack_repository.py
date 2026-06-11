"""
Rule Pack Repository
CRUD operations for rule pack persistence
"""

from pathlib import Path
from typing import List, Dict, Optional
import json
import logging
from datetime import datetime

from app.models.rule_pack import RulePack, RulePackSummary

logger = logging.getLogger(__name__)


class RulePackRepository:
    """Repository for managing rule pack storage"""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize repository
        
        Args:
            storage_dir: Directory for storing rule packs (default: data/oran_learning/rule_packs/)
        """
        self.storage_dir = storage_dir or Path("./data/oran_learning/rule_packs")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.storage_dir.parent / "rule_pack_index.json"
        self._ensure_index_exists()
    
    def _ensure_index_exists(self):
        """Ensure index file exists"""
        if not self.index_file.exists():
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)
            logger.info(f"Created rule pack index at {self.index_file}")
    
    def save_rule_pack(self, rule_pack: RulePack) -> bool:
        """
        Save rule pack to storage
        
        Args:
            rule_pack: Rule pack to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Save rule pack as JSON file
            rule_pack_file = self.storage_dir / f"{rule_pack.id}.json"
            
            with open(rule_pack_file, "w", encoding="utf-8") as f:
                json.dump(rule_pack.model_dump(mode="json"), f, indent=2, ensure_ascii=True, default=str)
            
            logger.info(f"Saved rule pack {rule_pack.id} to {rule_pack_file}")
            
            # Update index
            self._add_to_index(rule_pack)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save rule pack {rule_pack.id}: {e}")
            return False
    
    def load_rule_pack(self, rule_pack_id: str) -> Optional[RulePack]:
        """
        Load rule pack by ID
        
        Args:
            rule_pack_id: Rule pack identifier
            
        Returns:
            RulePack if found, None otherwise
        """
        try:
            rule_pack_file = self.storage_dir / f"{rule_pack_id}.json"
            
            if not rule_pack_file.exists():
                logger.warning(f"Rule pack {rule_pack_id} not found")
                return None
            
            with open(rule_pack_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            rule_pack = RulePack(**data)
            logger.info(f"Loaded rule pack {rule_pack_id}")
            return rule_pack
            
        except Exception as e:
            logger.error(f"Failed to load rule pack {rule_pack_id}: {e}")
            return None
    
    def list_rule_packs(self, document_type: Optional[str] = None) -> List[RulePackSummary]:
        """
        List all rule packs, optionally filtered by document type
        
        Args:
            document_type: Filter by document type (e.g., "TEST_SPECIFICATION")
            
        Returns:
            List of rule pack summaries
        """
        try:
            index = self._load_index()
            
            # Get all rule pack IDs
            all_ids = set()
            if document_type:
                all_ids = set(index.get(document_type, []))
            else:
                for ids in index.values():
                    all_ids.update(ids)
            
            # Load summaries
            summaries = []
            for rule_pack_id in all_ids:
                rule_pack = self.load_rule_pack(rule_pack_id)
                if rule_pack:
                    summaries.append(RulePackSummary.from_rule_pack(rule_pack))
            
            # Sort by creation date (newest first)
            summaries.sort(key=lambda s: s.created_date, reverse=True)
            
            logger.info(f"Listed {len(summaries)} rule packs")
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to list rule packs: {e}")
            return []
    
    def delete_rule_pack(self, rule_pack_id: str) -> bool:
        """
        Delete rule pack by ID
        
        Args:
            rule_pack_id: Rule pack identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load rule pack to get document type
            rule_pack = self.load_rule_pack(rule_pack_id)
            if not rule_pack:
                logger.warning(f"Rule pack {rule_pack_id} not found for deletion")
                return False
            
            # Delete file
            rule_pack_file = self.storage_dir / f"{rule_pack_id}.json"
            if rule_pack_file.exists():
                rule_pack_file.unlink()
                logger.info(f"Deleted rule pack file {rule_pack_file}")
            
            # Remove from index
            self._remove_from_index(rule_pack_id, rule_pack.document_type)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete rule pack {rule_pack_id}: {e}")
            return False
    
    def get_rule_packs_for_document_type(self, document_type: str) -> List[RulePack]:
        """
        Get all rule packs for a specific document type
        
        Args:
            document_type: Document type (e.g., "TEST_SPECIFICATION")
            
        Returns:
            List of rule packs
        """
        index = self._load_index()
        rule_pack_ids = index.get(document_type, [])
        
        rule_packs = []
        for rule_pack_id in rule_pack_ids:
            rule_pack = self.load_rule_pack(rule_pack_id)
            if rule_pack:
                rule_packs.append(rule_pack)
        
        return rule_packs
    
    def _load_index(self) -> Dict[str, List[str]]:
        """Load rule pack index"""
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load rule pack index: {e}")
            return {}
    
    def _save_index(self, index: Dict[str, List[str]]):
        """Save rule pack index"""
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(index, f, indent=2, ensure_ascii=True)
            logger.debug("Saved rule pack index")
        except Exception as e:
            logger.error(f"Failed to save rule pack index: {e}")
    
    def _add_to_index(self, rule_pack: RulePack):
        """Add rule pack to index"""
        index = self._load_index()
        
        doc_type = rule_pack.document_type
        if doc_type not in index:
            index[doc_type] = []
        
        # Add if not already in index
        if rule_pack.id not in index[doc_type]:
            index[doc_type].append(rule_pack.id)
            self._save_index(index)
            logger.info(f"Added rule pack {rule_pack.id} to index under {doc_type}")
    
    def _remove_from_index(self, rule_pack_id: str, document_type: str):
        """Remove rule pack from index"""
        index = self._load_index()
        
        if document_type in index:
            if rule_pack_id in index[document_type]:
                index[document_type].remove(rule_pack_id)
                self._save_index(index)
                logger.info(f"Removed rule pack {rule_pack_id} from index")
    
    def update_rule_pack(self, rule_pack: RulePack) -> bool:
        """
        Update existing rule pack
        
        Args:
            rule_pack: Updated rule pack
            
        Returns:
            True if successful, False otherwise
        """
        # Check if exists
        if not (self.storage_dir / f"{rule_pack.id}.json").exists():
            logger.warning(f"Rule pack {rule_pack.id} does not exist for update")
            return False
        
        # Update timestamp
        rule_pack.updated_date = datetime.now()
        
        # Save (same as create)
        return self.save_rule_pack(rule_pack)
    
    def get_statistics(self) -> Dict:
        """
        Get repository statistics
        
        Returns:
            Dictionary with statistics
        """
        index = self._load_index()
        
        total_packs = sum(len(ids) for ids in index.values())
        by_type = {doc_type: len(ids) for doc_type, ids in index.items()}
        
        return {
            "total_rule_packs": total_packs,
            "by_document_type": by_type,
            "storage_dir": str(self.storage_dir),
            "index_file": str(self.index_file)
        }
