package com.tts.demo.model;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for TrafficProfile model.
 * Tests profile configuration and JMeter properties conversion.
 */
class TrafficProfileTest {

    private TrafficProfile profile;

    @BeforeEach
    void setUp() {
        profile = new TrafficProfile();
    }

    @Test
    void testDefaultValues() {
        assertEquals(10, profile.getConcurrentCalls());
        assertEquals(100, profile.getTotalCalls());
        assertEquals(10, profile.getRampUpSeconds());
        assertEquals(0, profile.getDurationSeconds());
        assertEquals(0.0, profile.getFailureRate(), 0.01);
        assertEquals(ActorType.UNKNOWN, profile.getFailureNode());
        assertEquals("NONE", profile.getFailureScenario());
        assertEquals(5000, profile.getCallHoldTimeMs());
        assertEquals(100, profile.getInterCallDelayMs());
        assertTrue(profile.isCollectDetailedStats());
        assertFalse(profile.isExportRawData());
    }

    @Test
    void testSetAllFields() {
        profile.setConcurrentCalls(50);
        profile.setTotalCalls(500);
        profile.setRampUpSeconds(30);
        profile.setDurationSeconds(60);
        profile.setFailureRate(15.0);
        profile.setFailureNode(ActorType.P_CSCF);
        profile.setFailureScenario("CONF-AUTH-002");
        profile.setFailureType(FailureType.PROTOCOL_ERROR);
        profile.setCallHoldTimeMs(3000);
        profile.setInterCallDelayMs(200);
        profile.setCollectDetailedStats(false);
        profile.setExportRawData(true);
        
        assertEquals(50, profile.getConcurrentCalls());
        assertEquals(500, profile.getTotalCalls());
        assertEquals(30, profile.getRampUpSeconds());
        assertEquals(60, profile.getDurationSeconds());
        assertEquals(15.0, profile.getFailureRate(), 0.01);
        assertEquals(ActorType.P_CSCF, profile.getFailureNode());
        assertEquals("CONF-AUTH-002", profile.getFailureScenario());
        assertEquals(FailureType.PROTOCOL_ERROR, profile.getFailureType());
        assertEquals(3000, profile.getCallHoldTimeMs());
        assertEquals(200, profile.getInterCallDelayMs());
        assertFalse(profile.isCollectDetailedStats());
        assertTrue(profile.isExportRawData());
    }

    @Test
    void testToJMeterPropertiesWithFullConfiguration() {
        profile.setConcurrentCalls(25);
        profile.setTotalCalls(250);
        profile.setRampUpSeconds(20);
        profile.setDurationSeconds(60);
        profile.setFailureRate(10.0);
        profile.setFailureNode(ActorType.S_CSCF);
        profile.setFailureScenario("CONF-REG-001");
        profile.setFailureType(FailureType.TIMEOUT);
        profile.setCallHoldTimeMs(4000);
        profile.setInterCallDelayMs(150);
        
        Map<String, String> props = profile.toJMeterProperties();
        
        assertNotNull(props);
        assertEquals("25", props.get("threads"));
        assertEquals("10", props.get("loops")); // 250 / 25 = 10 loops per thread
        assertEquals("20", props.get("rampup"));
        assertEquals("60", props.get("duration"));
        assertEquals("10.0", props.get("failure_rate"));
        assertEquals("S_CSCF", props.get("failure_node"));
        assertEquals("CONF-REG-001", props.get("failure_scenario"));
        assertEquals("TIMEOUT", props.get("failure_type"));
        assertEquals("4000", props.get("call_hold_time"));
        assertEquals("150", props.get("inter_call_delay"));
        assertEquals("408", props.get("failure_response_code"));
    }

    @Test
    void testToJMeterPropertiesWithNoFailure() {
        profile.setConcurrentCalls(10);
        profile.setTotalCalls(100);
        profile.setFailureRate(0.0);
        profile.setFailureScenario("NONE");
        
        Map<String, String> props = profile.toJMeterProperties();
        
        assertNotNull(props);
        assertEquals("10", props.get("threads"));
        assertEquals("10", props.get("loops"));
        assertEquals("0.0", props.get("failure_rate"));
        assertEquals("NONE", props.get("failure_scenario"));
    }

    @Test
    void testFailureRateBounds() {
        // Test upper bound
        profile.setFailureRate(150.0);
        assertEquals(100.0, profile.getFailureRate(), 0.01);
        
        // Test lower bound
        profile.setFailureRate(-10.0);
        assertEquals(0.0, profile.getFailureRate(), 0.01);
        
        // Test valid value
        profile.setFailureRate(50.0);
        assertEquals(50.0, profile.getFailureRate(), 0.01);
    }

    @Test
    void testValidationValid() {
        profile.setConcurrentCalls(10);
        profile.setTotalCalls(100);
        profile.setRampUpSeconds(10);
        profile.setFailureRate(25.0);
        
        assertTrue(profile.isValid());
    }

    @Test
    void testValidationInvalidConcurrentCalls() {
        profile.setConcurrentCalls(0);
        profile.setTotalCalls(100);
        
        assertFalse(profile.isValid());
    }

    @Test
    void testValidationInvalidTotalCalls() {
        profile.setConcurrentCalls(10);
        profile.setTotalCalls(0);
        
        assertFalse(profile.isValid());
    }

    @Test
    void testValidationInvalidFailureRate() {
        profile.setConcurrentCalls(10);
        profile.setTotalCalls(100);
        profile.setFailureRate(150.0); // Will be clamped to 100, which is valid
        
        assertTrue(profile.isValid()); // After clamping, it's valid
    }

    @Test
    void testExtractResponseCodeFromScenario() {
        // Test various scenarios
        profile.setFailureScenario("CONF-AUTH-001");
        Map<String, String> props = profile.toJMeterProperties();
        assertEquals("401", props.get("failure_response_code"));
        
        profile.setFailureScenario("CONF-SIP-001");
        props = profile.toJMeterProperties();
        assertEquals("400", props.get("failure_response_code"));
        
        profile.setFailureScenario("CONF-CALL-002");
        props = profile.toJMeterProperties();
        assertEquals("580", props.get("failure_response_code"));
    }

    @Test
    void testExtractResponseCodeWithNoneScenario() {
        profile.setFailureScenario("NONE");
        Map<String, String> props = profile.toJMeterProperties();
        assertFalse(props.containsKey("failure_response_code") && !props.get("failure_response_code").isEmpty());
    }

    @Test
    void testLoopsCalculation() {
        // Test that loops per thread is calculated correctly
        profile.setConcurrentCalls(20);
        profile.setTotalCalls(200);
        
        Map<String, String> props = profile.toJMeterProperties();
        assertEquals("10", props.get("loops")); // 200 / 20 = 10
        
        profile.setConcurrentCalls(5);
        profile.setTotalCalls(100);
        
        props = profile.toJMeterProperties();
        assertEquals("20", props.get("loops")); // 100 / 5 = 20
    }

    @Test
    void testDifferentFailureNodes() {
        ActorType[] nodes = {
            ActorType.P_CSCF,
            ActorType.S_CSCF,
            ActorType.I_CSCF,
            ActorType.HSS,
            ActorType.AS
        };
        
        for (ActorType node : nodes) {
            profile.setFailureNode(node);
            assertEquals(node, profile.getFailureNode());
            
            Map<String, String> props = profile.toJMeterProperties();
            assertEquals(node.name(), props.get("failure_node"));
        }
    }

    @Test
    void testDifferentFailureTypes() {
        FailureType[] types = {
            FailureType.PROTOCOL_ERROR,
            FailureType.TIMEOUT,
            FailureType.AUTH_FAILURE
        };
        
        for (FailureType type : types) {
            profile.setFailureType(type);
            assertEquals(type, profile.getFailureType());
            
            Map<String, String> props = profile.toJMeterProperties();
            assertEquals(type.name(), props.get("failure_type"));
        }
    }

    @Test
    void testToString() {
        profile.setProfileName("Test Profile");
        profile.setConcurrentCalls(20);
        profile.setTotalCalls(200);
        profile.setFailureRate(15.0);
        profile.setFailureNode(ActorType.P_CSCF);
        
        String str = profile.toString();
        assertNotNull(str);
        assertTrue(str.contains("Test Profile"));
        assertTrue(str.contains("200"));
        assertTrue(str.contains("20"));
        assertTrue(str.contains("15"));
    }

    @Test
    void testProfileIdAndNameAndDescription() {
        profile.setProfileId("prof-001");
        profile.setProfileName("Load Test Profile");
        profile.setDescription("High-volume load test with 15% failure rate");
        
        assertEquals("prof-001", profile.getProfileId());
        assertEquals("Load Test Profile", profile.getProfileName());
        assertEquals("High-volume load test with 15% failure rate", profile.getDescription());
    }

    @Test
    void testCallTimingConfiguration() {
        profile.setCallHoldTimeMs(10000);
        profile.setInterCallDelayMs(500);
        
        assertEquals(10000, profile.getCallHoldTimeMs());
        assertEquals(500, profile.getInterCallDelayMs());
        
        Map<String, String> props = profile.toJMeterProperties();
        assertEquals("10000", props.get("call_hold_time"));
        assertEquals("500", props.get("inter_call_delay"));
    }

    @Test
    void testStatisticsConfiguration() {
        profile.setCollectDetailedStats(false);
        profile.setExportRawData(true);
        
        assertFalse(profile.isCollectDetailedStats());
        assertTrue(profile.isExportRawData());
    }

    @Test
    void testJMeterPropertiesKeysPresent() {
        Map<String, String> props = profile.toJMeterProperties();
        
        assertTrue(props.containsKey("threads"));
        assertTrue(props.containsKey("loops"));
        assertTrue(props.containsKey("rampup"));
        assertTrue(props.containsKey("duration"));
        assertTrue(props.containsKey("failure_rate"));
        assertTrue(props.containsKey("failure_node"));
        assertTrue(props.containsKey("failure_scenario"));
        assertTrue(props.containsKey("failure_type"));
        assertTrue(props.containsKey("call_hold_time"));
        assertTrue(props.containsKey("inter_call_delay"));
    }
}
