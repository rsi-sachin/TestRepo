"""
Hierarchy Tree Models
Data structures for representing extracted document hierarchies
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid


class ExtractionMetadata(BaseModel):
    """Metadata about how a node was extracted"""
    confidence: float = Field(..., description="Confidence score (0.0-1.0)", ge=0.0, le=1.0)
    match_pattern: Optional[str] = Field(None, description="Regex pattern that matched")
    match_method: Optional[str] = Field(None, description="Extraction method used")
    page_range: Optional[str] = Field(None, description="Page range where content was found")
    keywords_matched: List[str] = Field(default_factory=list, description="Keywords that matched")
    
    class Config:
        json_schema_extra = {
            "example": {
                "confidence": 0.85,
                "match_pattern": r"^4\.\s+Test\s+Methodology",
                "match_method": "HEADING_MATCH",
                "page_range": "12-15",
                "keywords_matched": ["test", "methodology", "conformance"]
            }
        }


class HierarchyNode(BaseModel):
    """Node in a document hierarchy tree"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique node identifier")
    level: int = Field(..., description="Hierarchy level (1=root, 2=child, etc.)", ge=1)
    level_name: str = Field(..., description="Name of this level (e.g., 'Features', 'Modules')")
    title: str = Field(..., description="Section title")
    section_number: Optional[str] = Field(None, description="Section number (e.g., '4.2.1')")
    content_text: Optional[str] = Field(None, description="Extracted content (truncated)")
    children: List["HierarchyNode"] = Field(default_factory=list, description="Child nodes")
    metadata: ExtractionMetadata = Field(..., description="Extraction metadata")
    parent_id: Optional[str] = Field(None, description="Parent node ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "node-123",
                "level": 2,
                "level_name": "Features",
                "title": "Conformance Testing Non-RT RIC",
                "section_number": "4.2",
                "content_text": "This section describes conformance testing...",
                "children": [],
                "metadata": {
                    "confidence": 0.9,
                    "match_pattern": r"^4\.\d+",
                    "match_method": "COMBINED",
                    "page_range": "15-18",
                    "keywords_matched": ["conformance", "testing", "RIC"]
                },
                "parent_id": "node-001"
            }
        }
    
    def add_child(self, child: "HierarchyNode"):
        """Add a child node"""
        child.parent_id = self.id
        self.children.append(child)
    
    def get_all_descendants(self) -> List["HierarchyNode"]:
        """Get all descendant nodes (recursive)"""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants
    
    def find_by_id(self, node_id: str) -> Optional["HierarchyNode"]:
        """Find node by ID (recursive search)"""
        if self.id == node_id:
            return self
        for child in self.children:
            result = child.find_by_id(node_id)
            if result:
                return result
        return None
    
    def count_descendants(self) -> int:
        """Count all descendants"""
        return len(self.children) + sum(child.count_descendants() for child in self.children)
    
    def to_dict(self, include_children: bool = True) -> Dict:
        """
        Convert to dictionary for serialization
        
        Args:
            include_children: Whether to include children in output
            
        Returns:
            Dictionary representation
        """
        result = {
            "id": self.id,
            "level": self.level,
            "level_name": self.level_name,
            "title": self.title,
            "section_number": self.section_number,
            "content_text": self.content_text,
            "metadata": self.metadata.model_dump(),
            "parent_id": self.parent_id,
            "child_count": len(self.children)
        }
        
        if include_children:
            result["children"] = [child.to_dict(include_children=True) for child in self.children]
        
        return result


class HierarchyTree(BaseModel):
    """Complete hierarchy tree extracted from a document"""
    tree_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique tree identifier")
    document_name: str = Field(..., description="Source document name")
    document_hash: str = Field(..., description="Hash of source document")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Extraction timestamp")
    
    # Tree structure
    root_nodes: List[HierarchyNode] = Field(default_factory=list, description="Top-level nodes")
    
    # Metadata
    rule_pack_id: Optional[str] = Field(None, description="ID of rule pack used for extraction")
    max_depth: int = Field(..., description="Maximum depth of tree", ge=1)
    total_nodes: int = Field(default=0, description="Total number of nodes in tree")
    
    # Quality metrics
    avg_confidence: float = Field(default=0.0, description="Average confidence across all nodes")
    extraction_quality: Optional[float] = Field(None, description="Overall extraction quality score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tree_id": "tree-456",
                "document_name": "ts_103989v040200p.pdf",
                "document_hash": "abc123def456",
                "extracted_at": "2026-06-11T10:30:00",
                "root_nodes": [],
                "rule_pack_id": "pack-789",
                "max_depth": 4,
                "total_nodes": 45,
                "avg_confidence": 0.82,
                "extraction_quality": 0.75
            }
        }
    
    def add_root_node(self, node: HierarchyNode):
        """Add a root-level node"""
        node.parent_id = None
        self.root_nodes.append(node)
        self._recalculate_stats()
    
    def find_nodes_by_level(self, level: int) -> List[HierarchyNode]:
        """
        Find all nodes at a specific level
        
        Args:
            level: Hierarchy level to search for
            
        Returns:
            List of nodes at that level
        """
        nodes = []
        
        def search_level(current_nodes: List[HierarchyNode]):
            for node in current_nodes:
                if node.level == level:
                    nodes.append(node)
                search_level(node.children)
        
        search_level(self.root_nodes)
        return nodes
    
    def find_node_by_id(self, node_id: str) -> Optional[HierarchyNode]:
        """
        Find node by ID
        
        Args:
            node_id: Node identifier
            
        Returns:
            Node if found, None otherwise
        """
        for root in self.root_nodes:
            result = root.find_by_id(node_id)
            if result:
                return result
        return None
    
    def get_all_nodes(self) -> List[HierarchyNode]:
        """Get all nodes in tree (flat list)"""
        all_nodes = []
        for root in self.root_nodes:
            all_nodes.append(root)
            all_nodes.extend(root.get_all_descendants())
        return all_nodes
    
    def _recalculate_stats(self):
        """Recalculate tree statistics"""
        all_nodes = self.get_all_nodes()
        self.total_nodes = len(all_nodes)
        
        if all_nodes:
            confidences = [node.metadata.confidence for node in all_nodes]
            self.avg_confidence = round(sum(confidences) / len(confidences), 3)
            
            # Calculate max depth
            depths = [node.level for node in all_nodes]
            self.max_depth = max(depths) if depths else 1
    
    def to_dict(self, include_all_nodes: bool = True) -> Dict:
        """
        Convert tree to dictionary
        
        Args:
            include_all_nodes: Whether to include full tree structure
            
        Returns:
            Dictionary representation
        """
        result = {
            "tree_id": self.tree_id,
            "document_name": self.document_name,
            "document_hash": self.document_hash,
            "extracted_at": self.extracted_at.isoformat(),
            "rule_pack_id": self.rule_pack_id,
            "max_depth": self.max_depth,
            "total_nodes": self.total_nodes,
            "avg_confidence": self.avg_confidence,
            "extraction_quality": self.extraction_quality
        }
        
        if include_all_nodes:
            result["root_nodes"] = [node.to_dict() for node in self.root_nodes]
        else:
            result["root_node_count"] = len(self.root_nodes)
        
        return result
    
    def get_statistics(self) -> Dict:
        """Get detailed statistics about the tree"""
        all_nodes = self.get_all_nodes()
        
        # Count nodes by level
        nodes_by_level = {}
        for node in all_nodes:
            level = node.level
            nodes_by_level[level] = nodes_by_level.get(level, 0) + 1
        
        # Calculate confidence distribution
        confidences = [node.metadata.confidence for node in all_nodes]
        high_conf = sum(1 for c in confidences if c >= 0.8)
        med_conf = sum(1 for c in confidences if 0.6 <= c < 0.8)
        low_conf = sum(1 for c in confidences if c < 0.6)
        
        return {
            "total_nodes": self.total_nodes,
            "max_depth": self.max_depth,
            "nodes_by_level": nodes_by_level,
            "avg_confidence": self.avg_confidence,
            "confidence_distribution": {
                "high": high_conf,  # >= 0.8
                "medium": med_conf,  # 0.6-0.8
                "low": low_conf     # < 0.6
            },
            "extraction_quality": self.extraction_quality
        }
    
    def validate(self) -> Dict:
        """
        Validate tree structure and return validation report
        
        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        
        all_nodes = self.get_all_nodes()
        
        # Check if tree is empty
        if not all_nodes:
            issues.append("Tree is empty (no nodes)")
        
        # Check if all nodes have required fields
        for node in all_nodes:
            if not node.title:
                issues.append(f"Node {node.id} missing title")
            if node.level < 1:
                issues.append(f"Node {node.id} has invalid level {node.level}")
            if node.metadata.confidence < 0 or node.metadata.confidence > 1:
                issues.append(f"Node {node.id} has invalid confidence {node.metadata.confidence}")
        
        # Check hierarchy consistency
        for node in all_nodes:
            for child in node.children:
                if child.level != node.level + 1:
                    warnings.append(
                        f"Node {child.id} (level {child.level}) is child of "
                        f"node {node.id} (level {node.level}) - expected level {node.level + 1}"
                    )
        
        # Check confidence levels
        low_conf_nodes = [n for n in all_nodes if n.metadata.confidence < 0.5]
        if low_conf_nodes:
            warnings.append(f"{len(low_conf_nodes)} nodes have confidence < 0.5")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "node_count": len(all_nodes),
            "validation_timestamp": datetime.now().isoformat()
        }


# Update forward references for self-referential models
HierarchyNode.model_rebuild()
