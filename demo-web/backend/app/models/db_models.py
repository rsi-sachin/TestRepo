"""
Database ORM models for ORAN test cases
"""

from sqlalchemy import Boolean, Column, Integer, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base
from app.models.oran import SpecType, HttpMethod, ScenarioType


class TestCase(Base):
    """
    Test case extracted from ETSI specifications
    Stored in database for review, filtering, and modification
    """
    __tablename__ = "test_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Test details
    scenario = Column(Text, nullable=False)
    description = Column(Text)
    
    # Source information
    source_spec = Column(Enum(SpecType), nullable=False, index=True)
    source_section = Column(String(50), nullable=False, index=True)
    source_page = Column(Integer)
    scenario_type = Column(Enum(ScenarioType), nullable=True, index=True)
    simulator_required = Column(Boolean, nullable=False, default=False)
    configurable_request_parts = Column(Text, nullable=False, default="[]")
    
    # HTTP API details
    http_method = Column(Enum(HttpMethod), nullable=False, index=True)
    endpoint = Column(String(200), nullable=False)
    expected_status = Column(Integer, nullable=False)
    
    # Metadata
    complexity = Column(String(20), default="BASIC", index=True)
    catalog_id = Column(String(100), index=True)  # Link to original catalog
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    enrichments = relationship("TestCaseEnrichment", back_populates="test_case", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TestCase {self.test_id}: {self.scenario[:50]}>"


class EnrichmentType(str, enum.Enum):
    """Types of enrichment data from cross-referencing"""
    BASE = "base"
    ENDPOINT = "endpoint"
    STATUS_CODE = "status_code"
    PAYLOAD = "payload"
    VALIDATION = "validation"
    TERMINOLOGY = "terminology"


class TestCaseEnrichment(Base):
    """
    Enrichment data for test cases from cross-referencing multiple specs
    Displayed as tooltips in UI
    """
    __tablename__ = "test_case_enrichments"
    
    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False, index=True)
    
    # Enrichment details
    enrichment_type = Column(Enum(EnrichmentType), nullable=False)
    source_spec = Column(Enum(SpecType), nullable=False)
    source_section = Column(String(50))
    source_page = Column(Integer)
    value = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    test_case = relationship("TestCase", back_populates="enrichments")
    
    def __repr__(self):
        return f"<Enrichment {self.enrichment_type} from {self.source_spec}>"
