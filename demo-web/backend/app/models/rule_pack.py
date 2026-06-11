"""
Rule Pack Models
Pydantic schemas for rule-based document extraction system
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class ExtractionMethod(str, Enum):
    """Method for extracting content"""
    HEADING_MATCH = "HEADING_MATCH"       # Match by heading patterns (regex)
    KEYWORD_SCAN = "KEYWORD_SCAN"         # Scan for keywords in content
    SECTION_RANGE = "SECTION_RANGE"       # Extract by section number range (e.g., 5.x-6.x)
    COMBINED = "COMBINED"                 # Combine multiple methods


class PatternMatcher(BaseModel):
    """Pattern matching configuration"""
    pattern: str = Field(..., description="Regex pattern to match")
    flags: Optional[str] = Field(None, description="Regex flags (e.g., 'IGNORECASE')")
    examples: List[str] = Field(default_factory=list, description="Example matches for documentation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pattern": r"^4\.\s+Test\s+Methodology",
                "flags": "IGNORECASE",
                "examples": ["4. Test Methodology", "4. Test methodology"]
            }
        }


class ExtractionRule(BaseModel):
    """Rule for extracting content at a specific hierarchy level"""
    level: int = Field(..., description="Hierarchy level (1=Methodology, 2=Features, etc.)", ge=1)
    level_name: str = Field(..., description="Human-readable name for this level (e.g., 'Features')")
    pattern: Optional[str] = Field(None, description="Primary regex pattern for matching")
    keywords: List[str] = Field(default_factory=list, description="Keywords that boost match confidence")
    required: bool = Field(default=False, description="Whether this level must be found")
    extraction_method: ExtractionMethod = Field(
        default=ExtractionMethod.HEADING_MATCH,
        description="Method to use for extraction"
    )
    parent_level: Optional[int] = Field(None, description="Parent level (for nested extraction)")
    section_range: Optional[str] = Field(None, description="Section number range (e.g., '5.x-6.x')")
    min_confidence: float = Field(default=0.5, description="Minimum confidence threshold (0.0-1.0)")
    pattern_matchers: List[PatternMatcher] = Field(
        default_factory=list,
        description="Multiple pattern matchers for this level"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "level": 1,
                "level_name": "Test Methodology",
                "pattern": r"^4\.\s+Test\s+Methodology",
                "keywords": ["test", "methodology", "conformance"],
                "required": True,
                "extraction_method": "HEADING_MATCH",
                "min_confidence": 0.8,
                "pattern_matchers": []
            }
        }


class HierarchyConfig(BaseModel):
    """Configuration for hierarchy extraction"""
    max_depth: int = Field(..., description="Maximum depth to extract", ge=1, le=10)
    level_definitions: Dict[int, str] = Field(
        ...,
        description="Mapping of level numbers to names (e.g., {1: 'Methodology', 2: 'Features'})"
    )
    extract_content: bool = Field(
        default=True,
        description="Whether to extract full content or just headings"
    )
    max_content_length: int = Field(
        default=500,
        description="Maximum characters of content to extract per node"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "max_depth": 4,
                "level_definitions": {
                    1: "Test Methodology",
                    2: "Features",
                    3: "Modules",
                    4: "Test Cases"
                },
                "extract_content": True,
                "max_content_length": 500
            }
        }


class MatchStatistics(BaseModel):
    """Statistics about rule pack application success"""
    success_count: int = Field(default=0, description="Number of successful applications")
    failure_count: int = Field(default=0, description="Number of failed applications")
    avg_quality_score: float = Field(default=0.0, description="Average quality score (0.0-1.0)")
    last_used: Optional[datetime] = Field(None, description="Last time this rule pack was used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success_count": 15,
                "failure_count": 2,
                "avg_quality_score": 0.85,
                "last_used": "2026-06-11T10:30:00"
            }
        }


class RulePack(BaseModel):
    """Complete rule pack for hierarchical extraction"""
    id: str = Field(..., description="Unique rule pack identifier (UUID)")
    name: str = Field(..., description="Human-readable name")
    description: Optional[str] = Field(None, description="Description of what this rule pack is for")
    created_date: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_date: Optional[datetime] = Field(None, description="Last update timestamp")
    
    # Source information
    source_document_hash: str = Field(
        ...,
        description="Hash of the document this rule pack was learned from"
    )
    source_document_name: str = Field(..., description="Name of source document")
    document_type: str = Field(..., description="Type of document (TEST_SPECIFICATION, etc.)")
    
    # Extraction configuration
    hierarchy_config: HierarchyConfig = Field(..., description="Hierarchy configuration")
    extraction_rules: List[ExtractionRule] = Field(
        ...,
        description="Extraction rules ordered by level"
    )
    
    # Performance tracking
    match_statistics: MatchStatistics = Field(
        default_factory=MatchStatistics,
        description="Statistics about rule pack usage"
    )
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    version: str = Field(default="1.0", description="Rule pack version")
    author: Optional[str] = Field(None, description="Rule pack author")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "ETSI Test Spec Baseline",
                "description": "Baseline rule pack for ETSI test specifications (TS 103 989 style)",
                "created_date": "2026-06-11T10:00:00",
                "source_document_hash": "abc123def456",
                "source_document_name": "ts_103989v040200p.pdf",
                "document_type": "TEST_SPECIFICATION",
                "hierarchy_config": {
                    "max_depth": 4,
                    "level_definitions": {
                        1: "Test Methodology",
                        2: "Features",
                        3: "Modules",
                        4: "Test Cases"
                    },
                    "extract_content": True,
                    "max_content_length": 500
                },
                "extraction_rules": [],
                "match_statistics": {
                    "success_count": 0,
                    "failure_count": 0,
                    "avg_quality_score": 0.0
                },
                "tags": ["ETSI", "A1", "test-spec"],
                "version": "1.0"
            }
        }
    
    def get_rule_by_level(self, level: int) -> Optional[ExtractionRule]:
        """Get extraction rule for specific level"""
        for rule in self.extraction_rules:
            if rule.level == level:
                return rule
        return None
    
    def get_max_level(self) -> int:
        """Get maximum level defined in rules"""
        if not self.extraction_rules:
            return 0
        return max(rule.level for rule in self.extraction_rules)
    
    def update_statistics(self, success: bool, quality_score: float):
        """Update match statistics after applying rule pack"""
        if success:
            self.match_statistics.success_count += 1
        else:
            self.match_statistics.failure_count += 1
        
        # Update average quality score
        total_applications = (
            self.match_statistics.success_count +
            self.match_statistics.failure_count
        )
        current_avg = self.match_statistics.avg_quality_score
        new_avg = ((current_avg * (total_applications - 1)) + quality_score) / total_applications
        self.match_statistics.avg_quality_score = round(new_avg, 3)
        
        self.match_statistics.last_used = datetime.now()
        self.updated_date = datetime.now()


class RulePackSummary(BaseModel):
    """Summary of a rule pack for listing purposes"""
    id: str
    name: str
    description: Optional[str] = None
    document_type: str
    created_date: datetime
    success_count: int = 0
    failure_count: int = 0
    avg_quality_score: float = 0.0
    version: str = "1.0"
    tags: List[str] = Field(default_factory=list)
    
    @classmethod
    def from_rule_pack(cls, rule_pack: RulePack) -> "RulePackSummary":
        """Create summary from full rule pack"""
        return cls(
            id=rule_pack.id,
            name=rule_pack.name,
            description=rule_pack.description,
            document_type=rule_pack.document_type,
            created_date=rule_pack.created_date,
            success_count=rule_pack.match_statistics.success_count,
            failure_count=rule_pack.match_statistics.failure_count,
            avg_quality_score=rule_pack.match_statistics.avg_quality_score,
            version=rule_pack.version,
            tags=rule_pack.tags
        )
