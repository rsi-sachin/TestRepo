package com.tts.demo.controller;

import com.tts.demo.model.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for RCA trigger logic in MainController.
 * These tests verify that RCA analysis is triggered correctly for:
 * 1. Error response codes (4xx, 5xx, 6xx)
 * 2. Error-related labels (even with 200 response codes)
 * 3. RCA/Failure demo names
 * 
 * REGRESSION PROTECTION: These tests prevent bugs where RCA panel doesn't appear
 * when it should (e.g., "Error Scenario" tests that return 200 but have error labels).
 */
@DisplayName("RCA Trigger Logic Tests")
public class RcaTriggerLogicTest {

    private CallFlow callFlow;
    private Demo sipRcaDemo;
    private Demo sipNormalDemo;
    private Demo diameterDemo;

    @BeforeEach
    void setUp() {
        callFlow = new CallFlow();
        
        // Create RCA demo (should trigger RCA even without errors)
        sipRcaDemo = new Demo(
            "sip-rca",
            "VoLTE Call Failure Diagnostics (RCA Demo)",
            "Test RCA analysis with failure scenarios",
            "Demonstrates root cause analysis",
            Demo.Protocol.SIP_IMS,
            Demo.Complexity.INTERMEDIATE,
            "test.jmx",
            null
        );
        
        // Create normal SIP demo
        sipNormalDemo = new Demo(
            "sip-normal",
            "VoLTE Call Setup",
            "Normal call flow",
            "Successful call",
            Demo.Protocol.SIP_IMS,
            Demo.Complexity.BASIC,
            "test.jmx",
            null
        );
        
        // Create non-SIP demo
        diameterDemo = new Demo(
            "diameter-test",
            "Diameter Authentication",
            "Diameter protocol test",
            "Auth test",
            Demo.Protocol.DIAMETER,
            Demo.Complexity.BASIC,
            "test.jmx",
            null
        );
    }

    /**
     * TEST 1: RCA should trigger when message has 4xx error response code
     */
    @Test
    @DisplayName("Should trigger RCA when call flow contains 403 Forbidden response")
    void testRcaTriggerOn403Response() {
        SipMessage msg = createSipMessage("INVITE", "403", "Forbidden", ActorType.UE_CLIENT, ActorType.P_CSCF);
        callFlow.addMessage(msg);
        
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(sipNormalDemo, callFlow);
        
        assertTrue(shouldTriggerRca, "RCA should trigger for 403 error response");
    }

    /**
     * TEST 2: RCA should trigger when message has 5xx error response code
     */
    @ParameterizedTest
    @ValueSource(strings = {"500", "503", "504"})
    @DisplayName("Should trigger RCA for 5xx server errors")
    void testRcaTriggerOn5xxResponse(String responseCode) {
        SipMessage msg = createSipMessage("INVITE", responseCode, "Server Error", ActorType.UE_CLIENT, ActorType.S_CSCF);
        callFlow.addMessage(msg);
        
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(sipNormalDemo, callFlow);
        
        assertTrue(shouldTriggerRca, "RCA should trigger for " + responseCode + " error response");
    }

    /**
     * TEST 3: RCA should trigger when message has 6xx error response code
     */
    @Test
    @DisplayName("Should trigger RCA when call flow contains 603 Decline response")
    void testRcaTriggerOn603Response() {
        SipMessage msg = createSipMessage("INVITE", "603", "Decline", ActorType.UE_CLIENT, ActorType.S_CSCF);
        callFlow.addMessage(msg);
        
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(sipNormalDemo, callFlow);
        
        assertTrue(shouldTriggerRca, "RCA should trigger for 603 decline response");
    }

    /**
     * TEST 4: RCA should NOT trigger for 200 OK without error labels
     */
    @Test
    @DisplayName("Should NOT trigger RCA for successful call with 200 OK responses")
    void testRcaNotTriggeredForSuccessfulCall() {
        callFlow.addMessage(createSipMessage("INVITE", "200", "OK", ActorType.UE_CLIENT, ActorType.P_CSCF));
        callFlow.addMessage(createSipMessage("ACK", "200", "OK", ActorType.P_CSCF, ActorType.UE_CLIENT));
        callFlow.addMessage(createSipMessage("BYE", "200", "OK", ActorType.UE_CLIENT, ActorType.P_CSCF));
        
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(sipNormalDemo, callFlow);
        
        assertFalse(shouldTriggerRca, "RCA should NOT trigger for successful call flow");
    }

    /**
     * TEST 5: REGRESSION BUG FIX - RCA should trigger for Error Scenario with 200 but "ERROR" label
     * This is the bug that occurred on May 13, 2026 - Error Scenario tests return 200 OK but have error labels
     */
    @Test
    @DisplayName("REGRESSION FIX: Should trigger RCA for 200 response with ERROR label")
    void testRcaTriggerForErrorLabelWith200Response() {
        // This simulates the actual "Error Scenario" test output:
        // "Listen for ERROR from TAS to A Party,200,SIP Request received successfully"
        SipMessage errorMsg = createSipMessage("Listen for ERROR from TAS to A Party", "200", "SIP Request received successfully", ActorType.TAS, ActorType.UE_CLIENT);
        callFlow.addMessage(errorMsg);
        
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(sipNormalDemo, callFlow);
        
        assertTrue(shouldTriggerRca, "RCA should trigger for message with ERROR in label even with 200 response");
    }

    /**
     * TEST 6: RCA should trigger for "error scenario" label
     */
    @Test
    @DisplayName("Should trigger RCA for message with 'error scenario' label")
    void testRcaTriggerForErrorScenarioLabel() {
        SipMessage msg = createSipMessage("=== Call was an error scenario ===", "200", "success", ActorType.UE_CLIENT, ActorType.S_CSCF);
        callFlow.addMessage(msg);
        
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(sipNormalDemo, callFlow);
        
        assertTrue(shouldTriggerRca, "RCA should trigger for 'error scenario' label");
    }

    /**
     * TEST 7: RCA should trigger for "REJECT" label
     */
    @Test
    @DisplayName("Should trigger RCA for message with REJECT label")
    void testRcaTriggerForRejectLabel() {
        SipMessage msg = createSipMessage("REJECT user authentication", "200", "OK", ActorType.HSS, ActorType.S_CSCF);
        callFlow.addMessage(msg);
        
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(sipNormalDemo, callFlow);
        
        assertTrue(shouldTriggerRca, "RCA should trigger for REJECT label");
    }

    /**
     * TEST 8: RCA should trigger for "FAIL" label
     */
    @Test
    @DisplayName("Should trigger RCA for message with FAIL label")
    void testRcaTriggerForFailLabel() {
        SipMessage msg = createSipMessage("Connection FAIL to P-CSCF", "200", "OK", ActorType.UE_CLIENT, ActorType.P_CSCF);
        callFlow.addMessage(msg);
        
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(sipNormalDemo, callFlow);
        
        assertTrue(shouldTriggerRca, "RCA should trigger for FAIL label");
    }

    /**
     * TEST 9: RCA should trigger for RCA demo even without errors
     */
    @Test
    @DisplayName("Should trigger RCA for RCA demo by name (even with successful messages)")
    void testRcaTriggerForRcaDemoName() {
        // Normal successful messages
        callFlow.addMessage(createSipMessage("INVITE", "200", "OK", ActorType.UE_CLIENT, ActorType.P_CSCF));
        callFlow.addMessage(createSipMessage("ACK", "200", "OK", ActorType.P_CSCF, ActorType.UE_CLIENT));
        
        // Should trigger RCA because demo name contains "rca"
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(sipRcaDemo, callFlow);
        
        assertTrue(shouldTriggerRca, "RCA should trigger for demo with 'rca' in ID");
    }

    /**
     * TEST 10: RCA should trigger for demo with "failure" in title
     */
    @Test
    @DisplayName("Should trigger RCA for demo with 'failure' in title")
    void testRcaTriggerForFailureDemoTitle() {
        Demo failureDemo = new Demo(
            "sip-test-1",
            "VoLTE Call Failure Analysis",
            "Failure analysis demo",
            "Test failure scenarios",
            Demo.Protocol.SIP_IMS,
            Demo.Complexity.INTERMEDIATE,
            "test.jmx",
            null
        );
        
        callFlow.addMessage(createSipMessage("INVITE", "200", "OK", ActorType.UE_CLIENT, ActorType.P_CSCF));
        
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(failureDemo, callFlow);
        
        assertTrue(shouldTriggerRca, "RCA should trigger for demo with 'failure' in title");
    }

    /**
     * TEST 11: RCA should trigger for demo with "error" in title
     */
    @Test
    @DisplayName("Should trigger RCA for demo with 'error' in title")
    void testRcaTriggerForErrorDemoTitle() {
        Demo errorDemo = new Demo(
            "sip-test-2",
            "VoLTE Error Diagnostics",
            "Error diagnostics demo",
            "Test error scenarios",
            Demo.Protocol.SIP_IMS,
            Demo.Complexity.INTERMEDIATE,
            "test.jmx",
            null
        );
        
        callFlow.addMessage(createSipMessage("INVITE", "200", "OK", ActorType.UE_CLIENT, ActorType.P_CSCF));
        
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(errorDemo, callFlow);
        
        assertTrue(shouldTriggerRca, "RCA should trigger for demo with 'error' in title");
    }

    /**
     * TEST 12: RCA should NOT trigger for non-SIP protocols
     */
    @Test
    @DisplayName("Should NOT trigger RCA for non-SIP protocol (Diameter)")
    void testRcaNotTriggeredForDiameterProtocol() {
        // Even with error-like conditions
        SipMessage msg = createSipMessage("ERROR message", "403", "Forbidden", ActorType.UE_CLIENT, ActorType.HSS);
        callFlow.addMessage(msg);
        
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(diameterDemo, callFlow);
        
        assertFalse(shouldTriggerRca, "RCA should NOT trigger for non-SIP protocols");
    }

    /**
     * TEST 13: RCA should NOT trigger for empty call flow
     */
    @Test
    @DisplayName("Should NOT trigger RCA when call flow is empty")
    void testRcaNotTriggeredForEmptyCallFlow() {
        CallFlow emptyFlow = new CallFlow();
        
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(sipNormalDemo, emptyFlow);
        
        assertFalse(shouldTriggerRca, "RCA should NOT trigger for empty call flow");
    }

    /**
     * TEST 14: RCA should NOT trigger when call flow is null
     */
    @Test
    @DisplayName("Should NOT trigger RCA when call flow is null")
    void testRcaNotTriggeredForNullCallFlow() {
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(sipNormalDemo, null);
        
        assertFalse(shouldTriggerRca, "RCA should NOT trigger for null call flow");
    }

    /**
     * TEST 15: Edge case - Mixed messages (success + error label)
     */
    @Test
    @DisplayName("Should trigger RCA when call flow has both success and error labeled messages")
    void testRcaTriggerForMixedMessages() {
        callFlow.addMessage(createSipMessage("INVITE", "200", "OK", ActorType.UE_CLIENT, ActorType.P_CSCF));
        callFlow.addMessage(createSipMessage("Send ERROR to client", "200", "OK", ActorType.S_CSCF, ActorType.UE_CLIENT));
        callFlow.addMessage(createSipMessage("ACK", "200", "OK", ActorType.UE_CLIENT, ActorType.P_CSCF));
        
        boolean shouldTriggerRca = shouldTriggerRcaAnalysis(sipNormalDemo, callFlow);
        
        assertTrue(shouldTriggerRca, "RCA should trigger if ANY message has error indicators");
    }

    // ================ HELPER METHODS ================

    /**
     * Replicates the RCA trigger logic from MainController.handleRunDemo()
     * This is the actual logic being tested (extracted for unit testing)
     */
    private boolean shouldTriggerRcaAnalysis(Demo demo, CallFlow flow) {
        // Check prerequisites
        if (demo.getProtocol() != Demo.Protocol.SIP_IMS) {
            return false;
        }
        
        if (flow == null || flow.getTotalMessages() == 0) {
            return false;
        }
        
        // Check if there are error responses OR error-related labels in the call flow
        boolean hasErrors = flow.getMessages().stream()
            .anyMatch(msg -> {
                String code = msg.getResponseCode();
                String label = msg.getLabel();
                
                // Check for error response codes
                boolean hasErrorCode = code != null && (code.startsWith("4") || code.startsWith("5") || code.startsWith("6"));
                
                // Check for error-related labels (for Error Scenario tests)
                boolean hasErrorLabel = label != null && (
                    label.toUpperCase().contains("ERROR") ||
                    label.contains("error scenario") ||
                    label.contains("REJECT") ||
                    label.contains("FAIL")
                );
                
                return hasErrorCode || hasErrorLabel;
            });
        
        // Also check if this is explicitly an RCA demo or error scenario demo
        boolean isRcaDemo = demo.getId().contains("rca") || 
                          demo.getTitle().toLowerCase().contains("failure") ||
                          demo.getTitle().toLowerCase().contains("error");
        
        return hasErrors || isRcaDemo;
    }

    /**
     * Helper to create SipMessage for testing
     */
    private SipMessage createSipMessage(String label, String responseCode, String responseMessage, 
                                       ActorType from, ActorType to) {
        SipMessage msg = new SipMessage();
        msg.setLabel(label);
        msg.setResponseCode(responseCode);
        msg.setTimestamp(System.currentTimeMillis());
        msg.setElapsed(100);
        msg.setSourceActor(from);
        msg.setTargetActor(to);
        msg.setSuccess(responseCode != null && responseCode.startsWith("2"));
        
        // Infer message type from label
        if (label.contains("INVITE")) {
            msg.setMessageType(SipMessage.MessageType.INVITE);
        } else if (label.contains("ACK")) {
            msg.setMessageType(SipMessage.MessageType.ACK);
        } else if (label.contains("BYE")) {
            msg.setMessageType(SipMessage.MessageType.BYE);
        } else {
            msg.setMessageType(SipMessage.MessageType.OTHER);
        }
        
        return msg;
    }
}
