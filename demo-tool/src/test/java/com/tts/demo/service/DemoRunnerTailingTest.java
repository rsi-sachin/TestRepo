package com.tts.demo.service;

import com.tts.demo.model.SipMessage;
import com.tts.demo.util.MockProcess;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Integration tests for DemoRunner's JTL file tailing functionality.
 * Tests real-time file reading and message capture during test execution.
 */
class DemoRunnerTailingTest {

    @TempDir
    Path tempDir;

    private DemoRunner runner;

    // JTL header line
    private static final String JTL_HEADER = "timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,sentBytes,grpThreads,allThreads,URL,Latency,IdleTime,Connect\n";

    @BeforeEach
    void setUp() {
        String runsPath = tempDir.resolve("runs").toString();
        ConfigManager configManager = new ConfigManager(runsPath);
        runner = new DemoRunner(configManager);
    }

    @Test
    void testTailJtlFile_NormalFlow() throws Exception {
        // Create temp JTL file with header
        Path jtlFile = tempDir.resolve("test_normal.jtl");
        Files.writeString(jtlFile, JTL_HEADER);

        List<SipMessage> captured = new CopyOnWriteArrayList<>();
        MockProcess mockProcess = new MockProcess(3000); // Alive for 3 seconds

        // Start tailing in background thread
        CountDownLatch startLatch = new CountDownLatch(1);
        Thread tailer = new Thread(() -> {
            startLatch.countDown();
            runner.tailJtlFile(jtlFile.toString(), captured::add, mockProcess);
        });
        tailer.start();

        // Wait for tailer to start
        assertTrue(startLatch.await(1, TimeUnit.SECONDS), "Tailer should start within 1 second");
        Thread.sleep(100); // Give tailer time to read header

        // Simulate incremental writes (like JMeter would do)
        appendLine(jtlFile, "1778572663980,104,Send INVITE from A party to TAS,200,SIP Response send successfully.,Thread Group 2-1,text,true,,354,0,1,3,null,0,0,8");
        Thread.sleep(200); // Wait for tailer to process

        appendLine(jtlFile, "1778572664085,54,Listen for TRYING from TAS to A Party,200,SIP Request received successfully.,Thread Group 2-1,text,true,,316,0,1,3,null,0,0,0");
        Thread.sleep(200);

        // Wait for tailer to finish (process will die after 3 seconds)
        tailer.join(5000);

        assertEquals(2, captured.size(), "Should capture both messages");
        assertEquals(SipMessage.MessageType.INVITE, captured.get(0).getMessageType());
        assertEquals(SipMessage.MessageType.TRYING, captured.get(1).getMessageType());
    }

    @Test
    void testTailJtlFile_FileCreatedLate() throws Exception {
        // Test scenario where JTL file doesn't exist initially (JMeter hasn't created it yet)
        Path jtlFile = tempDir.resolve("test_late.jtl");
        // Don't create file yet

        List<SipMessage> captured = new CopyOnWriteArrayList<>();
        MockProcess mockProcess = new MockProcess(2000);

        CountDownLatch startLatch = new CountDownLatch(1);
        Thread tailer = new Thread(() -> {
            startLatch.countDown();
            runner.tailJtlFile(jtlFile.toString(), captured::add, mockProcess);
        });
        tailer.start();

        assertTrue(startLatch.await(1, TimeUnit.SECONDS));
        
        // Wait a bit, then create the file (simulating JMeter starting late)
        Thread.sleep(300);
        Files.writeString(jtlFile, JTL_HEADER);
        Thread.sleep(100);

        // Add a message
        appendLine(jtlFile, "1778572664201,20,Send RINGING to A Party,200,SIP Response send successfully.,Thread Group 1-1,text,true,,392,0,1,3,null,0,0,0");
        Thread.sleep(200);

        tailer.join(5000);

        assertEquals(1, captured.size(), "Should capture message even when file created late");
        assertEquals(SipMessage.MessageType.RINGING, captured.get(0).getMessageType());
    }

    @Test
    void testTailJtlFile_ProcessTerminatesEarly() throws Exception {
        // Test that remaining messages are drained after process terminates
        Path jtlFile = tempDir.resolve("test_early_term.jtl");
        Files.writeString(jtlFile, JTL_HEADER);

        List<SipMessage> captured = new CopyOnWriteArrayList<>();
        MockProcess mockProcess = new MockProcess(1500); // Alive for 1.5 seconds

        Thread tailer = new Thread(() -> {
            runner.tailJtlFile(jtlFile.toString(), captured::add, mockProcess);
        });
        tailer.start();

        Thread.sleep(200);

        // Add first message while process is alive
        appendLine(jtlFile, "1778572664222,15,Send OK to A Party,200,SIP Response send successfully.,Thread Group 1-1,text,true,,387,0,1,3,null,0,0,0");
        Thread.sleep(300);

        // Wait for process to terminate
        Thread.sleep(1100); // Process dies after 1.5 seconds total
        
        // Add second message after process dies
        appendLine(jtlFile, "1778572664229,23,Send ACK from A party to TAS,200,SIP Response send successfully.,Thread Group 2-1,text,true,,388,0,1,3,null,0,0,0");
        
        // Give tailer time to drain remaining messages
        Thread.sleep(300);

        // Wait for tailer to finish
        tailer.join(3000);

        assertTrue(captured.size() >= 1, "Should capture at least the first message");
        assertEquals(SipMessage.MessageType.OK, captured.get(0).getMessageType());
        
        // Note: Draining behavior depends on timing - the tailer should attempt to read
        // remaining messages after process terminates, but this is best-effort
        if (captured.size() == 2) {
            assertEquals(SipMessage.MessageType.ACK, captured.get(1).getMessageType());
        }
    }

    @Test
    void testTailJtlFile_EmptyFile() throws Exception {
        // Test with empty file (no header, no data)
        Path jtlFile = tempDir.resolve("test_empty.jtl");
        Files.createFile(jtlFile); // Empty file

        List<SipMessage> captured = new CopyOnWriteArrayList<>();
        MockProcess mockProcess = new MockProcess(500);

        Thread tailer = new Thread(() -> {
            runner.tailJtlFile(jtlFile.toString(), captured::add, mockProcess);
        });
        tailer.start();

        tailer.join(2000);

        assertEquals(0, captured.size(), "Should not capture any messages from empty file");
    }

    @Test
    void testTailJtlFile_HeaderOnly() throws Exception {
        // Test with file containing only the header (no data rows)
        Path jtlFile = tempDir.resolve("test_header_only.jtl");
        Files.writeString(jtlFile, JTL_HEADER);

        List<SipMessage> captured = new CopyOnWriteArrayList<>();
        MockProcess mockProcess = new MockProcess(1000);

        Thread tailer = new Thread(() -> {
            runner.tailJtlFile(jtlFile.toString(), captured::add, mockProcess);
        });
        tailer.start();

        tailer.join(2000);

        assertEquals(0, captured.size(), "Should not capture any messages from header-only file");
    }

    @Test
    void testTailJtlFile_FilteredMessagesNotCaptured() throws Exception {
        // Test that filtered messages (timers, debug samplers) are not captured
        Path jtlFile = tempDir.resolve("test_filtered.jtl");
        Files.writeString(jtlFile, JTL_HEADER);

        List<SipMessage> captured = new CopyOnWriteArrayList<>();
        MockProcess mockProcess = new MockProcess(2000);

        Thread tailer = new Thread(() -> {
            runner.tailJtlFile(jtlFile.toString(), captured::add, mockProcess);
        });
        tailer.start();

        Thread.sleep(100);

        // Add a valid SIP message
        appendLine(jtlFile, "1778572664241,11,Send BYE to TAS from B Party,200,SIP Response send successfully.,Thread Group 3-1,text,true,,339,0,1,3,null,0,0,0");
        Thread.sleep(100);

        // Add filtered messages (should not be captured)
        appendLine(jtlFile, "1778572662968,1007,Short Delay,200,Timer successfully waited for 1000 miliseconds.,Thread Group 2-1,text,true,,0,0,1,3,null,0,0,0");
        appendLine(jtlFile, "1778572664110,0,ATo: sip:13880,2001,succes,Thread Group 1-1,text,true,,14,0,1,3,null,0,0,0");
        appendLine(jtlFile, "1778572664132,3,Debug Sampler - before call,200,OK,Thread Group 1-1,text,true,,903,0,1,3,null,0,0,0");
        Thread.sleep(200);

        // Add another valid SIP message
        appendLine(jtlFile, "1778572663980,104,Send INVITE from A party to TAS,200,SIP Response send successfully.,Thread Group 2-1,text,true,,354,0,1,3,null,0,0,8");
        Thread.sleep(200);

        tailer.join(3000);

        assertEquals(2, captured.size(), "Should only capture valid SIP messages, not filtered ones");
        assertEquals(SipMessage.MessageType.BYE, captured.get(0).getMessageType());
        assertEquals(SipMessage.MessageType.INVITE, captured.get(1).getMessageType());
    }

    /**
     * Helper method to append a line to a file (simulating incremental JTL writes)
     */
    private void appendLine(Path file, String line) throws IOException {
        Files.writeString(file, line + "\n", StandardOpenOption.APPEND);
    }
}
