"""
Module Impact Analyzer - Identifies source code modules/functions 
that may require updates based on specification version changes.

Module Purpose:
- Map specification sections to source code modules and functions
- Analyze impact of version changes on codebase
- Generate impact reports with severity and update types
- Track breaking changes and affected APIs
- Estimate effort for required updates

Integration Points:
- SpecParserService: Detect version changes and trigger analysis
- ModuleReference: Links spec clauses to code locations
- ImpactAnalysis: Contains change impact details
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
from datetime import datetime
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ImpactSeverity(str, Enum):
    """Impact severity level"""
    CRITICAL = "critical"      # Breaking change affects API contract
    HIGH = "high"              # Affects core functionality
    MEDIUM = "medium"          # Affects implementation details
    LOW = "low"                # Documentation/comments update


class UpdateType(str, Enum):
    """Type of update required"""
    API_SIGNATURE = "api_signature"      # Function signature changed
    BEHAVIOR_CHANGE = "behavior_change"  # Implementation changed
    NEW_FEATURE = "new_feature"          # New endpoint/function needed
    DEPRECATION = "deprecation"          # Function deprecated
    DATA_MODEL = "data_model"            # Data structure changed
    VALIDATION = "validation"            # Validation rules changed
    ERROR_HANDLING = "error_handling"    # Error codes/responses changed


@dataclass
class ModuleReference:
    """Reference to a source code module/function"""
    module_path: str              # e.g., "app/services/policy_service.py"
    function_name: str            # e.g., "create_policy"
    spec_version: str             # Version this was implemented for
    spec_clause: str              # Section/clause reference (e.g., "5.2.4.3")
    implementation_type: str      # "endpoint", "service", "model", "validator"
    
    def __hash__(self):
        return hash((self.module_path, self.function_name, self.spec_clause))


@dataclass
class SpecDependency:
    """Maps spec sections to code modules"""
    spec_type: str                # "TS_103987", "TS_103988", etc.
    spec_section: str             # "5.2.4.3", "6.2.2", etc.
    section_title: str            # "Create policy"
    module_references: List[ModuleReference] = field(default_factory=list)
    
    def add_reference(self, ref: ModuleReference) -> None:
        """Add a module reference to this spec section"""
        if ref not in self.module_references:
            self.module_references.append(ref)
    
    def get_affected_modules(self) -> Set[str]:
        """Get all unique module paths"""
        return {ref.module_path for ref in self.module_references}


@dataclass
class ImpactAnalysis:
    """Analysis result for a version change"""
    spec_type: str
    from_version: str
    to_version: str
    change_type: str              # "major", "minor", "patch"
    breaking_changes: List[Tuple[str, str]] = field(default_factory=list)  # (section, change)
    affected_modules: List[str] = field(default_factory=list)
    affected_functions: Dict[str, List[str]] = field(default_factory=dict)  # module -> [functions]
    required_updates: Dict[str, UpdateType] = field(default_factory=dict)   # function -> update_type
    severity_levels: Dict[str, ImpactSeverity] = field(default_factory=dict)  # function -> severity
    affected_apis: List[str] = field(default_factory=list)
    estimated_effort: int = 0     # Story points estimate
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "spec": self.spec_type,
            "version_change": f"{self.from_version} → {self.to_version}",
            "change_type": self.change_type,
            "is_breaking": self.change_type == "major",
            "affected_modules": self.affected_modules,
            "affected_functions": self.affected_functions,
            "required_updates": {k: v.value for k, v in self.required_updates.items()},
            "severity_levels": {k: v.value for k, v in self.severity_levels.items()},
            "affected_apis": self.affected_apis,
            "estimated_effort": self.estimated_effort,
            "timestamp": self.timestamp.isoformat()
        }


class ModuleImpactAnalyzer:
    """Analyzes impact of spec changes on source code"""
    
    def __init__(self, source_root: Optional[Path] = None):
        """
        Initialize impact analyzer.
        
        Args:
            source_root: Root of source code directory (default: ./app)
        """
        self.source_root = source_root or Path("./app")
        self.spec_dependencies: Dict[str, SpecDependency] = {}
        self.module_cache: Dict[str, str] = {}  # Cache for module content
        self._initialize_spec_mappings()
    
    def _initialize_spec_mappings(self) -> None:
        """
        Initialize spec section to code module mappings.
        
        TODO: Populate with actual mappings from codebase analysis:
        - Extract A1 service endpoints from OpenAPI definitions
        - Map to FastAPI routes
        - Link to data models and validators
        - Track API versions in URIs
        """
        # Placeholder mappings based on TS 103987 structure
        self.spec_dependencies = {
            "TS_103987:4.2": SpecDependency(
                spec_type="TS_103987",
                spec_section="4.2",
                section_title="Compatibility of A1 versions",
                module_references=[
                    ModuleReference(
                        module_path="app/services/semantic_version_tracker.py",
                        function_name="SemanticVersionTracker.register_document",
                        spec_version="1.2",
                        spec_clause="4.2",
                        implementation_type="service"
                    ),
                ]
            ),
            "TS_103987:6.2": SpecDependency(
                spec_type="TS_103987",
                spec_section="6.2",
                section_title="A1-P (policy management)",
                module_references=[
                    ModuleReference(
                        module_path="app/api/a1_policy.py",
                        function_name="get_policy",
                        spec_version="1.2",
                        spec_clause="6.2.1",
                        implementation_type="endpoint"
                    ),
                    ModuleReference(
                        module_path="app/api/a1_policy.py",
                        function_name="put_policy",
                        spec_version="1.2",
                        spec_clause="6.2.2",
                        implementation_type="endpoint"
                    ),
                    ModuleReference(
                        module_path="app/models/policy_model.py",
                        function_name="PolicyObject",
                        spec_version="1.2",
                        spec_clause="6.2.3",
                        implementation_type="model"
                    ),
                ]
            ),
            "TS_103987:6.3": SpecDependency(
                spec_type="TS_103987",
                spec_section="6.3",
                section_title="A1-EI (enrichment information)",
                module_references=[
                    ModuleReference(
                        module_path="app/api/a1_enrichment.py",
                        function_name="get_ei_job",
                        spec_version="1.2",
                        spec_clause="6.3.1",
                        implementation_type="endpoint"
                    ),
                    ModuleReference(
                        module_path="app/models/enrichment_model.py",
                        function_name="EiJobObject",
                        spec_version="1.2",
                        spec_clause="6.3.3",
                        implementation_type="model"
                    ),
                ]
            ),
        }
    
    def add_spec_dependency(self, spec_key: str, dependency: SpecDependency) -> None:
        """
        Register a spec section dependency mapping.
        
        Args:
            spec_key: Key in format "SPEC_TYPE:SECTION" (e.g., "TS_103987:6.2")
            dependency: SpecDependency object with module references
        """
        self.spec_dependencies[spec_key] = dependency
    
    def analyze_impact(
        self, spec_type: str, from_version: str, to_version: str, change_type: str
    ) -> ImpactAnalysis:
        """
        Analyze impact of a spec version change.
        
        Args:
            spec_type: e.g., "TS_103987"
            from_version: e.g., "4.2.0"
            to_version: e.g., "4.3.0"
            change_type: "major", "minor", or "patch"
            
        Returns:
            ImpactAnalysis with affected modules and functions
        """
        analysis = ImpactAnalysis(
            spec_type=spec_type,
            from_version=from_version,
            to_version=to_version,
            change_type=change_type
        )
        
        # Find all spec sections for this spec type
        relevant_sections = [
            (key, dep) for key, dep in self.spec_dependencies.items()
            if dep.spec_type == spec_type
        ]
        
        # For breaking changes (major version), flag all modules as needing review
        if change_type == "major":
            for key, dep in relevant_sections:
                for module_ref in dep.module_references:
                    if module_ref.module_path not in analysis.affected_modules:
                        analysis.affected_modules.append(module_ref.module_path)
                    
                    if module_ref.module_path not in analysis.affected_functions:
                        analysis.affected_functions[module_ref.module_path] = []
                    
                    analysis.affected_functions[module_ref.module_path].append(
                        module_ref.function_name
                    )
                    
                    # Set update requirements
                    analysis.required_updates[module_ref.function_name] = UpdateType.BEHAVIOR_CHANGE
                    analysis.severity_levels[module_ref.function_name] = ImpactSeverity.CRITICAL
                    analysis.affected_apis.append(
                        f"{module_ref.module_path}:{module_ref.function_name}"
                    )
        
        # For minor changes, check specific sections that changed
        elif change_type == "minor":
            for key, dep in relevant_sections:
                for module_ref in dep.module_references:
                    analysis.affected_modules.append(module_ref.module_path)
                    analysis.required_updates[module_ref.function_name] = UpdateType.NEW_FEATURE
                    analysis.severity_levels[module_ref.function_name] = ImpactSeverity.MEDIUM
        
        # Estimate effort (simplified: major changes need more effort)
        analysis.estimated_effort = (
            len(analysis.affected_modules) * 3 if change_type == "major" else 1
        )
        
        return analysis
    
    def find_module_references(self, pattern: str) -> List[ModuleReference]:
        """
        Find module references matching a pattern.
        
        Args:
            pattern: Regex pattern to match against function names or module paths
            
        Returns:
            List of matching ModuleReference objects
        """
        results = []
        for dep in self.spec_dependencies.values():
            for ref in dep.module_references:
                if re.search(pattern, ref.function_name, re.IGNORECASE) or \
                   re.search(pattern, ref.module_path, re.IGNORECASE):
                    results.append(ref)
        return results
    
    def get_affected_modules_for_spec_section(self, spec_type: str, section: str) -> List[str]:
        """
        Get modules affected by a specific spec section.
        
        Args:
            spec_type: e.g., "TS_103987"
            section: e.g., "6.2"
            
        Returns:
            List of module paths
        """
        key = f"{spec_type}:{section}"
        if key in self.spec_dependencies:
            return list(self.spec_dependencies[key].get_affected_modules())
        return []
    
    def generate_impact_report(self, analysis: ImpactAnalysis) -> str:
        """
        Generate human-readable impact report.
        
        Args:
            analysis: ImpactAnalysis object
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append(f"MODULE IMPACT ANALYSIS: {analysis.spec_type}")
        report.append(f"Version Change: {analysis.from_version} → {analysis.to_version}")
        report.append(f"Change Type: {analysis.change_type.upper()}")
        report.append("=" * 80)
        report.append("")
        
        if analysis.change_type == "major":
            report.append("⚠ WARNING: BREAKING CHANGE DETECTED")
            report.append("")
        
        report.append(f"Affected Modules ({len(analysis.affected_modules)}):")
        for module in sorted(analysis.affected_modules):
            functions = analysis.affected_functions.get(module, [])
            report.append(f"  • {module}")
            for func in functions:
                severity = analysis.severity_levels.get(func, ImpactSeverity.LOW).value
                update_type = analysis.required_updates.get(func, UpdateType.BEHAVIOR_CHANGE).value
                report.append(f"    - {func} [{severity}] ({update_type})")
        
        report.append("")
        report.append(f"Estimated Effort: {analysis.estimated_effort} story points")
        report.append("")
        
        if analysis.affected_apis:
            report.append("Affected APIs:")
            for api in analysis.affected_apis:
                report.append(f"  • {api}")
        
        report.append("")
        return "\n".join(report)
