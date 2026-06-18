package com.tts.demo.model;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for ConformanceScenario enum.
 * Tests 3GPP conformance scenarios mapping and metadata.
 */
class ConformanceScenarioTest {

    @Test
    void testAllScenariosHaveIds() {
        for (ConformanceScenario scenario : ConformanceScenario.values()) {
            assertNotNull(scenario.getScenarioId());
            assertFalse(scenario.getScenarioId().isEmpty());
        }
    }

    @Test
    void testAllScenariosHaveNames() {
        for (ConformanceScenario scenario : ConformanceScenario.values()) {
            assertNotNull(scenario.getScenarioName());
            assertFalse(scenario.getScenarioName().isEmpty());
        }
    }

    @Test
    void testAllScenariosHaveDescriptions() {
        for (ConformanceScenario scenario : ConformanceScenario.values()) {
            assertNotNull(scenario.getDescription());
            assertFalse(scenario.getDescription().isEmpty());
        }
    }

    @Test
    void testAllScenariosHaveExpectedResponses() {
        for (ConformanceScenario scenario : ConformanceScenario.values()) {
            assertNotNull(scenario.getExpectedResponse());
            assertFalse(scenario.getExpectedResponse().isEmpty());
        }
    }

    @Test
    void testAllScenariosHaveAffectedNodes() {
        for (ConformanceScenario scenario : ConformanceScenario.values()) {
            assertNotNull(scenario.getAffectedNode());
        }
    }

    @Test
    void testSipProtocolScenarios() {
        assertEquals("CONF-SIP-001", ConformanceScenario.INVALID_SIP_URI.getScenarioId());
        assertTrue(ConformanceScenario.INVALID_SIP_URI.getExpectedResponse().contains("400"));
        assertTrue(ConformanceScenario.INVALID_SIP_URI.getDescription().toLowerCase().contains("uri"));
        
        assertEquals("CONF-SIP-002", ConformanceScenario.MISSING_MANDATORY_HEADER.getScenarioId());
        assertTrue(ConformanceScenario.MISSING_MANDATORY_HEADER.getExpectedResponse().contains("400"));
        
        assertEquals("CONF-SIP-003", ConformanceScenario.INVALID_CSEQ_NUMBER.getScenarioId());
        assertTrue(ConformanceScenario.INVALID_CSEQ_NUMBER.getExpectedResponse().contains("400"));
        
        assertEquals("CONF-SIP-004", ConformanceScenario.MALFORMED_SDP_OFFER.getScenarioId());
        assertTrue(ConformanceScenario.MALFORMED_SDP_OFFER.getExpectedResponse().contains("488"));
    }

    @Test
    void testAuthenticationScenarios() {
        assertEquals("CONF-AUTH-001", ConformanceScenario.INVALID_AUTH_HEADER.getScenarioId());
        assertTrue(ConformanceScenario.INVALID_AUTH_HEADER.getExpectedResponse().contains("401"));
        
        assertEquals("CONF-AUTH-002", ConformanceScenario.EXPIRED_NONCE.getScenarioId());
        assertTrue(ConformanceScenario.EXPIRED_NONCE.getExpectedResponse().contains("401"));
        
        assertEquals("CONF-AUTH-003", ConformanceScenario.WRONG_CREDENTIALS.getScenarioId());
        assertTrue(ConformanceScenario.WRONG_CREDENTIALS.getExpectedResponse().contains("403"));
    }

    @Test
    void testRegistrationScenarios() {
        assertEquals("CONF-REG-001", ConformanceScenario.REGISTRATION_TIMEOUT.getScenarioId());
        assertTrue(ConformanceScenario.REGISTRATION_TIMEOUT.getExpectedResponse().contains("408"));
        
        assertEquals("CONF-REG-002", ConformanceScenario.INVALID_CONTACT_HEADER.getScenarioId());
        assertTrue(ConformanceScenario.INVALID_CONTACT_HEADER.getExpectedResponse().contains("400"));
        
        assertEquals("CONF-REG-003", ConformanceScenario.REGISTRATION_REJECTED_NOT_PROVISIONED.getScenarioId());
        assertTrue(ConformanceScenario.REGISTRATION_REJECTED_NOT_PROVISIONED.getExpectedResponse().contains("403"));
    }

    @Test
    void testSessionSetupScenarios() {
        assertEquals("CONF-CALL-001", ConformanceScenario.INVITE_TIMEOUT.getScenarioId());
        assertTrue(ConformanceScenario.INVITE_TIMEOUT.getExpectedResponse().contains("408"));
        
        assertEquals("CONF-CALL-002", ConformanceScenario.PRECONDITION_FAILURE.getScenarioId());
        assertTrue(ConformanceScenario.PRECONDITION_FAILURE.getExpectedResponse().contains("580"));
        
        assertEquals("CONF-CALL-003", ConformanceScenario.RESOURCE_ALLOCATION_FAILURE.getScenarioId());
        assertTrue(ConformanceScenario.RESOURCE_ALLOCATION_FAILURE.getExpectedResponse().contains("503"));
        
        assertEquals("CONF-CALL-004", ConformanceScenario.INCOMPATIBLE_MEDIA.getScenarioId());
        assertTrue(ConformanceScenario.INCOMPATIBLE_MEDIA.getExpectedResponse().contains("488"));
    }

    @Test
    void testRoutingScenarios() {
        assertEquals("CONF-ROUTE-001", ConformanceScenario.ROUTING_FAILURE_USER_NOT_FOUND.getScenarioId());
        assertTrue(ConformanceScenario.ROUTING_FAILURE_USER_NOT_FOUND.getExpectedResponse().contains("480"));
        
        assertEquals("CONF-ROUTE-002", ConformanceScenario.ROUTING_FAILURE_NO_PATH.getScenarioId());
        assertTrue(ConformanceScenario.ROUTING_FAILURE_NO_PATH.getExpectedResponse().contains("404"));
    }

    @Test
    void testEmergencyScenario() {
        assertEquals("CONF-EMERG-001", ConformanceScenario.EMERGENCY_CALL_REJECTION.getScenarioId());
        assertTrue(ConformanceScenario.EMERGENCY_CALL_REJECTION.getExpectedResponse().contains("380"));
    }

    @Test
    void testTerminationScenario() {
        assertEquals("CONF-TERM-001", ConformanceScenario.BYE_TIMEOUT.getScenarioId());
        assertTrue(ConformanceScenario.BYE_TIMEOUT.getExpectedResponse().contains("408"));
    }

    @Test
    void testNoneScenario() {
        assertEquals("CONF-NONE", ConformanceScenario.NONE.getScenarioId());
        assertTrue(ConformanceScenario.NONE.getExpectedResponse().contains("200"));
        assertEquals(ActorType.UNKNOWN, ConformanceScenario.NONE.getAffectedNode());
    }

    @Test
    void testScenarioCount() {
        ConformanceScenario[] scenarios = ConformanceScenario.values();
        assertEquals(17, scenarios.length, "Should have exactly 17 conformance scenarios");
    }

    @Test
    void testValidResponseCodes() {
        // Verify that response codes are from valid SIP ranges
        for (ConformanceScenario scenario : ConformanceScenario.values()) {
            String response = scenario.getExpectedResponse();
            // Extract numeric code from response like "400 Bad Request"
            String codeStr = response.split(" ")[0];
            int code = Integer.parseInt(codeStr);
            assertTrue(code >= 200 && code <= 699,
                    "Response code should be in valid SIP range: " + code);
        }
    }

    @Test
    void testIdFormat() {
        for (ConformanceScenario scenario : ConformanceScenario.values()) {
            String id = scenario.getScenarioId();
            assertTrue(id.matches("CONF-[A-Z]+-\\d{3}") || id.equals("CONF-NONE"),
                    "ID should match pattern CONF-XXX-NNN or be CONF-NONE: " + id);
        }
    }

    @Test
    void testDisplayString() {
        for (ConformanceScenario scenario : ConformanceScenario.values()) {
            String display = scenario.getDisplayString();
            assertNotNull(display);
            assertFalse(display.isEmpty());
            assertTrue(display.contains(scenario.getScenarioId()));
            assertTrue(display.contains(scenario.getAffectedNode().getDisplayName()));
        }
    }

    @Test
    void testFromIdMethod() {
        assertEquals(ConformanceScenario.INVALID_SIP_URI, 
                     ConformanceScenario.fromId("CONF-SIP-001"));
        assertEquals(ConformanceScenario.INVALID_AUTH_HEADER, 
                     ConformanceScenario.fromId("CONF-AUTH-001"));
        assertEquals(ConformanceScenario.REGISTRATION_TIMEOUT, 
                     ConformanceScenario.fromId("CONF-REG-001"));
        assertEquals(ConformanceScenario.NONE, 
                     ConformanceScenario.fromId("INVALID_ID"));
    }

    @Test
    void testSpecificScenarioDetails() {
        // INVALID_SIP_URI
        assertEquals(ActorType.P_CSCF, ConformanceScenario.INVALID_SIP_URI.getAffectedNode());
        assertTrue(ConformanceScenario.INVALID_SIP_URI.getDescription().toLowerCase().contains("uri"));
        
        // WRONG_CREDENTIALS
        assertEquals(ActorType.HSS, ConformanceScenario.WRONG_CREDENTIALS.getAffectedNode());
        assertTrue(ConformanceScenario.WRONG_CREDENTIALS.getDescription().toLowerCase().contains("credential"));
        
        // REGISTRATION_TIMEOUT
        assertEquals(ActorType.S_CSCF, ConformanceScenario.REGISTRATION_TIMEOUT.getAffectedNode());
        assertTrue(ConformanceScenario.REGISTRATION_TIMEOUT.getDescription().toLowerCase().contains("timeout"));
        
        // INVITE_TIMEOUT
        assertEquals(ActorType.S_CSCF, ConformanceScenario.INVITE_TIMEOUT.getAffectedNode());
        assertTrue(ConformanceScenario.INVITE_TIMEOUT.getExpectedResponse().contains("408"));
        
        // ROUTING_FAILURE_USER_NOT_FOUND
        assertEquals(ActorType.S_CSCF, ConformanceScenario.ROUTING_FAILURE_USER_NOT_FOUND.getAffectedNode());
        assertTrue(ConformanceScenario.ROUTING_FAILURE_USER_NOT_FOUND.getExpectedResponse().contains("480"));
    }

    @Test
    void testEnumValueOf() {
        ConformanceScenario scenario = ConformanceScenario.valueOf("INVALID_SIP_URI");
        assertNotNull(scenario);
        assertEquals("CONF-SIP-001", scenario.getScenarioId());
    }

    @Test
    void testEnumValueOfInvalid() {
        assertThrows(IllegalArgumentException.class, () -> {
            ConformanceScenario.valueOf("INVALID_SCENARIO");
        });
    }

    @Test
    void testAllScenariosAccessible() {
        // Verify all scenarios can be accessed
        assertNotNull(ConformanceScenario.INVALID_SIP_URI);
        assertNotNull(ConformanceScenario.MISSING_MANDATORY_HEADER);
        assertNotNull(ConformanceScenario.INVALID_CSEQ_NUMBER);
        assertNotNull(ConformanceScenario.MALFORMED_SDP_OFFER);
        assertNotNull(ConformanceScenario.INVALID_AUTH_HEADER);
        assertNotNull(ConformanceScenario.EXPIRED_NONCE);
        assertNotNull(ConformanceScenario.WRONG_CREDENTIALS);
        assertNotNull(ConformanceScenario.REGISTRATION_TIMEOUT);
        assertNotNull(ConformanceScenario.INVALID_CONTACT_HEADER);
        assertNotNull(ConformanceScenario.REGISTRATION_REJECTED_NOT_PROVISIONED);
        assertNotNull(ConformanceScenario.INVITE_TIMEOUT);
        assertNotNull(ConformanceScenario.PRECONDITION_FAILURE);
        assertNotNull(ConformanceScenario.RESOURCE_ALLOCATION_FAILURE);
        assertNotNull(ConformanceScenario.INCOMPATIBLE_MEDIA);
        assertNotNull(ConformanceScenario.BYE_TIMEOUT);
        assertNotNull(ConformanceScenario.ROUTING_FAILURE_USER_NOT_FOUND);
        assertNotNull(ConformanceScenario.ROUTING_FAILURE_NO_PATH);
        assertNotNull(ConformanceScenario.EMERGENCY_CALL_REJECTION);
        assertNotNull(ConformanceScenario.NONE);
    }

    @Test
    void testAffectedNodeDistribution() {
        // Count scenarios by affected node
        long pCscfCount = countByNode(ActorType.P_CSCF);
        long sCscfCount = countByNode(ActorType.S_CSCF);
        long hssCount = countByNode(ActorType.HSS);
        
        assertTrue(pCscfCount > 0, "Should have P-CSCF scenarios");
        assertTrue(sCscfCount > 0, "Should have S-CSCF scenarios");
        assertTrue(hssCount > 0, "Should have HSS scenarios");
    }

    private long countByNode(ActorType node) {
        long count = 0;
        for (ConformanceScenario scenario : ConformanceScenario.values()) {
            if (scenario.getAffectedNode() == node) {
                count++;
            }
        }
        return count;
    }
}
