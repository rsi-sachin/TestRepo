"""
Semantic Version Tracker for ETSI Specifications
Tracks document versions, detects compatibility changes, and identifies breaking changes.
Based on Section 4.2 of TS 103987: Compatibility of A1 versions

Module Purpose:
- Track specification versions across multiple documents
- Detect version changes (major/minor/patch)
- Assess backward compatibility per TS 103987 rules
- Generate version diff reports for documentation
- Support version history persistence

Version Change Rules (TS 103987 Section 4.2):
- MAJOR (1st digit): New major feature or incompatible change (breaking)
- MINOR (2nd digit): Optional features, clarifications, corrections (backward compatible)
- PATCH (3rd digit): Bug fixes
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
import re
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class VersionChangeType(str, Enum):
    """Type of version change between documents"""
    MAJOR = "major"           # Breaking change (1st digit: new feature/incompatible)
    MINOR = "minor"           # Backward compatible (2nd digit: optional features/clarifications)
    PATCH = "patch"           # Bug fixes/corrections
    INCOMPATIBLE = "incompatible"
    NO_CHANGE = "no_change"


class CompatibilityLevel(str, Enum):
    """Backward compatibility assessment per TS 103987 Section 4.2"""
    FULLY_COMPATIBLE = "fully_compatible"
    PARTIALLY_COMPATIBLE = "partially_compatible"
    BREAKING = "breaking"


@dataclass
class SemanticVersion:
    """Semantic version per TS 103987 versioning strategy"""
    major: int
    minor: int
    patch: int = 0
    spec_identifier: str = ""  # e.g., "TS_103987"
    release_date: Optional[datetime] = None
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}" if self.patch else f"{self.major}.{self.minor}"
    
    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.major, self.minor, self.patch)
    
    @classmethod
    def parse(cls, version_str: str, spec_id: str = "") -> "SemanticVersion":
        """
        Parse version strings: v4.3.0, 4.3, v040300p, 2025-05
        
        Args:
            version_str: Version string to parse
            spec_id: Specification identifier for context
            
        Returns:
            SemanticVersion instance
        """
        version_str = str(version_str).strip()
        
        # ETSI format: v040300p -> 4.3.0
        etsi_match = re.match(r"v(\d)(\d{2})(\d{2})", version_str)
        if etsi_match:
            return cls(
                major=int(etsi_match.group(1)),
                minor=int(etsi_match.group(2)),
                patch=int(etsi_match.group(3)),
                spec_identifier=spec_id
            )
        
        # Standard: 4.3.0 or v4.3.0
        std_match = re.match(r"v?(\d+)\.(\d+)(?:\.(\d+))?", version_str)
        if std_match:
            return cls(
                major=int(std_match.group(1)),
                minor=int(std_match.group(2)),
                patch=int(std_match.group(3) or 0),
                spec_identifier=spec_id
            )
        
        logger.warning(f"Could not parse version: {version_str}")
        return cls(major=0, minor=0, patch=0, spec_identifier=spec_id)
    
    def is_compatible_with(self, other: "SemanticVersion") -> CompatibilityLevel:
        """
        Assess compatibility per TS 103987 rules.
        
        Compatibility Logic:
        - Different major version: BREAKING
        - Same major, different minor/patch: PARTIALLY_COMPATIBLE
        - Identical versions: FULLY_COMPATIBLE
        """
        if self.major != other.major:
            return CompatibilityLevel.BREAKING
        if self.minor != other.minor or self.patch != other.patch:
            return CompatibilityLevel.PARTIALLY_COMPATIBLE
        return CompatibilityLevel.FULLY_COMPATIBLE


@dataclass
class VersionChange:
    """Description of a change between two versions"""
    change_type: VersionChangeType
    from_version: SemanticVersion
    to_version: SemanticVersion
    compatibility: CompatibilityLevel
    breaking_details: str = ""
    affected_services: List[str] = field(default_factory=list)
    affected_apis: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_breaking(self) -> bool:
        """Check if this is a breaking change"""
        return self.change_type in [VersionChangeType.MAJOR, VersionChangeType.INCOMPATIBLE]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "change_type": self.change_type.value,
            "from_version": str(self.from_version),
            "to_version": str(self.to_version),
            "compatibility": self.compatibility.value,
            "breaking": self.is_breaking(),
            "breaking_details": self.breaking_details,
            "affected_services": self.affected_services,
            "affected_apis": self.affected_apis,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class DocumentVersionHistory:
    """Track version history for a single document"""
    spec_type: str
    current_version: SemanticVersion
    history: List[SemanticVersion] = field(default_factory=list)
    changes: List[VersionChange] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def add_version(self, version: SemanticVersion, detect_changes: bool = True) -> Optional[VersionChange]:
        """
        Add new version to history and detect changes.
        
        Args:
            version: New version to add
            detect_changes: Whether to detect and record changes
            
        Returns:
            VersionChange if version differs from current, else None
        """
        if version.to_tuple() == self.current_version.to_tuple():
            return None
        
        change = None
        if detect_changes:
            change = self._detect_change(self.current_version, version)
            self.changes.append(change)
        
        self.history.append(self.current_version)
        self.current_version = version
        self.last_updated = datetime.now()
        return change
    
    def _detect_change(self, from_v: SemanticVersion, to_v: SemanticVersion) -> VersionChange:
        """Detect type of change"""
        from_tuple = from_v.to_tuple()
        to_tuple = to_v.to_tuple()
        
        if to_tuple < from_tuple:
            change_type = VersionChangeType.INCOMPATIBLE
            details = "Version downgrade detected"
        elif to_tuple[0] > from_tuple[0]:
            change_type = VersionChangeType.MAJOR
            details = "New major feature or incompatible change"
        elif to_tuple[1] > from_tuple[1]:
            change_type = VersionChangeType.MINOR
            details = "Optional features/clarifications added"
        else:
            change_type = VersionChangeType.PATCH
            details = "Bug fixes or corrections"
        
        compatibility = from_v.is_compatible_with(to_v)
        
        return VersionChange(
            change_type=change_type,
            from_version=from_v,
            to_version=to_v,
            compatibility=compatibility,
            breaking_details=details
        )


class SemanticVersionTracker:
    """Tracks versions across multiple documents"""
    
    def __init__(self, history_file: Optional[Path] = None):
        """Initialize tracker with optional persistence file"""
        self.documents: Dict[str, DocumentVersionHistory] = {}
        self.history_file = history_file or Path("./data/oran_learning/version_history.json")
        self.load_history()
    
    def register_document(self, spec_type: str, version: SemanticVersion) -> None:
        """Register a new document or update existing"""
        if spec_type not in self.documents:
            self.documents[spec_type] = DocumentVersionHistory(spec_type, version)
            logger.info(f"Registered {spec_type} version {version}")
        else:
            change = self.documents[spec_type].add_version(version)
            if change and change.is_breaking():
                logger.warning(
                    f"{spec_type} BREAKING CHANGE: {change.from_version} → {change.to_version}"
                )
    
    def extract_version_from_text(self, text: str, spec_type: str = "") -> Optional[SemanticVersion]:
        """
        Extract version string from document text.
        
        Patterns:
        - "ETSI TS 103 987 V4.3.0"
        - "Version 4.3.0"
        - "v4.3.0"
        """
        # Pattern: ETSI TS #### V#.#.#
        etsi_match = re.search(r"ETSI\s+(?:TS\s+)?(\d+\s+\d+)\s+V([\d.]+)", text)
        if etsi_match:
            return SemanticVersion.parse(etsi_match.group(2), spec_type)
        
        # Pattern: Version #.#.#
        version_match = re.search(r"[Vv]ersion\s+([\d.]+)", text)
        if version_match:
            return SemanticVersion.parse(version_match.group(1), spec_type)
        
        return None
    
    def detect_breaking_changes(self, spec_type: str) -> List[VersionChange]:
        """Get all breaking changes for a spec"""
        if spec_type not in self.documents:
            return []
        return [c for c in self.documents[spec_type].changes if c.is_breaking()]
    
    def get_version_diff_report(self) -> Dict:
        """Generate comprehensive version diff report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "documents": {},
            "breaking_changes": [],
            "summary": {}
        }
        
        for spec_type, history in self.documents.items():
            report["documents"][spec_type] = {
                "current_version": str(history.current_version),
                "version_count": len(history.history) + 1,
                "last_updated": history.last_updated.isoformat(),
                "changes": [c.to_dict() for c in history.changes]
            }
            
            report["breaking_changes"].extend(
                [{"spec": spec_type, **c.to_dict()} for c in history.changes if c.is_breaking()]
            )
        
        report["summary"] = {
            "total_specs_tracked": len(self.documents),
            "total_version_changes": sum(len(h.changes) for h in self.documents.values()),
            "total_breaking_changes": len(report["breaking_changes"])
        }
        
        return report
    
    def save_history(self) -> None:
        """Persist version history to file"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "documents": {
                spec_type: {
                    "current_version": str(history.current_version),
                    "version_history": [str(v) for v in history.history],
                    "changes": [c.to_dict() for c in history.changes]
                }
                for spec_type, history in self.documents.items()
            }
        }
        
        with open(self.history_file, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved version history to {self.history_file}")
    
    def load_history(self) -> None:
        """Load version history from file"""
        if not self.history_file.exists():
            logger.debug(f"No version history file found at {self.history_file}")
            return
        
        try:
            with open(self.history_file, "r") as f:
                data = json.load(f)
            
            for spec_type, doc_data in data.get("documents", {}).items():
                version_str = doc_data.get("current_version", "0.0")
                version = SemanticVersion.parse(version_str, spec_type)
                self.register_document(spec_type, version)
                
                logger.debug(f"Loaded {spec_type} version {version} from history")
        
        except Exception as e:
            logger.error(f"Failed to load version history: {e}")
