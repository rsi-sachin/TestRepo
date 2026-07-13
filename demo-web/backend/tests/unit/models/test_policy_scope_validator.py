"""
Unit tests for PolicyScopeValidator
Tests all policy/scope combinations from TS 103 988 Section 7 tables
"""

import pytest
from app.models.validators.a1_policy_validator import (
    PolicyScopeValidator,
    ScopeCardinality,
    validate_policy_scope,
    validate_policy_scope_with_error,
)


class TestQoSTargetCombinations:
    """Test QoSTarget (7.2.1) scope combinations"""

    def test_qos_ue_required_qos_required(self):
        """Test: ueId=1, groupId=0..1, sliceId=0, qosId=1, cellId=0..1"""
        # Valid: ueId and qosId present, no sliceId
        scopes = {'ueId': True, 'qosId': True, 'sliceId': False, 'groupId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes, 'qosObjectives'
        )
        assert is_valid, error

    def test_qos_ue_with_optional_group(self):
        """Test: ueId=1, groupId=0..1, sliceId=0, qosId=1, cellId=0..1"""
        # Valid: ueId, qosId, and optional groupId
        scopes = {'ueId': True, 'groupId': True, 'sliceId': False, 'qosId': True, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes, 'qosObjectives'
        )
        assert is_valid, error

    def test_qos_ue_with_optional_cell(self):
        """Test: ueId=1, groupId=0..1, sliceId=0, qosId=1, cellId=0..1"""
        # Valid: ueId, qosId, and optional cellId
        scopes = {'ueId': True, 'qosId': True, 'cellId': True, 'sliceId': False, 'groupId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes, 'qosObjectives'
        )
        assert is_valid, error

    def test_qos_ue_with_slice(self):
        """Test: ueId=1, groupId=0, sliceId=0..1, qosId=1, cellId=0..1"""
        # Valid: ueId, qosId, and optional sliceId
        scopes = {'ueId': True, 'qosId': True, 'sliceId': True, 'groupId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes, 'qosObjectives'
        )
        assert is_valid, error

    def test_qos_group_required(self):
        """Test: ueId=0, groupId=1, sliceId=0, qosId=1, cellId=0..1"""
        # Valid: groupId and qosId required, no ueId or sliceId
        scopes = {'groupId': True, 'qosId': True, 'ueId': False, 'sliceId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes, 'qosObjectives'
        )
        assert is_valid, error

    def test_qos_slice_required(self):
        """Test: ueId=0, groupId=0, sliceId=1, qosId=1, cellId=0..1"""
        # Valid: sliceId and qosId required
        scopes = {'sliceId': True, 'qosId': True, 'ueId': False, 'groupId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes, 'qosObjectives'
        )
        assert is_valid, error

    def test_qos_qos_only(self):
        """Test: ueId=0, groupId=0, sliceId=0, qosId=1, cellId=0..1"""
        # Valid: qosId required, all others absent
        scopes = {'qosId': True, 'ueId': False, 'groupId': False, 'sliceId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes, 'qosObjectives'
        )
        assert is_valid, error

    def test_qos_invalid_missing_qos_id(self):
        """Invalid: Missing required qosId"""
        scopes = {'ueId': True, 'qosId': False, 'sliceId': False, 'groupId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes, 'qosObjectives'
        )
        assert not is_valid
        assert 'not allowed' in error.lower() or 'invalid' in error.lower()

    def test_qos_invalid_ue_and_group(self):
        """Invalid: Cannot have ueId, groupId, AND sliceId together for QoS"""
        # Per table 7.2.1.2.2-1: combinations either have ueId OR groupId OR sliceId, not combinations
        # This has all three which is not allowed
        scopes = {'ueId': True, 'groupId': True, 'sliceId': True, 'qosId': True, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes, 'qosObjectives'
        )
        assert not is_valid, "Should reject ueId + groupId + sliceId combination"

    def test_qos_invalid_slice_and_ue_group_combo(self):
        """Invalid: Wrong combination pattern"""
        scopes = {'ueId': True, 'sliceId': True, 'groupId': True, 'qosId': True, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes, 'qosObjectives'
        )
        assert not is_valid


class TestQoETargetCombinations:
    """Test QoETarget (7.2.2) scope combinations"""

    def test_qoe_ue_with_slice(self):
        """Test: ueId=1, groupId=0, sliceId=1, qosId=0..1, cellId=0..1"""
        scopes = {'ueId': True, 'sliceId': True, 'groupId': False, 'qosId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoETarget', scopes, 'qoeObjectives'
        )
        assert is_valid, error

    def test_qoe_ue_with_qos(self):
        """Test: ueId=1, groupId=0, sliceId=0, qosId=1, cellId=0..1"""
        scopes = {'ueId': True, 'qosId': True, 'sliceId': False, 'groupId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoETarget', scopes, 'qoeObjectives'
        )
        assert is_valid, error

    def test_qoe_slice_only(self):
        """Test: ueId=0, groupId=0, sliceId=1, qosId=0..1, cellId=0..1"""
        scopes = {'sliceId': True, 'ueId': False, 'groupId': False, 'qosId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoETarget', scopes, 'qoeObjectives'
        )
        assert is_valid, error

    def test_qoe_qos_only(self):
        """Test: ueId=0, groupId=0, sliceId=0, qosId=1, cellId=0..1"""
        scopes = {'qosId': True, 'ueId': False, 'groupId': False, 'sliceId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoETarget', scopes, 'qoeObjectives'
        )
        assert is_valid, error

    def test_qoe_invalid_group_not_allowed(self):
        """Invalid: groupId not allowed with QoE"""
        scopes = {'groupId': True, 'ueId': False, 'sliceId': True, 'qosId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoETarget', scopes, 'qoeObjectives'
        )
        assert not is_valid


class TestTrafficSteeringPreferenceCombinations:
    """Test TrafficSteeringPreference (7.2.3) scope combinations"""

    def test_tsp_ue_required(self):
        """Test: ueId=1, groupId=0, sliceId=0..1, qosId=0..1, cellId=0..1"""
        scopes = {'ueId': True, 'groupId': False, 'sliceId': False, 'qosId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'TrafficSteeringPreference', scopes, 'tspResources'
        )
        assert is_valid, error

    def test_tsp_slice_required(self):
        """Test: ueId=0, groupId=0, sliceId=1, qosId=0..1, cellId=0..1"""
        scopes = {'sliceId': True, 'ueId': False, 'groupId': False, 'qosId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'TrafficSteeringPreference', scopes, 'tspResources'
        )
        assert is_valid, error

    def test_tsp_invalid_group_not_allowed(self):
        """Invalid: groupId not allowed with TSP"""
        scopes = {'groupId': True, 'ueId': False, 'sliceId': False, 'qosId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'TrafficSteeringPreference', scopes, 'tspResources'
        )
        assert not is_valid


class TestUELevelTargetCombinations:
    """Test UELevelTarget (7.2.6) scope combinations"""

    def test_ue_level_ue_required(self):
        """Test: ueId=1, groupId=0, sliceId=0..1, qosId=0, cellId=0..1"""
        scopes = {'ueId': True, 'groupId': False, 'sliceId': False, 'qosId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'UELevelTarget', scopes, 'ueLevelObjectives'
        )
        assert is_valid, error

    def test_ue_level_with_optional_slice(self):
        """Test: ueId=1, groupId=0, sliceId=0..1, qosId=0, cellId=0..1"""
        scopes = {'ueId': True, 'sliceId': True, 'groupId': False, 'qosId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'UELevelTarget', scopes, 'ueLevelObjectives'
        )
        assert is_valid, error

    def test_ue_level_invalid_qos_not_allowed(self):
        """Invalid: qosId not allowed with UE level"""
        scopes = {'ueId': True, 'qosId': True, 'groupId': False, 'sliceId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'UELevelTarget', scopes, 'ueLevelObjectives'
        )
        assert not is_valid


class TestSliceSLATargetCombinations:
    """Test SliceSLATarget (7.2.7) scope combinations"""

    def test_sla_slice_required(self):
        """Test: sliceId=1, cellId=0..1, all others=0"""
        scopes = {'sliceId': True, 'ueId': False, 'groupId': False, 'qosId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'SliceSLATarget', scopes, 'sliceSlaObjectives'
        )
        assert is_valid, error

    def test_sla_with_optional_cell(self):
        """Test: sliceId=1, cellId=0..1"""
        scopes = {'sliceId': True, 'cellId': True, 'ueId': False, 'groupId': False, 'qosId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'SliceSLATarget', scopes, 'sliceSlaObjectives'
        )
        assert is_valid, error

    def test_sla_invalid_missing_slice(self):
        """Invalid: Missing required sliceId"""
        scopes = {'sliceId': False, 'cellId': True, 'ueId': False, 'groupId': False, 'qosId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'SliceSLATarget', scopes, 'sliceSlaObjectives'
        )
        assert not is_valid

    def test_sla_invalid_ue_not_allowed(self):
        """Invalid: ueId not allowed with SLA"""
        scopes = {'sliceId': True, 'ueId': True, 'groupId': False, 'qosId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'SliceSLATarget', scopes, 'sliceSlaObjectives'
        )
        assert not is_valid


class TestLoadBalancingCombinations:
    """Test LoadBalancing (7.2.8) scope combinations"""

    def test_lb_cell_required(self):
        """Test: cellId=1, taiList=0..1, cellIdList=0..1, all others=0"""
        scopes = {'cellId': True, 'ueId': False, 'groupId': False, 'sliceId': False, 'qosId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'LoadBalancing', scopes, 'lbObjectives'
        )
        assert is_valid, error


class TestEnergySavingCombinations:
    """Test EnergySaving (7.2.9) scope combinations"""

    def test_es_with_cell(self):
        """Test: cellId=0..1, taiList=0..1, cellIdList=0..1, all others=0"""
        scopes = {'cellId': True, 'ueId': False, 'groupId': False, 'sliceId': False, 'qosId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'EnergySaving', scopes, 'esObjectives'
        )
        assert is_valid, error

    def test_es_optional_all_cells(self):
        """Test: All cell identifiers optional"""
        scopes = {'cellId': False, 'ueId': False, 'groupId': False, 'sliceId': False, 'qosId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'EnergySaving', scopes, 'esObjectives'
        )
        assert is_valid, error


class TestValidatorHelpers:
    """Test validator helper methods"""

    def test_get_policy_statement_type(self):
        """Test getting required statement type for policy"""
        assert PolicyScopeValidator.get_policy_statement_type('QoSTarget') == 'qosObjectives'
        assert PolicyScopeValidator.get_policy_statement_type('SliceSLATarget') == 'sliceSlaObjectives'
        assert PolicyScopeValidator.get_policy_statement_type('UnknownPolicy') is None

    def test_get_allowed_resources(self):
        """Test getting allowed resources for policy"""
        qos_resources = PolicyScopeValidator.get_allowed_resources('QoSTarget')
        assert 'tspResources' in qos_resources

    def test_list_allowed_scope_combinations(self):
        """Test listing all allowed combinations for policy"""
        combos = PolicyScopeValidator.list_allowed_scope_combinations('QoSTarget')
        assert len(combos) == 5  # QoS has 5 allowed combinations
        assert all(isinstance(combo, dict) for combo in combos)

    def test_unknown_policy_type(self):
        """Test validation with unknown policy type"""
        scopes = {'ueId': True, 'qosId': True}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'UnknownPolicyType', scopes
        )
        assert not is_valid
        assert 'Unknown policy type' in error

    def test_wrong_statement_type(self):
        """Test validation with wrong statement type for policy"""
        scopes = {'ueId': True, 'qosId': True}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes, 'wrongStatementType'
        )
        assert not is_valid
        assert 'qosObjectives' in error


class TestConvenienceFunctions:
    """Test convenience validation functions"""

    def test_validate_policy_scope_simple(self):
        """Test simple boolean validation function"""
        scopes = {'qosId': True, 'ueId': False, 'groupId': False, 'sliceId': False, 'cellId': False}
        result = validate_policy_scope('QoSTarget', scopes)
        assert result is True

    def test_validate_policy_scope_with_error_valid(self):
        """Test validation with error message function (valid case)"""
        scopes = {'qosId': True, 'ueId': False, 'groupId': False, 'sliceId': False, 'cellId': False}
        is_valid, error = validate_policy_scope_with_error('QoSTarget', scopes)
        assert is_valid
        assert error is None

    def test_validate_policy_scope_with_error_invalid(self):
        """Test validation with error message function (invalid case)"""
        scopes = {'groupId': True, 'ueId': False, 'sliceId': True, 'qosId': False, 'cellId': False}
        is_valid, error = validate_policy_scope_with_error('QoETarget', scopes)
        assert not is_valid
        assert error is not None


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_scopes(self):
        """Test with empty scope dict"""
        scopes = {}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes
        )
        # Empty dict might not match any combination
        assert not is_valid

    def test_all_scopes_false(self):
        """Test with all scopes set to false"""
        scopes = {'ueId': False, 'groupId': False, 'sliceId': False, 'qosId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes
        )
        # Only qosId-only combination should match
        assert not is_valid  # Because all are False

    def test_all_scopes_true(self):
        """Test with all scopes set to true (over-specified)"""
        scopes = {'ueId': True, 'groupId': True, 'sliceId': True, 'qosId': True, 'cellId': True}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes
        )
        # Should not match any combination (too many scopes)
        assert not is_valid

    def test_policy_with_resources(self):
        """Test validation includes resource type checking"""
        scopes = {'qosId': True, 'ueId': False, 'groupId': False, 'sliceId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes, 'qosObjectives', ['tspResources']
        )
        assert is_valid

    def test_policy_with_invalid_resources(self):
        """Test validation rejects invalid resources"""
        scopes = {'qosId': True, 'ueId': False, 'groupId': False, 'sliceId': False, 'cellId': False}
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget', scopes, 'qosObjectives', ['invalidResource']
        )
        assert not is_valid
        assert 'does not support' in error.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
