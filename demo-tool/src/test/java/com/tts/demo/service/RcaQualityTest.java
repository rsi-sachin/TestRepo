package com.tts.demo.service;

import com.tts.demo.model.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * REGRESSION TESTS for RCA quality issues reported on May 13, 2026:
 * 1. "Unknown Failure Failure at ACK Send" - repeated "Failure" text
 * 2. "Affected Node: Unknown Node" - should extract from label
 * 3. "Communication Direction: Unknown" - should parse from SIP message labels
 * 
 * These tests ensure RCA output is high quality and doesn't regress.
 */
@DisplayName("RCA Quality Regression Tests (May 13, 2026 bugs)")
public class RcaQualityTest {

    private RcaAnalyzer analyzer;
    private CallFlow callFlow;
    private RunResult runResult;

    @BeforeEach
    void setUp() {
        analyzer = new RcaAnalyzer();
        callFlow = new CallFlow();
        
        runResult = new RunResult(
            "test-run-001",
            "sip-rca",
            "RCA Test Demo"
        );
        runResult.setStatus(RunResult.RunStatus.FAILED);
        runResult.setExitCode(1);
    }

    /**
     * REGRESSION BUG #1: "Unknown Failure Failure" - word "Failure" repeated
     * Root cause: String.format("%s failure occurred at %s", type.getDisplayName(), point.getDisplayName())
     * where type.getDisplayName() = "Unknown Failure" already contains "Failure"
     */
    @Test
    @DisplayName("RCA diagnosis should NOT contain repeated 'Failure' text")
    void testNoDuplicateFailureText() {
        // Create a message that will trigger UNKNOWN failure type
        SipMessage msg = createMessage("Listen for ACK", "0", false, 100);
        callFlow.addMessage(msg);
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        String diagnosis = rca.getRootCause().toLowerCase();
        
        // Count occurrences of "failure"
        int count = 0;
        int index = 0;
        while ((index = diagnosis.indexOf("failure", index)) != -1) {
            count++;
            index++;
        }
        
        assertTrue(count <= 1, 
            "Diagnosis should not repeat 'failure': " + rca.getRootCause());
    }

    /**
     * REGRESSION BUG #2: "Affected Node: Unknown Node"
     * Root cause: Actor extraction only looked at thread names, not labels
     * Fix: Extract actors from labels like "Send ERROR from TAS to A Party"
     */
    @Test
    @DisplayName("RCA should extract affected node from 'Send ERROR from TAS to A Party' label")
    void testAffectedNodeFromLabelSendError() {
        SipMessage msg = createMessage("Send Error to A Party", "200", true, 50);
        callFlow.addMessage(createMessage("INVITE", "200", true, 100));
        callFlow.addMessage(msg); // Failed message
        
        runResult.setStatus(RunResult.RunStatus.SUCCESS); // Force RCA to analyze
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        String affectedNode = rca.getAffectedNode();
        
        assertNotNull(affectedNode, "Affected node should not be null");
        assertFalse(affectedNode.equals("Unknown Node"), 
            "Should extract 'UE (Client)' from label, got: " + affectedNode);
        assertTrue(affectedNode.contains("UE") || affectedNode.contains("Client"), 
            "Should identify A Party as UE Client, got: " + affectedNode);
    }

    /**
     * REGRESSION BUG #2 continued: Extract from "Listen for ERROR from TAS to A Party"
     */
    @Test
    @DisplayName("RCA should extract affected node from 'Listen for ERROR from TAS' label")
    void testAffectedNodeFromLabelListenError() {
        SipMessage msg = createMessage("Listen for ERROR from TAS to A Party", "200", true, 80);
        callFlow.addMessage(createMessage("INVITE", "200", true, 100));
        callFlow.addMessage(msg);
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        String affectedNode = rca.getAffectedNode();
        
        assertNotNull(affectedNode, "Affected node should not be null");
        assertTrue(affectedNode.contains("UE") || affectedNode.contains("TAS") || affectedNode.contains("Client"), 
            "Should extract actor from 'Listen for ERROR from TAS to A Party', got: " + affectedNode);
    }

    /**
     * REGRESSION BUG #2 continued: Actor extraction from "Send INVITE from A Party to TAS"
     */
    @Test
    @DisplayName("RCA should extract actors from 'Send INVITE from A Party to TAS' label")
    void testActorExtractionFromToPattern() {
        SipMessage msg = createMessage("Send INVITE from A Party to TAS", "200", true, 100);
        callFlow.addMessage(msg);
        
        // Check that actors are extracted correctly
        assertEquals(ActorType.UE_CLIENT, msg.getSourceActor(), 
            "Should extract 'A Party' as UE_CLIENT from label");
        assertEquals(ActorType.TAS, msg.getTargetActor(), 
            "Should extract 'TAS' as TAS from label");
    }

    /**
     * REGRESSION BUG #3: "Communication Direction: Unknown"
     * Root cause: Direction not extracted from label, only from thread name
     * Fix: Enhanced direction parsing in evidence building
     */
    @Test
    @DisplayName("RCA evidence should show specific actors, not 'Unknown' direction")
    void testCommunicationDirectionNotUnknown() {
        SipMessage msg = createMessage("Send INVITE from A Party to TAS", "403", false, 100);
        callFlow.addMessage(msg);
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        // Check evidence list
        String evidenceStr = String.join("; ", rca.getEvidence());
        
        assertFalse(evidenceStr.contains("Unknown"), 
            "Evidence should not contain 'Unknown' direction, got: " + evidenceStr);
        assertTrue(evidenceStr.contains("→") || evidenceStr.contains("UE") || evidenceStr.contains("TAS"), 
            "Evidence should show specific actors, got: " + evidenceStr);
    }

    /**
     * Test that ActorType.fromLabel() correctly extracts actors from various label formats
     */
    @Test
    @DisplayName("ActorType.fromLabel should parse various label patterns")
    void testActorTypeFromLabelParsing() {
        // Pattern: "from X to Y"
        assertEquals(ActorType.TAS, ActorType.fromLabel("Send ERROR from TAS to A Party"), 
            "Should extract TAS from 'from TAS to'");
        
        assertEquals(ActorType.UE_CLIENT, ActorType.fromLabel("Send INVITE from A Party to TAS"), 
            "Should extract A Party as UE_CLIENT");
        
        // Pattern: "to X"
        assertEquals(ActorType.UE_CLIENT, ActorType.fromLabel("Send Error to A Party"), 
            "Should extract A Party from 'to A Party'");
        
        // Pattern: actor name in text
        assertEquals(ActorType.TAS, ActorType.fromLabel("TAS initialization"), 
            "Should detect TAS in label");
        
        assertEquals(ActorType.P_CSCF, ActorType.fromLabel("P-CSCF routing"), 
            "Should detect P-CSCF in label");
    }

    /**
     * Test SipMessage actor extraction with real-world Error Scenario label
     */
    @Test
    @DisplayName("SipMessage should extract actors from Error Scenario test labels")
    void testSipMessageActorExtractionErrorScenario() {
        // Real label from Error Scenario test
        SipMessage msg = new SipMessage(
            SipMessage.MessageType.OTHER,
            SipMessage.Direction.UNKNOWN,
            "Thread Group 1-1",
            System.currentTimeMillis(),
            81,
            true,
            "200",
            "Listen for ERROR from TAS to A Party"
        );
        
        // Should extract TAS as source
        assertNotEquals(ActorType.UNKNOWN, msg.getSourceActor(), 
            "Should extract source actor from label, got: " + msg.getSourceActor());
        
        // Should extract A Party as target
        assertNotEquals(ActorType.UNKNOWN, msg.getTargetActor(), 
            "Should extract target actor from label, got: " + msg.getTargetActor());
        
        assertTrue(msg.getSourceActor() == ActorType.TAS, 
            "Source should be TAS, got: " + msg.getSourceActor());
        
        assertTrue(msg.getTargetActor() == ActorType.UE_CLIENT, 
            "Target should be UE_CLIENT (A Party), got: " + msg.getTargetActor());
    }

    /**
     * Test that RCA output quality is high (no "Unknown Unknown" patterns)
     */
    @Test
    @DisplayName("RCA output should not contain double 'Unknown' patterns")
    void testNoDoubleUnknownPatterns() {
        SipMessage msg = createMessage("Send Error to A Party", "200", true, 50);
        callFlow.addMessage(msg);
        
        RcaResult rca = analyzer.analyze(runResult, callFlow);
        
        String fullOutput = String.format("%s | %s | %s | %s", 
            rca.getRootCause(), 
            rca.getAffectedNode(), 
            rca.getFailurePoint().getDisplayName(),
            String.join("; ", rca.getEvidence()));
        
        assertFalse(fullOutput.contains("Unknown Unknown"), 
            "RCA output should not have double 'Unknown': " + fullOutput);
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
