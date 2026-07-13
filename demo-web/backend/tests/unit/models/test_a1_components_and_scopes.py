"""
Extended test suite for Phase 1 - Steps 4-6
Tests for statement components, scope identifiers, and policy workflows
"""

import pytest
from pydantic import ValidationError

from app.data.models.a1_statement_components import (
    RangeConstraint, MeasurementUnit, MeasurementUnitType, ConstraintSpecification,
    ComparisonOperator, PolicyStateType, QosObjective, QoeObjective,
    TrafficSteeringPreference, UeLevelObjective, SliceSlaObjective,
    LoadBalancingObjective, EnergySavingObjective, ResourceDirective,
    StatementComponentFactory
)
from app.data.models.a1_scope_identifiers import (
    PlmnId, UeIdentifier, GroupIdentifier, SliceIdentifier, QosClassIdentifier,
    CellIdentifier, GlobalGnbId, GuAmI, GuMmeI, TrackingAreaIdentifier,
    TaiList, ScopeIdentifierFactory
)
from app.models.validators.a1_policy_validator import PolicyScopeValidator


# ==================== STATEMENT COMPONENT TESTS ====================

class TestRangeConstraint:
    """Test RangeConstraint component"""

    def test_valid_range_constraint(self):
        """Test creating valid range constraint"""
        constraint = RangeConstraint(min_value=0, max_value=100, step_value=10)
        assert constraint.min_value == 0
        assert constraint.max_value == 100
        assert constraint.step_value == 10

    def test_range_constraint_no_step(self):
        """Test range constraint without step"""
        constraint = RangeConstraint(min_value=1, max_value=1000)
        assert constraint.step_value is None

    def test_range_constraint_validation_max_less_than_min(self):
        """Test that max_value must be >= min_value"""
        with pytest.raises(ValidationError):
            RangeConstraint(min_value=100, max_value=50)

    def test_is_valid_value_within_range(self):
        """Test value validation within range"""
        constraint = RangeConstraint(min_value=0, max_value=100)
        assert constraint.is_valid_value(50)
        assert constraint.is_valid_value(0)
        assert constraint.is_valid_value(100)

    def test_is_valid_value_outside_range(self):
        """Test value validation outside range"""
        constraint = RangeConstraint(min_value=0, max_value=100)
        assert not constraint.is_valid_value(-1)
        assert not constraint.is_valid_value(101)

    def test_is_valid_value_with_step(self):
        """Test value validation with step constraint"""
        constraint = RangeConstraint(min_value=0, max_value=100, step_value=10)
        assert constraint.is_valid_value(0)
        assert constraint.is_valid_value(10)
        assert constraint.is_valid_value(50)
        assert constraint.is_valid_value(100)
        # These don't align with step
        assert not constraint.is_valid_value(5)
        assert not constraint.is_valid_value(25)

    def test_range_constraint_only_min(self):
        """Test range constraint with only minimum"""
        constraint = RangeConstraint(min_value=0)
        assert constraint.is_valid_value(0)
        assert constraint.is_valid_value(1000000)

    def test_range_constraint_only_max(self):
        """Test range constraint with only maximum"""
        constraint = RangeConstraint(max_value=100)
        assert constraint.is_valid_value(0)
        assert constraint.is_valid_value(100)
        assert not constraint.is_valid_value(101)


class TestMeasurementUnit:
    """Test MeasurementUnit component"""

    def test_valid_measurement_unit(self):
        """Test creating measurement unit"""
        unit = MeasurementUnit(unit_type=MeasurementUnitType.MEGABYTES)
        assert unit.unit_type == MeasurementUnitType.MEGABYTES

    def test_measurement_unit_with_scale(self):
        """Test measurement unit with scale factor"""
        unit = MeasurementUnit(unit_type=MeasurementUnitType.KILOBYTES, scale=3)
        assert unit.scale == 3

    def test_measurement_unit_with_custom_label(self):
        """Test measurement unit with custom label"""
        unit = MeasurementUnit(
            unit_type=MeasurementUnitType.BYTES,
            custom_label="custom_bytes"
        )
        assert str(unit) == "custom_bytes"

    def test_measurement_unit_str_without_label(self):
        """Test string representation without custom label"""
        unit = MeasurementUnit(unit_type=MeasurementUnitType.MEGABYTES)
        assert str(unit) == "megabytes"

    def test_all_measurement_unit_types(self):
        """Test all defined measurement unit types are valid"""
        for unit_type in MeasurementUnitType:
            unit = MeasurementUnit(unit_type=unit_type)
            assert unit.unit_type == unit_type


class TestConstraintSpecification:
    """Test ConstraintSpecification component"""

    def test_constraint_less_than(self):
        """Test less than constraint evaluation"""
        constraint = ConstraintSpecification(
            operator=ComparisonOperator.LESS_THAN,
            value=100
        )
        assert constraint.evaluate(50)
        assert constraint.evaluate(99.9)
        assert not constraint.evaluate(100)
        assert not constraint.evaluate(101)

    def test_constraint_equal(self):
        """Test equality constraint evaluation"""
        constraint = ConstraintSpecification(
            operator=ComparisonOperator.EQUAL,
            value=100
        )
        assert constraint.evaluate(100)
        assert not constraint.evaluate(99.9)
        assert not constraint.evaluate(100.1)

    def test_constraint_greater_than_or_equal(self):
        """Test >= constraint evaluation"""
        constraint = ConstraintSpecification(
            operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
            value=50
        )
        assert constraint.evaluate(50)
        assert constraint.evaluate(100)
        assert not constraint.evaluate(49.9)

    def test_constraint_not_equal(self):
        """Test != constraint evaluation"""
        constraint = ConstraintSpecification(
            operator=ComparisonOperator.NOT_EQUAL,
            value=100
        )
        assert constraint.evaluate(99)
        assert constraint.evaluate(101)
        assert not constraint.evaluate(100)

    def test_constraint_with_unit(self):
        """Test constraint with measurement unit"""
        unit = MeasurementUnit(unit_type=MeasurementUnitType.MEGABYTES)
        constraint = ConstraintSpecification(
            operator=ComparisonOperator.GREATER_THAN,
            value=10,
            unit=unit
        )
        assert constraint.unit == unit


class TestPolicyStatements:
    """Test policy statement types"""

    def test_qos_objective_creation(self):
        """Test creating QoS objective statement"""
        qos = QosObjective(
            statement_id="qos-001",
            downlink_bandwidth=10000000,  # 10 Mbps
            uplink_bandwidth=5000000,     # 5 Mbps
            max_latency=50                # 50 ms
        )
        assert qos.statement_id == "qos-001"
        assert qos.downlink_bandwidth == 10000000
        assert qos.state == PolicyStateType.ACTIVE

    def test_qoe_objective_creation(self):
        """Test creating QoE objective statement"""
        qoe = QoeObjective(
            video_bitrate=5000000,  # 5 Mbps
            video_resolution="1920x1080",
            audio_quality="HD",
            buffering_time=100
        )
        assert qoe.video_bitrate == 5000000
        assert qoe.video_resolution == "1920x1080"

    def test_tsp_statement_creation(self):
        """Test creating Traffic Steering Preference"""
        tsp = TrafficSteeringPreference(
            preferred_access_type="5G_SA",
            preferred_network_slice="slice-001"
        )
        assert tsp.preferred_access_type == "5G_SA"

    def test_ue_level_objective_creation(self):
        """Test creating UE-level objective"""
        ue_obj = UeLevelObjective(
            session_timeout=3600,
            max_concurrent_connections=10
        )
        assert ue_obj.session_timeout == 3600
        assert ue_obj.max_concurrent_connections == 10

    def test_sla_objective_creation(self):
        """Test creating Slice SLA objective"""
        sla = SliceSlaObjective(
            availability=0.999,
            latency_percentile=50,
            throughput_commitment=1000000
        )
        assert sla.availability == 0.999
        assert sla.latency_percentile == 50

    def test_lb_objective_creation(self):
        """Test creating Load Balancing objective"""
        lb = LoadBalancingObjective(
            max_load_percentage=80,
            target_load_percentage=70
        )
        assert lb.max_load_percentage == 80
        assert lb.target_load_percentage == 70

    def test_es_objective_creation(self):
        """Test creating Energy Saving objective"""
        es = EnergySavingObjective(
            power_saving_target=20,
            renewable_energy_preference=True
        )
        assert es.power_saving_target == 20
        assert es.renewable_energy_preference is True

    def test_statement_with_constraints(self):
        """Test statement with constraints"""
        constraint = ConstraintSpecification(
            operator=ComparisonOperator.LESS_THAN,
            value=100
        )
        qos = QosObjective(
            downlink_bandwidth=10000000,
            constraints=[constraint]
        )
        assert len(qos.constraints) == 1
        assert qos.constraints[0].evaluate(50)

    def test_statement_priority_validation(self):
        """Test statement priority validation (0-255)"""
        qos = QosObjective(
            downlink_bandwidth=10000000,
            priority=100
        )
        assert qos.priority == 100

        with pytest.raises(ValidationError):
            QosObjective(
                downlink_bandwidth=10000000,
                priority=256  # Out of range
            )

    def test_statement_with_metadata(self):
        """Test statement with metadata"""
        qos = QosObjective(
            downlink_bandwidth=10000000,
            metadata={"owner": "admin", "version": "1.0"}
        )
        assert qos.metadata["owner"] == "admin"


class TestResourceDirective:
    """Test ResourceDirective component"""

    def test_resource_directive_creation(self):
        """Test creating resource directive"""
        directive = ResourceDirective(
            resource_id="res-001",
            action="limit",
            action_parameters={"limit": "10 Mbps"}
        )
        assert directive.resource_id == "res-001"
        assert directive.action == "limit"

    def test_resource_directive_with_constraints(self):
        """Test resource directive with constraints"""
        constraint = ConstraintSpecification(
            operator=ComparisonOperator.LESS_THAN,
            value=100
        )
        directive = ResourceDirective(
            resource_id="res-001",
            action="prioritize",
            constraints=[constraint]
        )
        assert len(directive.constraints) == 1


# ==================== SCOPE IDENTIFIER TESTS ====================

class TestPlmnId:
    """Test PLMN Identifier"""

    def test_plmn_creation(self):
        """Test creating PLMN identifier"""
        plmn = PlmnId(mcc="310", mnc="150")
        assert plmn.mcc == "310"
        assert plmn.mnc == "150"

    def test_plmn_string_representation(self):
        """Test PLMN string representation"""
        plmn = PlmnId(mcc="310", mnc="150")
        assert str(plmn) == "310-150"

    def test_plmn_validation_mcc_non_numeric(self):
        """Test PLMN validation rejects non-numeric MCC"""
        with pytest.raises(ValidationError):
            PlmnId(mcc="31A", mnc="150")

    def test_plmn_validation_mcc_length(self):
        """Test PLMN validation for MCC length"""
        with pytest.raises(ValidationError):
            PlmnId(mcc="31", mnc="150")  # Too short

    def test_plmn_validation_mnc_length(self):
        """Test PLMN validation for MNC length"""
        valid = PlmnId(mcc="310", mnc="15")  # 2 digits OK
        assert valid.mnc == "15"


class TestUeIdentifier:
    """Test UE Identifier"""

    def test_ue_identifier_creation(self):
        """Test creating UE identifier"""
        ue = UeIdentifier(
            ue_identifier="310150123456789",
            plmn=PlmnId(mcc="310", mnc="150")
        )
        assert ue.ue_identifier == "310150123456789"

    def test_ue_identifier_with_type(self):
        """Test UE identifier with type"""
        ue = UeIdentifier(
            ue_identifier="310150123456789",
            plmn=PlmnId(mcc="310", mnc="150"),
            identifier_type="IMSI"
        )
        assert ue.identifier_type == "IMSI"

    def test_ue_identifier_creation_via_factory(self):
        """Test creating UE identifier using factory"""
        ue = ScopeIdentifierFactory.create_ue_scope(
            ue_id="310150123456789",
            mcc="310",
            mnc="150",
            id_type="IMSI"
        )
        assert ue.ue_identifier == "310150123456789"
        assert ue.identifier_type == "IMSI"


class TestGroupIdentifier:
    """Test Group Identifier"""

    def test_group_identifier_creation(self):
        """Test creating group identifier"""
        group = GroupIdentifier(group_identifier="sales-group")
        assert group.group_identifier == "sales-group"

    def test_group_identifier_with_type(self):
        """Test group identifier with type"""
        group = GroupIdentifier(
            group_identifier="sales-group",
            group_type="NAME_BASED",
            description="Sales team"
        )
        assert group.group_type == "NAME_BASED"
        assert group.description == "Sales team"

    def test_group_identifier_factory(self):
        """Test creating group identifier using factory"""
        group = ScopeIdentifierFactory.create_group_scope(
            group_id="dept-it",
            group_type="DEPARTMENT",
            description="IT department"
        )
        assert group.group_identifier == "dept-it"


class TestSliceIdentifier:
    """Test Slice Identifier"""

    def test_slice_identifier_creation(self):
        """Test creating slice identifier"""
        slice_id = SliceIdentifier(sst=1)
        assert slice_id.sst == 1
        assert slice_id.sd is None

    def test_slice_identifier_with_sd(self):
        """Test slice identifier with SD"""
        slice_id = SliceIdentifier(sst=1, sd="001")
        assert slice_id.sd == "001"

    def test_slice_identifier_sst_range(self):
        """Test SST range validation"""
        # Min SST
        s1 = SliceIdentifier(sst=0)
        assert s1.sst == 0
        
        # Max SST
        s2 = SliceIdentifier(sst=255)
        assert s2.sst == 255

        # Out of range
        with pytest.raises(ValidationError):
            SliceIdentifier(sst=256)

    def test_slice_identifier_with_plmn(self):
        """Test slice identifier with PLMN"""
        slice_id = SliceIdentifier(
            sst=1,
            sd="001",
            plmn=PlmnId(mcc="310", mnc="150")
        )
        assert slice_id.plmn.mcc == "310"

    def test_slice_identifier_factory(self):
        """Test creating slice identifier using factory"""
        slice_id = ScopeIdentifierFactory.create_slice_scope(
            sst=1,
            sd="001",
            mcc="310",
            mnc="150"
        )
        assert slice_id.sst == 1
        assert slice_id.sd == "001"


class TestQosClassIdentifier:
    """Test QoS Class Identifier"""

    def test_qos_identifier_creation(self):
        """Test creating QoS identifier"""
        qos = QosClassIdentifier(qci=5)
        assert qos.qci == 5

    def test_qos_identifier_with_arp(self):
        """Test QoS identifier with ARP"""
        qos = QosClassIdentifier(qci=5, arp=8)
        assert qos.arp == 8

    def test_qos_identifier_with_bitrates(self):
        """Test QoS identifier with bitrates"""
        qos = QosClassIdentifier(
            qci=5,
            mbrUl=1000000,
            mbrDl=2000000
        )
        assert qos.mbrUl == 1000000
        assert qos.mbrDl == 2000000

    def test_qos_identifier_factory(self):
        """Test creating QoS identifier using factory"""
        qos = ScopeIdentifierFactory.create_qos_scope(
            qci=5,
            arp=8,
            mbr_ul=1000000,
            mbr_dl=2000000
        )
        assert qos.qci == 5
        assert qos.arp == 8


class TestCellIdentifier:
    """Test Cell Identifier"""

    def test_cell_identifier_creation(self):
        """Test creating cell identifier"""
        cell = CellIdentifier(
            cell_id="12F45600F123401",
            plmn=PlmnId(mcc="310", mnc="150")
        )
        assert cell.cell_id == "12F45600F123401"

    def test_cell_identifier_with_type(self):
        """Test cell identifier with type"""
        cell = CellIdentifier(
            cell_id="12F45600F123401",
            plmn=PlmnId(mcc="310", mnc="150"),
            cell_type="MACRO"
        )
        assert cell.cell_type == "MACRO"

    def test_cell_identifier_factory(self):
        """Test creating cell identifier using factory"""
        cell = ScopeIdentifierFactory.create_cell_scope(
            cell_id="12F45600F123401",
            mcc="310",
            mnc="150",
            cell_type="MACRO"
        )
        assert cell.cell_id == "12F45600F123401"


class TestGuAmI:
    """Test Global AMF Identifier"""

    def test_guami_creation(self):
        """Test creating GuAmI"""
        guami = GuAmI(
            plmn=PlmnId(mcc="310", mnc="150"),
            amf_region_id=1,
            amf_set_id=256,
            amf_pointer=1
        )
        assert guami.amf_region_id == 1

    def test_guami_string_representation(self):
        """Test GuAmI string format"""
        guami = GuAmI(
            plmn=PlmnId(mcc="310", mnc="150"),
            amf_region_id=1,
            amf_set_id=256,
            amf_pointer=1
        )
        # Should produce: 310-150:010100001
        assert "310-150" in guami.to_string()


class TestTaiList:
    """Test TAI List"""

    def test_tai_list_creation(self):
        """Test creating TAI list"""
        tai = TrackingAreaIdentifier(
            plmn=PlmnId(mcc="310", mnc="150"),
            tac=1
        )
        tai_list = TaiList(tracking_areas=[tai])
        assert len(tai_list.tracking_areas) == 1

    def test_tai_list_multiple_entries(self):
        """Test TAI list with multiple entries"""
        ta1 = TrackingAreaIdentifier(
            plmn=PlmnId(mcc="310", mnc="150"),
            tac=1
        )
        ta2 = TrackingAreaIdentifier(
            plmn=PlmnId(mcc="310", mnc="150"),
            tac=2
        )
        tai_list = TaiList(tracking_areas=[ta1, ta2])
        assert len(tai_list.tracking_areas) == 2

    def test_tai_list_factory(self):
        """Test creating TAI list using factory"""
        tai_list = ScopeIdentifierFactory.create_tai_list_scope(
            tai_list=[
                {'plmn': {'mcc': '310', 'mnc': '150'}, 'tac': 1},
                {'plmn': {'mcc': '310', 'mnc': '150'}, 'tac': 2}
            ]
        )
        assert len(tai_list.tracking_areas) == 2


# ==================== POLICY WORKFLOW TESTS ====================

class TestPolicyWorkflows:
    """Test complete policy creation workflows"""

    def test_qos_policy_ue_workflow(self):
        """Test QoS policy targeting specific UE"""
        # Create scope
        ue_scope = ScopeIdentifierFactory.create_ue_scope(
            ue_id="310150123456789",
            mcc="310",
            mnc="150",
            id_type="IMSI"
        )
        
        # Create statement
        qos = QosObjective(
            statement_id="qos-001",
            downlink_bandwidth=10000000,
            max_latency=50
        )
        
        # Validate scope/policy combination
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'QoSTarget',
            {'ueId': True, 'qosId': True, 'sliceId': False,
             'groupId': False, 'cellId': False},
            'qosObjectives'
        )
        assert is_valid

    def test_slice_sla_policy_workflow(self):
        """Test Slice SLA policy"""
        # Create scope
        slice_scope = ScopeIdentifierFactory.create_slice_scope(
            sst=1,
            sd="001",
            mcc="310",
            mnc="150"
        )
        
        # Create statement
        sla = SliceSlaObjective(
            statement_id="sla-001",
            availability=0.999,
            latency_percentile=50
        )
        
        # Validate
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'SliceSLATarget',
            {'sliceId': True, 'ueId': False, 'groupId': False,
             'qosId': False, 'cellId': False},
            'sliceSlaObjectives'
        )
        assert is_valid

    def test_tsp_policy_workflow(self):
        """Test Traffic Steering Preference policy"""
        # Create statement
        tsp = TrafficSteeringPreference(
            statement_id="tsp-001",
            preferred_access_type="5G_SA"
        )
        
        # Validate - can be UE or Slice based
        is_valid_ue, _ = PolicyScopeValidator.validate_policy_scope_combination(
            'TrafficSteeringPreference',
            {'ueId': True, 'sliceId': False, 'groupId': False,
             'qosId': False, 'cellId': False},
            'tspResources'
        )
        assert is_valid_ue

        is_valid_slice, _ = PolicyScopeValidator.validate_policy_scope_combination(
            'TrafficSteeringPreference',
            {'sliceId': True, 'ueId': False, 'groupId': False,
             'qosId': False, 'cellId': False},
            'tspResources'
        )
        assert is_valid_slice

    def test_load_balancing_policy_workflow(self):
        """Test Load Balancing policy"""
        # Create scope
        cell_scope = ScopeIdentifierFactory.create_cell_scope(
            cell_id="12F45600F123401",
            mcc="310",
            mnc="150"
        )
        
        # Create statement
        lb = LoadBalancingObjective(
            statement_id="lb-001",
            max_load_percentage=80,
            target_load_percentage=70
        )
        
        # Validate
        is_valid, error = PolicyScopeValidator.validate_policy_scope_combination(
            'LoadBalancing',
            {'cellId': True, 'ueId': False, 'groupId': False,
             'sliceId': False, 'qosId': False},
            'lbObjectives'
        )
        assert is_valid


# ==================== INTEGRATION TESTS ====================

class TestCrossComponentIntegration:
    """Test integration between components"""

    def test_qos_with_range_constraint(self):
        """Test QoS objective with range constraints"""
        # Create constraint
        bw_constraint = StatementComponentFactory.create_range_constraint(
            min_val=1000000,
            max_val=100000000,
            step=1000000
        )
        
        # Create statement with constraint
        qos = QosObjective(
            downlink_bandwidth=10000000,
            constraints=[
                ConstraintSpecification(
                    operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
                    value=1000000
                )
            ]
        )
        
        # Validate constraint
        assert bw_constraint.is_valid_value(10000000)
        assert qos.constraints[0].evaluate(10000000)

    def test_sla_with_multiple_constraints(self):
        """Test SLA objective with multiple constraints"""
        sla = SliceSlaObjective(
            availability=0.999,
            constraints=[
                ConstraintSpecification(
                    operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
                    value=0.99
                ),
                ConstraintSpecification(
                    operator=ComparisonOperator.LESS_THAN_OR_EQUAL,
                    value=1.0
                )
            ]
        )
        
        assert len(sla.constraints) == 2
        assert sla.constraints[0].evaluate(0.999)
        assert sla.constraints[1].evaluate(0.999)

    def test_statement_with_resource_directives(self):
        """Test statement with resource directives"""
        directives = [
            ResourceDirective(
                resource_id="res-1",
                action="limit",
                action_parameters={"limit": "10 Mbps"}
            ),
            ResourceDirective(
                resource_id="res-2",
                action="prioritize"
            )
        ]
        
        qos = QosObjective(
            downlink_bandwidth=5000000
        )
        
        assert len(directives) == 2
        assert directives[0].resource_id == "res-1"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
