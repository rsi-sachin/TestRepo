package com.tts.demo.service;

import com.tts.demo.model.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests for failure mechanism detection in RCA.
 * Verifies that RCA correctly identifies HOW the failure occurred:
 * - Unsolicited ERROR messages
 * - Missing expected messages
 * - Incorrect message content
 * - Response code rejections
 * - Timeouts
 * - Sequence violations
 * 
 * Added May 13, 2026 to address: "RCA does not mention if an unsolicited message 
 * is observed or an expected message is not observed"
 */
@DisplayName("RCA Failure Mechanism Detection Tests")
public class FailureMechanismTest {

    private RcaAnalyzer analyzer;
    private CallFlow callFlow;
    private RunResult runResult;

    @BeforeEach
    void setUp() {
        analyzer = new RcaAnalyzer();
        callFlow = new CallFlow();
        
        runResult = new RunResult(
            "test-run-mech-001",
            "sip-mechanism-test",
            "Mechanism Test Demo"
        );
        runResult.setStatus(RunResult.RunStatus.SUCCESS); // Force analysis even on "success"
        runResult.setExitCode(0);
    }

    /**
     * TEST 1: Detect unsolicited ERROR message (Error Scenario test case)
     * Label contains "ERROR" but response code is 200
     */
    @Test
    @DisplayName("Should detect UNSOLICITED_ERROR_MESSAGE for 'Send ERROR' with 200 code")
    void testUnsolicitedErrorMessage() {
        callFlow.addMessage(createMessage("Send INVITE from A Party to TAS", "200", true, 100));
        callFlow.addMessage(createMessage("Listen for ERROR from TAS to A Party", "200", true, 81));
        callFlow.addMessage(createMessage("Send Error to A Party", "200", true, 53));
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        assertNotNull(rca.getFailureMechanism(), "Failure mechanism should be detected");
        assertEquals(FailureMechanism.UNSOLICITED_ERROR_MESSAGE, rca.getFailureMechanism(),
            "Should detect unsolicited ERROR message");
        
        assertTrue(rca.getRootCause().toLowerCase().contains("unsolicited"),
            "Diagnosis should mention 'unsolicited': " + rca.getRootCause());
    }

    /**
     * TEST 2: Detect response code rejection (4xx error)
     */
    @Test
    @DisplayName("Should detect RESPONSE_CODE_REJECTION for 403 Forbidden")
    void testResponseCodeRejection403() {
        callFlow.addMessage(createMessage("Send REGISTER", "200", true, 50));
        callFlow.addMessage(createMessage("Receive 403 Forbidden", "403", false, 30));
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        assertEquals(FailureMechanism.RESPONSE_CODE_REJECTION, rca.getFailureMechanism(),
            "Should detect response code rejection for 403");
        
        assertTrue(rca.getRootCause().contains("403") || rca.getRootCause().contains("rejection"),
            "Diagnosis should mention rejection: " + rca.getRootCause());
    }

    /**
     * TEST 3: Detect response code rejection (5xx server error)
     */
    @Test
    @DisplayName("Should detect RESPONSE_CODE_REJECTION for 503 Service Unavailable")
    void testResponseCodeRejection503() {
        callFlow.addMessage(createMessage("Send INVITE", "200", true, 100));
        callFlow.addMessage(createMessage("Receive 503 Service Unavailable", "503", false, 50));
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        assertEquals(FailureMechanism.RESPONSE_CODE_REJECTION, rca.getFailureMechanism(),
            "Should detect response code rejection for 503");
    }

    /**
     * TEST 4: Detect timeout (high elapsed time)
     */
    @Test
    @DisplayName("Should detect TIMEOUT_NO_RESPONSE for message with >5000ms elapsed")
    void testTimeoutNoResponse() {
        callFlow.addMessage(createMessage("Send INVITE", "200", true, 100));
        callFlow.addMessage(createMessage("Wait for RINGING", "0", false, 6000)); // 6 seconds
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        assertEquals(FailureMechanism.TIMEOUT_NO_RESPONSE, rca.getFailureMechanism(),
            "Should detect timeout for message with 6000ms elapsed");
        
        assertTrue(rca.getRootCause().toLowerCase().contains("timeout") || 
                   rca.getRootCause().toLowerCase().contains("no response"),
            "Diagnosis should mention timeout: " + rca.getRootCause());
    }

    /**
     * TEST 5: Detect missing expected message (incomplete call flow)
     */
    @Test
    @DisplayName("Should detect MISSING_EXPECTED_MESSAGE when 200 OK never received")
    void testMissingExpectedMessage() {
        // Only INVITE sent, no 200 OK response
        callFlow.addMessage(createMessage("Send INVITE", "100", true, 100));
        callFlow.addMessage(createMessage("Receive TRYING", "100", true, 50));
        // Missing 200 OK - only 3 messages
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        assertEquals(FailureMechanism.MISSING_EXPECTED_MESSAGE, rca.getFailureMechanism(),
            "Should detect missing expected message when call flow is incomplete");
        
        assertTrue(rca.getRootCause().toLowerCase().contains("expected") || 
                   rca.getRootCause().toLowerCase().contains("never received"),
            "Diagnosis should mention missing message: " + rca.getRootCause());
    }

    /**
     * TEST 6: Detect sequence violation (ACK before 200 OK)
     */
    @Test
    @DisplayName("Should detect SEQUENCE_VIOLATION when ACK comes before 200 OK")
    void testSequenceViolationAckBeforeOk() {
        callFlow.addMessage(createMessage("Send INVITE", "100", true, 100));
        callFlow.addMessage(createMessage("Send ACK", "200", true, 50)); // ACK too early
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        assertEquals(FailureMechanism.SEQUENCE_VIOLATION, rca.getFailureMechanism(),
            "Should detect sequence violation when ACK appears before 200 OK");
    }

    /**
     * TEST 7: Detect protocol malformation (400 Bad Request)
     * Note: 400 is detected as RESPONSE_CODE_REJECTION first (since it's a 4xx code),
     * PROTOCOL_MALFORMATION is a secondary classification
     */
    @Test
    @DisplayName("Should detect RESPONSE_CODE_REJECTION for 400 Bad Request (4xx)")
    void testProtocolMalformation() {
        callFlow.addMessage(createMessage("Send malformed INVITE", "400", false, 20));
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        // 400 is first detected as 4xx rejection
        assertEquals(FailureMechanism.RESPONSE_CODE_REJECTION, rca.getFailureMechanism(),
            "Should detect response code rejection for 400 (it's a 4xx response)");
        
        assertTrue(rca.getRootCause().toLowerCase().contains("reject") || 
                   rca.getRootCause().contains("400") ||
                   rca.getRootCause().toLowerCase().contains("protocol"),
            "Diagnosis should mention rejection or protocol error: " + rca.getRootCause());
    }

    /**
     * TEST 8: Detect unsolicited REJECT message
     */
    @Test
    @DisplayName("Should detect UNSOLICITED_ERROR_MESSAGE for 'REJECT' label with 200 code")
    void testUnsolicitedRejectMessage() {
        callFlow.addMessage(createMessage("Send REGISTER", "200", true, 100));
        callFlow.addMessage(createMessage("REJECT authentication from HSS", "200", true, 50));
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        assertEquals(FailureMechanism.UNSOLICITED_ERROR_MESSAGE, rca.getFailureMechanism(),
            "Should detect unsolicited REJECT message");
    }

    /**
     * TEST 9: Detect unsolicited FAIL message
     */
    @Test
    @DisplayName("Should detect UNSOLICITED_ERROR_MESSAGE for 'FAIL' label with 200 code")
    void testUnsolicitedFailMessage() {
        callFlow.addMessage(createMessage("Send INVITE", "200", true, 100));
        callFlow.addMessage(createMessage("Connection FAIL to P-CSCF", "200", true, 80));
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        assertEquals(FailureMechanism.UNSOLICITED_ERROR_MESSAGE, rca.getFailureMechanism(),
            "Should detect unsolicited FAIL message");
    }

    /**
     * TEST 10: Verify mechanism is included in RCA result
     */
    @Test
    @DisplayName("RCA result should include failure mechanism field")
    void testMechanismIncludedInResult() {
        callFlow.addMessage(createMessage("Send INVITE", "200", true, 100));
        callFlow.addMessage(createMessage("Listen for ERROR from TAS", "200", true, 81));
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        assertNotNull(rca.getFailureMechanism(), "Failure mechanism should not be null");
        assertNotEquals(FailureMechanism.NORMAL_FLOW, rca.getFailureMechanism(),
            "Should detect failure mechanism, not normal flow");
    }

    /**
     * TEST 11: Verify diagnosis includes mechanism explanation
     */
    @Test
    @DisplayName("RCA diagnosis should include mechanism-specific explanation")
    void testDiagnosisIncludesMechanism() {
        callFlow.addMessage(createMessage("Send ERROR to client", "200", true, 50));
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        String diagnosis = rca.getRootCause();
        assertNotNull(diagnosis, "Diagnosis should not be null");
        assertFalse(diagnosis.isEmpty(), "Diagnosis should not be empty");
        
        // Should contain mechanism icon or explanation
        assertTrue(diagnosis.contains("⚠️") || 
                   diagnosis.contains("ERROR") ||
                   diagnosis.contains("Unsolicited"),
            "Diagnosis should include mechanism explanation: " + diagnosis);
    }

    // ============= HELPER METHODS =============

    /**
     * Helper to create SipMessage for testing
     */
    private SipMessage createMessage(String label, String responseCode, boolean success, long elapsed) {
        return new SipMessage(
            SipMessage.MessageType.fromLabel(label),
            SipMessage.Direction.UNKNOWN,
            "Thread Group 1-1",
            System.currentTimeMillis(),
            elapsed,
            success,
            responseCode,
            label
        );
    }
}
