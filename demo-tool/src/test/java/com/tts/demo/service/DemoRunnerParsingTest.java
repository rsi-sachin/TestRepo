package com.tts.demo.service;

import com.tts.demo.model.SipMessage;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for DemoRunner's JTL parsing and label filtering logic.
 * Tests the shouldSkipLabel() and parseJtlLine() methods using real JTL file patterns.
 */
class DemoRunnerParsingTest {

    @TempDir
    Path tempDir;

    private DemoRunner runner;

    @BeforeEach
    void setUp() {
        String runsPath = tempDir.resolve("runs").toString();
        ConfigManager configManager = new ConfigManager(runsPath);
        runner = new DemoRunner(configManager);
    }

    @Test
    void testShouldSkipLabel_ValidSipMessages() {
        // Valid SIP message labels should NOT be skipped
        assertFalse(runner.shouldSkipLabel("Send INVITE"));
        assertFalse(runner.shouldSkipLabel("Listen for TRYING from TAS to A Party"));
        assertFalse(runner.shouldSkipLabel("Send RINGING to A Party"));
        assertFalse(runner.shouldSkipLabel("Listen for OK from TAS to A Party"));
        assertFalse(runner.shouldSkipLabel("Send ACK from A party to TAS"));
        assertFalse(runner.shouldSkipLabel("Send BYE to TAS from B Party"));
    }

    @Test
    void testShouldSkipLabel_TimerMessages() {
        // Timer messages should be skipped
        assertTrue(runner.shouldSkipLabel("Short Delay"));
        assertTrue(runner.shouldSkipLabel("Long Delay"));
        assertTrue(runner.shouldSkipLabel("Timer successfully waited for 1000 miliseconds."));
    }

    @Test
    void testShouldSkipLabel_VariableExtractors() {
        // Variable extractor labels (starting with "A") should be skipped
        assertTrue(runner.shouldSkipLabel("ATo: sip:13880"));
        assertTrue(runner.shouldSkipLabel("AFrom: sip:13885@tts.example.com"));
        assertTrue(runner.shouldSkipLabel("AVia: SIP/2.0/UDP localhost:13885"));
        assertTrue(runner.shouldSkipLabel("ACallID: 172592996-893"));
    }

    @Test
    void testShouldSkipLabel_DebugSamplers() {
        // Debug sampler messages should be skipped
        assertTrue(runner.shouldSkipLabel("Debug Sampler - before call"));
        assertTrue(runner.shouldSkipLabel("Debug Sampler - after call"));
    }

    @Test
    void testShouldSkipLabel_StartingMessages() {
        // Starting messages should be skipped
        assertTrue(runner.shouldSkipLabel("Starting TAS SIM"));
        assertTrue(runner.shouldSkipLabel("Starting Client Thread"));
    }

    @Test
    void testShouldSkipLabel_GenerateMessages() {
        // Generate messages should be skipped
        assertTrue(runner.shouldSkipLabel("Generate and print CallId - 172592996-893"));
        assertTrue(runner.shouldSkipLabel("Generate and print CallId - 1798549979-48"));
    }

    @Test
    void testShouldSkipLabel_NullAndEmpty() {
        // Null and empty labels should be skipped
        assertTrue(runner.shouldSkipLabel(null));
        assertTrue(runner.shouldSkipLabel(""));
        assertTrue(runner.shouldSkipLabel("   "));
    }

    @Test
    void testParseJtlLine_ValidSipMessage() {
        // Real line from log_20260512_132734_sip-003.jtl
        String line = "1778572664084,54,Listen for TRYING from TAS to A Party,200,SIP Request received successfully.,Thread Group 2-1,text,true,,316,0,1,3,null,0,0,0";
        
        SipMessage msg = runner.parseJtlLine(line);
        
        assertNotNull(msg, "Should parse valid SIP message");
        assertEquals(SipMessage.MessageType.TRYING, msg.getMessageType());
        assertEquals(1778572664084L, msg.getTimestamp());
        assertEquals(54L, msg.getElapsed());
        assertEquals("Thread Group 2-1", msg.getThreadName());
        assertTrue(msg.isSuccess());
        assertEquals("200", msg.getResponseCode());
        assertEquals("Listen for TRYING from TAS to A Party", msg.getLabel());
    }

    @Test
    void testParseJtlLine_FilteredMessage() {
        // Timer message should be filtered out
        String line = "1778572662968,1007,Short Delay,200,Timer successfully waited for 1000 miliseconds.,Thread Group 2-1,text,true,,0,0,1,3,null,0,0,0";
        
        SipMessage msg = runner.parseJtlLine(line);
        
        assertNull(msg, "Timer message should be filtered");
    }

    @Test
    void testParseJtlLine_VariableExtractorFiltered() {
        // Variable extractor message should be filtered out
        String line = "1778572664110,0,ATo: sip:13880,2001,succes,Thread Group 1-1,text,true,,14,0,1,3,null,0,0,0";
        
        SipMessage msg = runner.parseJtlLine(line);
        
        assertNull(msg, "Variable extractor message should be filtered");
    }

    @Test
    void testParseJtlLine_MalformedLine() {
        // Malformed lines should return null gracefully
        String malformed1 = "invalid,line";
        String malformed2 = "1778572664084,54,Send INVITE"; // Only 3 fields, need 8+
        
        assertNull(runner.parseJtlLine(malformed1), "Malformed line with invalid numbers should return null");
        assertNull(runner.parseJtlLine(malformed2), "Line with insufficient fields should return null");
    }

    @Test
    void testParseJtlLine_NullAndEmpty() {
        // Null and empty lines should return null
        assertNull(runner.parseJtlLine(null), "Null line should return null");
        assertNull(runner.parseJtlLine(""), "Empty line should return null");
        assertNull(runner.parseJtlLine("   "), "Whitespace-only line should return null");
    }

    @Test
    void testParseJtlLine_AllSipMessageTypes() {
        // Test parsing different SIP message types
        String inviteLine = "1778572663980,104,Send INVITE from A party to TAS,200,SIP Response send successfully.,Thread Group 2-1,text,true,,354,0,1,3,null,0,0,8";
        String ringingLine = "1778572664201,20,Send RINGING to A Party,200,SIP Response send successfully.,Thread Group 1-1,text,true,,392,0,1,3,null,0,0,0";
        String okLine = "1778572664222,15,Send OK to A Party,200,SIP Response send successfully.,Thread Group 1-1,text,true,,387,0,1,3,null,0,0,0";
        String ackLine = "1778572664229,23,Send ACK from A party to TAS,200,SIP Response send successfully.,Thread Group 2-1,text,true,,388,0,1,3,null,0,0,0";
        String byeLine = "1778572664241,11,Send BYE to TAS from B Party,200,SIP Response send successfully.,Thread Group 3-1,text,true,,339,0,1,3,null,0,0,0";
        
        SipMessage inviteMsg = runner.parseJtlLine(inviteLine);
        SipMessage ringingMsg = runner.parseJtlLine(ringingLine);
        SipMessage okMsg = runner.parseJtlLine(okLine);
        SipMessage ackMsg = runner.parseJtlLine(ackLine);
        SipMessage byeMsg = runner.parseJtlLine(byeLine);
        
        assertNotNull(inviteMsg);
        assertEquals(SipMessage.MessageType.INVITE, inviteMsg.getMessageType());
        
        assertNotNull(ringingMsg);
        assertEquals(SipMessage.MessageType.RINGING, ringingMsg.getMessageType());
        
        assertNotNull(okMsg);
        assertEquals(SipMessage.MessageType.OK, okMsg.getMessageType());
        
        assertNotNull(ackMsg);
        assertEquals(SipMessage.MessageType.ACK, ackMsg.getMessageType());
        
        assertNotNull(byeMsg);
        assertEquals(SipMessage.MessageType.BYE, byeMsg.getMessageType());
    }
}
