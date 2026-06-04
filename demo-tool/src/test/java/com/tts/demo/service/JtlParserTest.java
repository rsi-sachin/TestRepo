package com.tts.demo.service;

import com.tts.demo.model.CallFlow;
import com.tts.demo.model.SipMessage;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class JtlParserTest {

    private JtlParser parser;
    private static final String BASELINE_JTL = "logs/phase1_success_baseline.jtl";

    @BeforeEach
    void setUp() {
        parser = new JtlParser();
    }

    @Test
    void testParseBaselineJtlFile() throws IOException {
        // Verify test file exists
        Path path = Paths.get(BASELINE_JTL);
        assertTrue(Files.exists(path), "Baseline JTL file should exist: " + BASELINE_JTL);
        
        // Parse the file
        CallFlow callFlow = parser.parseJtlFile(BASELINE_JTL);
        
        assertNotNull(callFlow, "CallFlow should not be null");
        assertTrue(callFlow.getTotalMessages() > 0, "Should parse at least one message");
    }

    @Test
    void testParsedMessageCount() throws IOException {
        CallFlow callFlow = parser.parseJtlFile(BASELINE_JTL);
        
        // Based on the baseline JTL, we expect specific SIP messages
        // (filtering out timers and utility messages)
        // Expected SIP messages: INVITE, TRYING, RINGING, OK, ACK, BYE exchanges
        assertTrue(callFlow.getTotalMessages() >= 10, 
                "Should parse at least 10 SIP messages (actual: " + callFlow.getTotalMessages() + ")");
    }

    @Test
    void testMessageTypesDetected() throws IOException {
        CallFlow callFlow = parser.parseJtlFile(BASELINE_JTL);
        List<SipMessage> messages = callFlow.getMessages();
        
        // Verify we have different message types
        boolean hasInvite = messages.stream()
                .anyMatch(m -> m.getMessageType() == SipMessage.MessageType.INVITE);
        boolean hasTrying = messages.stream()
                .anyMatch(m -> m.getMessageType() == SipMessage.MessageType.TRYING);
        boolean hasRinging = messages.stream()
                .anyMatch(m -> m.getMessageType() == SipMessage.MessageType.RINGING);
        boolean hasOk = messages.stream()
                .anyMatch(m -> m.getMessageType() == SipMessage.MessageType.OK);
        boolean hasAck = messages.stream()
                .anyMatch(m -> m.getMessageType() == SipMessage.MessageType.ACK);
        boolean hasBye = messages.stream()
                .anyMatch(m -> m.getMessageType() == SipMessage.MessageType.BYE);
        
        assertTrue(hasInvite, "Should detect INVITE message");
        assertTrue(hasTrying, "Should detect TRYING message");
        assertTrue(hasRinging, "Should detect RINGING message");
        assertTrue(hasOk, "Should detect OK message");
        assertTrue(hasAck, "Should detect ACK message");
        assertTrue(hasBye, "Should detect BYE message");
    }

    @Test
    void testDirectionAssignment() throws IOException {
        CallFlow callFlow = parser.parseJtlFile(BASELINE_JTL);
        List<SipMessage> messages = callFlow.getMessages();
        
        // Verify direction is properly assigned
        long clientToServer = messages.stream()
                .filter(m -> m.getDirection() == SipMessage.Direction.CLIENT_TO_SERVER)
                .count();
        long serverToClient = messages.stream()
                .filter(m -> m.getDirection() == SipMessage.Direction.SERVER_TO_CLIENT)
                .count();
        
        assertTrue(clientToServer > 0, "Should have client-to-server messages");
        assertTrue(serverToClient > 0, "Should have server-to-client messages");
    }

    @Test
    void testCallFlowAnalysis() throws IOException {
        CallFlow callFlow = parser.parseJtlFile(BASELINE_JTL);
        
        // Baseline test should show a completed call
        assertTrue(callFlow.isCallCompleted(), 
                "Baseline test should show completed call flow");
        
        // All messages should be successful
        assertEquals(callFlow.getTotalMessages(), callFlow.getSuccessfulMessages(),
                "All messages in baseline should be successful");
        
        // Success rate should be 100%
        assertEquals(100.0, callFlow.getSuccessRate(), 0.01,
                "Success rate should be 100%");
    }

    @Test
    void testClientAndServerMessages() throws IOException {
        CallFlow callFlow = parser.parseJtlFile(BASELINE_JTL);
        
        List<SipMessage> clientMessages = callFlow.getClientMessages();
        List<SipMessage> serverMessages = callFlow.getServerMessages();
        
        assertFalse(clientMessages.isEmpty(), "Should have client messages");
        assertFalse(serverMessages.isEmpty(), "Should have server messages");
        
        // Total should equal all messages
        assertEquals(callFlow.getTotalMessages(), 
                clientMessages.size() + serverMessages.size(),
                "Client + Server messages should equal total");
    }

    @Test
    void testMessagesByType() throws IOException {
        CallFlow callFlow = parser.parseJtlFile(BASELINE_JTL);
        
        List<SipMessage> inviteMessages = callFlow.getMessagesByType(SipMessage.MessageType.INVITE);
        List<SipMessage> okMessages = callFlow.getMessagesByType(SipMessage.MessageType.OK);
        
        assertFalse(inviteMessages.isEmpty(), "Should have INVITE messages");
        assertFalse(okMessages.isEmpty(), "Should have OK messages");
        
        // Verify message details
        for (SipMessage invite : inviteMessages) {
            assertEquals(SipMessage.MessageType.INVITE, invite.getMessageType());
            assertTrue(invite.isSuccess(), "INVITE should be successful in baseline");
        }
    }

    @Test
    void testFailedMessages() throws IOException {
        CallFlow callFlow = parser.parseJtlFile(BASELINE_JTL);
        
        List<SipMessage> failedMessages = callFlow.getFailedMessages();
        
        // Baseline test should have no failures
        assertTrue(failedMessages.isEmpty(), 
                "Baseline test should have no failed messages");
    }

    @Test
    void testTotalDuration() throws IOException {
        CallFlow callFlow = parser.parseJtlFile(BASELINE_JTL);
        
        // Duration should be positive (measured in milliseconds)
        assertTrue(callFlow.getTotalDuration() > 0, 
                "Call duration should be positive");
        
        // Reasonable duration for a VoLTE test (should be several seconds)
        assertTrue(callFlow.getTotalDuration() > 1000, 
                "Call duration should be at least 1 second");
    }

    @Test
    void testNonExistentFile() {
        String nonExistentFile = "logs/nonexistent.jtl";
        
        assertThrows(IOException.class, () -> {
            parser.parseJtlFile(nonExistentFile);
        }, "Should throw IOException for non-existent file");
    }

    @Test
    void testMessageFields() throws IOException {
        CallFlow callFlow = parser.parseJtlFile(BASELINE_JTL);
        List<SipMessage> messages = callFlow.getMessages();
        
        assertFalse(messages.isEmpty(), "Should have messages");
        
        // Verify first message has valid fields
        SipMessage firstMessage = messages.get(0);
        assertNotNull(firstMessage.getMessageType(), "Message type should not be null");
        assertNotNull(firstMessage.getDirection(), "Direction should not be null");
        assertNotNull(firstMessage.getThreadName(), "Thread name should not be null");
        assertTrue(firstMessage.getTimestamp() > 0, "Timestamp should be positive");
        assertTrue(firstMessage.getElapsed() >= 0, "Elapsed time should be non-negative");
        assertNotNull(firstMessage.getResponseCode(), "Response code should not be null");
        assertNotNull(firstMessage.getLabel(), "Label should not be null");
    }

    @Test
    void testToStringMethod() throws IOException {
        CallFlow callFlow = parser.parseJtlFile(BASELINE_JTL);
        
        String callFlowString = callFlow.toString();
        assertNotNull(callFlowString);
        assertTrue(callFlowString.contains("totalMessages="));
        assertTrue(callFlowString.contains("successfulMessages="));
        assertTrue(callFlowString.contains("callCompleted="));
        assertTrue(callFlowString.contains("totalDuration="));
    }
}
