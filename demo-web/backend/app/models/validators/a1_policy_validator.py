"""
Policy Scope Combination Validator
Implements clause 6.4.1.2 allowed combinations per Section 7 policy type definitions
"""

from typing import Dict, List, Set, Optional, Tuple
from enum import Enum


class ScopeCardinality(str, Enum):
    """Cardinality notation from TS 103 988"""
    REQUIRED = "1"       # Must occur (exactly 1)
    OPTIONAL = "0..1"    # May occur (0 or 1)
    NOT_ALLOWED = "0"    # Must not occur


class PolicyScopeValidator:
    """
    Validates policy/scope identifier combinations per TS 103 988 Section 7
    
    Each policy type has specific allowed combinations of scope identifiers.
    Combinations are defined in tables 7.2.X.2.2-1 for each policy type.
    """

    # Define allowed scope combinations per policy type
    # Key: policy type name
    # Value: list of allowed scope combinations
    # Each combination specifies cardinality for: ueId, groupId, sliceId, qosId, cellId, taiList, cellIdList
    
    POLICY_COMBINATIONS = {
        # Policy Type 7.2.1: QoS Objectives
        'QoSTarget': {
            'statement_type': 'qosObjectives',
            'optional_resources': ['tspResources'],
            'allowed_scopes': [
                {
                    'ueId': ScopeCardinality.REQUIRED,
                    'groupId': ScopeCardinality.OPTIONAL,
                    'sliceId': ScopeCardinality.NOT_ALLOWED,
                    'qosId': ScopeCardinality.REQUIRED,
                    'cellId': ScopeCardinality.OPTIONAL,
                },
                {
                    'ueId': ScopeCardinality.REQUIRED,
                    'groupId': ScopeCardinality.NOT_ALLOWED,
                    'sliceId': ScopeCardinality.OPTIONAL,
                    'qosId': ScopeCardinality.REQUIRED,
                    'cellId': ScopeCardinality.OPTIONAL,
                },
                {
                    'ueId': ScopeCardinality.NOT_ALLOWED,
                    'groupId': ScopeCardinality.REQUIRED,
                    'sliceId': ScopeCardinality.NOT_ALLOWED,
                    'qosId': ScopeCardinality.REQUIRED,
                    'cellId': ScopeCardinality.OPTIONAL,
                },
                {
                    'ueId': ScopeCardinality.NOT_ALLOWED,
                    'groupId': ScopeCardinality.NOT_ALLOWED,
                    'sliceId': ScopeCardinality.REQUIRED,
                    'qosId': ScopeCardinality.REQUIRED,
                    'cellId': ScopeCardinality.OPTIONAL,
                },
                {
                    'ueId': ScopeCardinality.NOT_ALLOWED,
                    'groupId': ScopeCardinality.NOT_ALLOWED,
                    'sliceId': ScopeCardinality.NOT_ALLOWED,
                    'qosId': ScopeCardinality.REQUIRED,
                    'cellId': ScopeCardinality.OPTIONAL,
                },
            ]
        },
        
        # Policy Type 7.2.2: QoE Objectives
        'QoETarget': {
            'statement_type': 'qoeObjectives',
            'optional_resources': ['tspResources'],
            'allowed_scopes': [
                {
                    'ueId': ScopeCardinality.REQUIRED,
                    'groupId': ScopeCardinality.NOT_ALLOWED,
                    'sliceId': ScopeCardinality.REQUIRED,
                    'qosId': ScopeCardinality.OPTIONAL,
                    'cellId': ScopeCardinality.OPTIONAL,
                },
                {
                    'ueId': ScopeCardinality.REQUIRED,
                    'groupId': ScopeCardinality.NOT_ALLOWED,
                    'sliceId': ScopeCardinality.NOT_ALLOWED,
                    'qosId': ScopeCardinality.REQUIRED,
                    'cellId': ScopeCardinality.OPTIONAL,
                },
                {
                    'ueId': ScopeCardinality.NOT_ALLOWED,
                    'groupId': ScopeCardinality.NOT_ALLOWED,
                    'sliceId': ScopeCardinality.REQUIRED,
                    'qosId': ScopeCardinality.OPTIONAL,
                    'cellId': ScopeCardinality.OPTIONAL,
                },
                {
                    'ueId': ScopeCardinality.NOT_ALLOWED,
                    'groupId': ScopeCardinality.NOT_ALLOWED,
                    'sliceId': ScopeCardinality.NOT_ALLOWED,
                    'qosId': ScopeCardinality.REQUIRED,
                    'cellId': ScopeCardinality.OPTIONAL,
                },
            ]
        },
        
        # Policy Type 7.2.3: Traffic Steering Preferences
        'TrafficSteeringPreference': {
            'statement_type': 'tspResources',
            'optional_resources': [],
            'allowed_scopes': [
                {
                    'ueId': ScopeCardinality.REQUIRED,
                    'groupId': ScopeCardinality.NOT_ALLOWED,
                    'sliceId': ScopeCardinality.OPTIONAL,
                    'qosId': ScopeCardinality.OPTIONAL,
                    'cellId': ScopeCardinality.OPTIONAL,
                },
                {
                    'ueId': ScopeCardinality.NOT_ALLOWED,
                    'groupId': ScopeCardinality.NOT_ALLOWED,
                    'sliceId': ScopeCardinality.REQUIRED,
                    'qosId': ScopeCardinality.OPTIONAL,
                    'cellId': ScopeCardinality.OPTIONAL,
                },
            ]
        },
        
        # Policy Type 7.2.4: QoS Optimization with Resource Directive
        'QoSandTSP': {
            'statement_type': 'qosObjectives',
            'optional_resources': ['tspResources'],
            'allowed_scopes': [
                # Same as QoS + TSP combinations (combination of both)
            ]
        },
        
        # Policy Type 7.2.5: QoE Optimization with Resource Directive
        'QoEandTSP': {
            'statement_type': 'qoeObjectives',
            'optional_resources': ['tspResources'],
            'allowed_scopes': [
                # Same as QoE + TSP combinations (combination of both)
            ]
        },
        
        # Policy Type 7.2.6: UE Level Target
        'UELevelTarget': {
            'statement_type': 'ueLevelObjectives',
            'optional_resources': [],
            'allowed_scopes': [
                {
                    'ueId': ScopeCardinality.REQUIRED,
                    'groupId': ScopeCardinality.NOT_ALLOWED,
                    'sliceId': ScopeCardinality.OPTIONAL,
                    'qosId': ScopeCardinality.NOT_ALLOWED,
                    'cellId': ScopeCardinality.OPTIONAL,
                },
            ]
        },
        
        # Policy Type 7.2.7: Slice SLA Target
        'SliceSLATarget': {
            'statement_type': 'sliceSlaObjectives',
            'optional_resources': ['slaSlaResources'],
            'allowed_scopes': [
                {
                    'ueId': ScopeCardinality.NOT_ALLOWED,
                    'groupId': ScopeCardinality.NOT_ALLOWED,
                    'sliceId': ScopeCardinality.REQUIRED,
                    'qosId': ScopeCardinality.NOT_ALLOWED,
                    'cellId': ScopeCardinality.OPTIONAL,
                },
            ]
        },
        
        # Policy Type 7.2.8: Load Balancing
        'LoadBalancing': {
            'statement_type': 'lbObjectives',
            'optional_resources': ['lbResources'],
            'allowed_scopes': [
                {
                    'ueId': ScopeCardinality.NOT_ALLOWED,
                    'groupId': ScopeCardinality.NOT_ALLOWED,
                    'sliceId': ScopeCardinality.NOT_ALLOWED,
                    'qosId': ScopeCardinality.NOT_ALLOWED,
                    'cellId': ScopeCardinality.REQUIRED,
                    'taiList': ScopeCardinality.OPTIONAL,
                    'cellIdList': ScopeCardinality.OPTIONAL,
                },
            ]
        },
        
        # Policy Type 7.2.9: Energy Saving
        'EnergySaving': {
            'statement_type': 'esObjectives',
            'optional_resources': ['esResources'],
            'allowed_scopes': [
                {
                    'ueId': ScopeCardinality.NOT_ALLOWED,
                    'groupId': ScopeCardinality.NOT_ALLOWED,
                    'sliceId': ScopeCardinality.NOT_ALLOWED,
                    'qosId': ScopeCardinality.NOT_ALLOWED,
                    'cellId': ScopeCardinality.OPTIONAL,
                    'taiList': ScopeCardinality.OPTIONAL,
                    'cellIdList': ScopeCardinality.OPTIONAL,
                },
            ]
        },
    }

    @classmethod
    def validate_policy_scope_combination(
        cls,
        policy_type: str,
        scope_identifiers: Dict[str, bool],
        statement_type: Optional[str] = None,
        resource_types: Optional[List[str]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if a scope/statement/resource combination is allowed
        
        Args:
            policy_type: Policy type name (QoSTarget, SliceSLATarget, etc.)
            scope_identifiers: Dict of scope presence {scopeId: is_present}
            statement_type: Optional statement type to verify
            resource_types: Optional list of resource types used
        
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if combination is allowed, False otherwise
            - error_message: Detailed error if invalid, None if valid
        """
        
        # Check if policy type is known
        if policy_type not in cls.POLICY_COMBINATIONS:
            return False, f"Unknown policy type: {policy_type}"
        
        policy_def = cls.POLICY_COMBINATIONS[policy_type]
        
        # Verify statement type if provided
        if statement_type and statement_type != policy_def['statement_type']:
            return False, f"Policy type {policy_type} requires statement type '{policy_def['statement_type']}', got '{statement_type}'"
        
        # Verify resources if provided
        if resource_types:
            allowed_resources = {policy_def['statement_type']} | set(policy_def.get('optional_resources', []))
            invalid_resources = set(resource_types) - allowed_resources
            if invalid_resources:
                return False, f"Policy type {policy_type} does not support resources: {invalid_resources}"
        
        # Check if scope combination matches one of allowed combinations
        allowed_scopes = policy_def.get('allowed_scopes', [])
        
        if not allowed_scopes:
            return False, f"No scope combinations defined for policy type {policy_type}"
        
        # Try to match against one of the allowed combinations
        for combo in allowed_scopes:
            if cls._matches_combination(scope_identifiers, combo):
                return True, None
        
        # No match found
        return False, f"Scope combination not allowed for policy type {policy_type}. Provided scopes: {scope_identifiers}"

    @classmethod
    def _matches_combination(
        cls,
        provided_scopes: Dict[str, bool],
        allowed_combo: Dict[str, ScopeCardinality],
    ) -> bool:
        """
        Check if provided scopes match an allowed combination pattern
        
        Cardinality rules:
        - REQUIRED (1): Must be present
        - OPTIONAL (0..1): May or may not be present
        - NOT_ALLOWED (0): Must not be present
        """
        
        for scope_id, cardinality in allowed_combo.items():
            is_provided = provided_scopes.get(scope_id, False)
            
            if cardinality == ScopeCardinality.REQUIRED and not is_provided:
                return False  # Required but not provided
            elif cardinality == ScopeCardinality.NOT_ALLOWED and is_provided:
                return False  # Not allowed but provided
            # OPTIONAL matches either case
        
        # Also check that no unexpected scopes are provided
        for scope_id, is_provided in provided_scopes.items():
            if is_provided and scope_id not in allowed_combo:
                # Unknown scope provided
                return False
        
        return True

    @classmethod
    def get_policy_statement_type(cls, policy_type: str) -> Optional[str]:
        """Get the required statement type for a policy type"""
        policy_def = cls.POLICY_COMBINATIONS.get(policy_type)
        return policy_def.get('statement_type') if policy_def else None

    @classmethod
    def get_allowed_resources(cls, policy_type: str) -> List[str]:
        """Get allowed resource types for a policy type"""
        policy_def = cls.POLICY_COMBINATIONS.get(policy_type)
        return policy_def.get('optional_resources', []) if policy_def else []

    @classmethod
    def list_allowed_scope_combinations(cls, policy_type: str) -> List[Dict[str, str]]:
        """List all allowed scope combinations for a policy type"""
        policy_def = cls.POLICY_COMBINATIONS.get(policy_type)
        if not policy_def:
            return []
        
        combos = []
        for combo in policy_def.get('allowed_scopes', []):
            # Convert to readable format
            readable = {
                scope_id: cardinality.value
                for scope_id, cardinality in combo.items()
            }
            combos.append(readable)
        
        return combos


# Convenience functions for validation

def validate_policy_scope(
    policy_type: str,
    scopes_dict: Dict[str, bool],
    statement_type: Optional[str] = None,
) -> bool:
    """Simple validation that returns True/False"""
    is_valid, _ = PolicyScopeValidator.validate_policy_scope_combination(
        policy_type, scopes_dict, statement_type
    )
    return is_valid


def validate_policy_scope_with_error(
    policy_type: str,
    scopes_dict: Dict[str, bool],
    statement_type: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """Validation that returns detailed error message"""
    return PolicyScopeValidator.validate_policy_scope_combination(
        policy_type, scopes_dict, statement_type
    )
