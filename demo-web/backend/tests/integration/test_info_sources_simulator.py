"""
Info Sources Simulator Behavioral Verification Tests

Validates that the InfoSourceSimulator meets Phase A requirements:
- Deterministic result generation for ORAN_UEGeoandVel_3.0.1
- Notification delivery mechanism
- State reset between test runs
"""

import pytest
import asyncio
from app.modules.simulators.info_sources import InfoSourceSimulator


@pytest.fixture
def simulator():
    """Provide a fresh simulator instance for each test."""
    sim = InfoSourceSimulator({"seed": 42, "mode": "deterministic"})
    yield sim
    sim.reset()


class TestInfoSourceSimulatorResultGeneration:
    """Test EI result generation behavior."""
    
    @pytest.mark.asyncio
    async def test_generate_uegeoandvel_result_returns_array(self, simulator):
        """Result for UE geo/velocity should be an array of observations."""
        result = await simulator.generate_result_for_ei_job(
            "ORAN_UEGeoandVel_3.0.1",
            "job_1"
        )
        
        assert isinstance(result, list), "Result should be array"
        assert len(result) > 0, "Result should have observations"
    
    @pytest.mark.asyncio
    async def test_result_contains_location_and_velocity(self, simulator):
        """Each result observation should contain location and velocity."""
        result = await simulator.generate_result_for_ei_job(
            "ORAN_UEGeoandVel_3.0.1",
            "job_2"
        )
        
        for obs in result:
            assert "location" in obs, "Observation missing location"
            assert "velocity" in obs, "Observation missing velocity"
            assert "timestamp" in obs, "Observation missing timestamp"
    
    @pytest.mark.asyncio
    async def test_result_respects_reporting_amount(self, simulator):
        """Result count should match job definition reporting amount."""
        job_def = {
            "jobDefinition": {
                "constraints": {"reportingAmount": 5}
            }
        }
        
        result = await simulator.generate_result_for_ei_job(
            "ORAN_UEGeoandVel_3.0.1",
            "job_3",
            job_def
        )
        
        assert len(result) == 5, "Result count should match reportingAmount"
    
    @pytest.mark.asyncio
    async def test_deterministic_result_with_seed(self, simulator):
        """Same seed should produce identical results across runs."""
        sim1 = InfoSourceSimulator({"seed": 42})
        sim2 = InfoSourceSimulator({"seed": 42})
        
        result1 = await sim1.generate_result_for_ei_job(
            "ORAN_UEGeoandVel_3.0.1",
            "job_det_1"
        )
        
        result2 = await sim2.generate_result_for_ei_job(
            "ORAN_UEGeoandVel_3.0.1",
            "job_det_2"
        )
        
        # Compare first observation coordinates
        assert result1[0]["location"]["pointAltitudeUncertainty"]["point"]["latitude"] == \
               result2[0]["location"]["pointAltitudeUncertainty"]["point"]["latitude"]
        assert result1[0]["location"]["pointAltitudeUncertainty"]["point"]["longitude"] == \
               result2[0]["location"]["pointAltitudeUncertainty"]["point"]["longitude"]


class TestInfoSourceSimulatorNotifications:
    """Test notification delivery mechanism."""
    
    @pytest.mark.asyncio
    async def test_send_result_notification_succeeds(self, simulator):
        """Result notification should be sent and tracked."""
        result = {"data": "test"}
        success = await simulator.send_result_notification(
            "http://example.com/callback",
            "job_notify_1",
            result
        )
        
        assert success is True
        assert len(simulator.get_notification_history()) == 1
    
    @pytest.mark.asyncio
    async def test_send_status_notification_succeeds(self, simulator):
        """Status notification should be sent and tracked."""
        success = await simulator.send_status_notification(
            "http://example.com/callback",
            "job_status_1",
            "COMPLETED",
            "Job result available"
        )
        
        assert success is True
        assert len(simulator.get_notification_history()) == 1
    
    @pytest.mark.asyncio
    async def test_notification_history_tracks_all_deliveries(self, simulator):
        """All notifications should be tracked in history."""
        await simulator.send_result_notification(
            "http://example.com/callback",
            "job_1",
            {"data": "result1"}
        )
        
        await simulator.send_status_notification(
            "http://example.com/callback",
            "job_1",
            "STARTED"
        )
        
        history = simulator.get_notification_history()
        assert len(history) == 2


class TestInfoSourceSimulatorStateManagement:
    """Test simulator state management."""
    
    @pytest.mark.asyncio
    async def test_reset_clears_state(self, simulator):
        """Reset should clear all generated results and notifications."""
        # Generate some data
        await simulator.generate_result_for_ei_job(
            "ORAN_UEGeoandVel_3.0.1",
            "job_reset_1"
        )
        
        await simulator.send_status_notification(
            "http://example.com/callback",
            "job_reset_1",
            "STARTED"
        )
        
        assert len(simulator.get_notification_history()) > 0
        
        # Reset and verify
        simulator.reset()
        
        assert len(simulator.get_notification_history()) == 0
    
    @pytest.mark.asyncio
    async def test_get_state_summary(self, simulator):
        """State summary should report simulator configuration."""
        summary = simulator.get_state_summary()
        
        assert "mode" in summary
        assert "seed" in summary
        assert "supported_ei_types" in summary
        assert "ORAN_UEGeoandVel_3.0.1" in summary["supported_ei_types"]


class TestInfoSourceSimulatorIntegration:
    """Integration tests with Phase A conformance suites."""
    
    @pytest.mark.asyncio
    async def test_full_ei_job_lifecycle_flow(self, simulator):
        """Verify complete EI job result generation and notification flow."""
        ei_job_id = "phase_a_job_1"
        callback_uri = "http://non-rt-ric/callback/job"
        job_def = {
            "jobDefinition": {
                "constraints": {"reportingAmount": 3}
            }
        }
        
        # Step 1: Generate result
        result = await simulator.generate_result_for_ei_job(
            "ORAN_UEGeoandVel_3.0.1",
            ei_job_id,
            job_def
        )
        
        assert len(result) == 3, "Should generate 3 observations"
        
        # Step 2: Send status - STARTED
        await simulator.send_status_notification(
            callback_uri,
            ei_job_id,
            "STARTED",
            "EI job started by info source"
        )
        
        # Step 3: Send result delivery
        await simulator.send_result_notification(
            callback_uri,
            ei_job_id,
            result
        )
        
        # Step 4: Send status - COMPLETED
        await simulator.send_status_notification(
            callback_uri,
            ei_job_id,
            "COMPLETED",
            "EI job completed and result delivered"
        )
        
        # Verify full history
        history = simulator.get_notification_history()
        assert len(history) == 3, "Should have 3 notifications"
        
        # Verify state
        summary = simulator.get_state_summary()
        assert summary["total_results_generated"] == 1
        assert summary["total_notifications_sent"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
