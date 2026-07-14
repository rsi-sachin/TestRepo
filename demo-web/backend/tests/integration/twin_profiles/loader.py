"""
Twin Profile Loader and Validator

Loads digital twin profiles (e.g., a1_minimal_twin_v1.json) and validates completeness
for test execution. Used by test harnesses to select simulators and set configuration.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class TwinProfileLoader:
    """Load and validate digital twin profiles for test execution."""
    
    _PROFILE_DIR = Path(__file__).parent
    
    @classmethod
    def load_profile(cls, profile_id: str) -> Dict[str, Any]:
        """
        Load a twin profile by ID.
        
        Args:
            profile_id: Profile name, e.g., "a1_minimal_twin_v1"
            
        Returns:
            Parsed profile configuration
            
        Raises:
            FileNotFoundError: If profile file not found
            json.JSONDecodeError: If profile JSON is invalid
        """
        profile_path = cls._PROFILE_DIR / f"{profile_id}.json"
        
        if not profile_path.exists():
            raise FileNotFoundError(f"Twin profile not found: {profile_path}")
        
        with open(profile_path, "r") as f:
            profile = json.load(f)
        
        logger.info(f"Loaded twin profile: {profile_id}")
        return profile
    
    @classmethod
    def validate_profile(cls, profile: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate profile completeness and structure.
        
        Args:
            profile: Parsed profile dictionary
            
        Returns:
            (is_valid, error_list) tuple
        """
        errors = []
        
        # Mandatory fields
        mandatory_fields = ["profile_id", "profile_version", "components", "conformance_scope"]
        for field in mandatory_fields:
            if field not in profile:
                errors.append(f"Missing mandatory field: {field}")
        
        # Validate components
        if "components" in profile:
            component_ids = set()
            for comp in profile["components"]:
                if "component_id" not in comp:
                    errors.append("Component missing component_id")
                elif comp["component_id"] in component_ids:
                    errors.append(f"Duplicate component_id: {comp['component_id']}")
                else:
                    component_ids.add(comp["component_id"])
                
                if "operation_mode" not in comp:
                    errors.append(f"Component {comp.get('component_id')} missing operation_mode")
                elif comp["operation_mode"] not in ("production", "simulated"):
                    errors.append(f"Invalid operation_mode for {comp.get('component_id')}: {comp['operation_mode']}")
        
        # Validate conformance scope is non-empty
        if "conformance_scope" in profile and not profile["conformance_scope"]:
            errors.append("conformance_scope must not be empty")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info(f"Profile validation passed: {profile.get('profile_id')}")
        else:
            logger.error(f"Profile validation failed: {profile.get('profile_id')}")
            for error in errors:
                logger.error(f"  - {error}")
        
        return is_valid, errors
    
    @classmethod
    def get_components_for_test_family(
        cls, 
        profile: Dict[str, Any], 
        test_family: str
    ) -> List[Dict[str, Any]]:
        """
        Get required components for a test family.
        
        Args:
            profile: Parsed profile dictionary
            test_family: Test family name (e.g., "conformance_a1p")
            
        Returns:
            List of required component configurations
        """
        activation_rules = profile.get("component_activation_rules", [])
        
        # Find matching rule
        for rule in activation_rules:
            if rule.get("test_family") == test_family:
                required_component_ids = rule.get("required_components", [])
                components = profile.get("components", [])
                
                # Return component definitions for required IDs
                return [
                    c for c in components 
                    if c.get("component_id") in required_component_ids
                ]
        
        logger.warning(f"No activation rule found for test_family: {test_family}")
        return []
    
    @classmethod
    def get_simulator_config(
        cls, 
        profile: Dict[str, Any], 
        component_id: str
    ) -> Dict[str, Any]:
        """
        Get simulator configuration for a component.
        
        Args:
            profile: Parsed profile dictionary
            component_id: Component identifier
            
        Returns:
            Simulator configuration dictionary
        """
        components = profile.get("components", [])
        
        for comp in components:
            if comp.get("component_id") == component_id:
                return comp.get("config", {})
        
        raise ValueError(f"Component not found: {component_id}")
    
    @classmethod
    def list_available_profiles(cls) -> List[str]:
        """
        List all available twin profiles.
        
        Returns:
            List of profile names (without .json extension)
        """
        json_files = cls._PROFILE_DIR.glob("*.json")
        profiles = [f.stem for f in json_files]
        logger.info(f"Available profiles: {profiles}")
        return profiles


class TwinProfileContextManager:
    """Context manager for test execution with a twin profile."""
    
    def __init__(self, profile_id: str):
        """
        Initialize context with a twin profile.
        
        Args:
            profile_id: Twin profile identifier
        """
        self.profile_id = profile_id
        self.profile = None
        self.loaded_simulators = {}
    
    def __enter__(self) -> Dict[str, Any]:
        """Load and validate profile on context entry."""
        self.profile = TwinProfileLoader.load_profile(self.profile_id)
        is_valid, errors = TwinProfileLoader.validate_profile(self.profile)
        
        if not is_valid:
            raise ValueError(f"Profile validation failed: {errors}")
        
        logger.info(f"Twin profile context activated: {self.profile_id}")
        return self.profile
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up simulators on context exit."""
        for sim_id, simulator in self.loaded_simulators.items():
            if hasattr(simulator, "reset"):
                simulator.reset()
                logger.info(f"Reset simulator: {sim_id}")
        
        self.loaded_simulators.clear()
        logger.info(f"Twin profile context closed: {self.profile_id}")
    
    def get_simulator_instance(self, component_id: str):
        """
        Get or create simulator instance for a component.
        
        Args:
            component_id: Component identifier
            
        Returns:
            Simulator instance
        """
        if component_id in self.loaded_simulators:
            return self.loaded_simulators[component_id]
        
        if not self.profile:
            raise RuntimeError("Profile not loaded; use context manager")
        
        # Find component definition
        components = self.profile.get("components", [])
        component_def = next(
            (c for c in components if c.get("component_id") == component_id),
            None
        )
        
        if not component_def:
            raise ValueError(f"Component not found: {component_id}")
        
        if component_def.get("operation_mode") != "simulated":
            raise ValueError(f"Component is not simulated: {component_id}")
        
        # Load and instantiate simulator
        module_path = component_def.get("module_path")
        class_name = component_def.get("class")
        config = component_def.get("config", {})
        
        if not module_path or not class_name:
            raise ValueError(f"Simulator definition incomplete for {component_id}")
        
        try:
            # Import module dynamically
            import importlib
            module = importlib.import_module(module_path.replace("/", "."))
            simulator_class = getattr(module, class_name)
            
            # Instantiate with config
            simulator = simulator_class(config)
            self.loaded_simulators[component_id] = simulator
            
            logger.info(f"Loaded simulator instance: {component_id} ({class_name})")
            return simulator
        
        except (ImportError, AttributeError) as e:
            raise RuntimeError(f"Failed to load simulator {component_id}: {e}")
