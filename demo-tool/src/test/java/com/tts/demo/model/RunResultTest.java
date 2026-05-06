package com.tts.demo.model;

import org.junit.jupiter.api.Test;
import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.*;

class RunResultTest {

    @Test
    void testRunResultCreation() {
        RunResult result = new RunResult("run-123", "demo-001", "Test Demo");
        
        assertEquals("run-123", result.getRunId());
        assertEquals("demo-001", result.getDemoId());
        assertEquals("Test Demo", result.getDemoTitle());
        assertNotNull(result.getStartTime());
        assertEquals(RunResult.RunStatus.RUNNING, result.getStatus());
    }

    @Test
    void testCompleteWithSuccess() {
        RunResult result = new RunResult("run-123", "demo-001", "Test Demo");
        
        result.complete(0);
        
        assertEquals(RunResult.RunStatus.SUCCESS, result.getStatus());
        assertEquals(0, result.getExitCode());
        assertNotNull(result.getEndTime());
        assertTrue(result.getDurationSeconds() >= 0);
    }

    @Test
    void testCompleteWithFailure() {
        RunResult result = new RunResult("run-123", "demo-001", "Test Demo");
        
        result.complete(1);
        
        assertEquals(RunResult.RunStatus.FAILED, result.getStatus());
        assertEquals(1, result.getExitCode());
        assertNotNull(result.getEndTime());
    }

    @Test
    void testFail() {
        RunResult result = new RunResult("run-123", "demo-001", "Test Demo");
        String errorMsg = "Connection timeout";
        
        result.fail(errorMsg);
        
        assertEquals(RunResult.RunStatus.FAILED, result.getStatus());
        assertEquals(errorMsg, result.getOutputSnapshot());
        assertNotNull(result.getEndTime());
    }

    @Test
    void testDurationCalculation() throws InterruptedException {
        RunResult result = new RunResult("run-123", "demo-001", "Test Demo");
        
        // Wait a bit
        Thread.sleep(1100);
        
        result.complete(0);
        
        long duration = result.getDurationSeconds();
        assertTrue(duration >= 1, "Duration should be at least 1 second");
    }

    @Test
    void testDurationBeforeCompletion() {
        RunResult result = new RunResult("run-123", "demo-001", "Test Demo");
        
        // Duration should be 0 before completion
        assertEquals(0, result.getDurationSeconds());
    }

    @Test
    void testRunStatusDisplayName() {
        assertEquals("Running", RunResult.RunStatus.RUNNING.getDisplayName());
        assertEquals("Success", RunResult.RunStatus.SUCCESS.getDisplayName());
        assertEquals("Failed", RunResult.RunStatus.FAILED.getDisplayName());
    }

    @Test
    void testEqualsAndHashCode() {
        RunResult result1 = new RunResult("run-123", "demo-001", "Test Demo");
        RunResult result2 = new RunResult("run-123", "demo-002", "Different Demo");
        RunResult result3 = new RunResult("run-456", "demo-001", "Test Demo");

        assertEquals(result1, result2); // Same run ID
        assertNotEquals(result1, result3); // Different run ID
        assertEquals(result1.hashCode(), result2.hashCode());
    }

    @Test
    void testToString() {
        RunResult result = new RunResult("run-123", "demo-001", "Test Demo");
        result.complete(0);
        
        String str = result.toString();
        assertTrue(str.contains("run-123"));
        assertTrue(str.contains("Test Demo"));
        assertTrue(str.contains("SUCCESS"));
    }

    @Test
    void testSettersAndGetters() {
        RunResult result = new RunResult();
        
        result.setRunId("run-999");
        assertEquals("run-999", result.getRunId());

        result.setDemoId("demo-999");
        assertEquals("demo-999", result.getDemoId());

        result.setDemoTitle("Custom Title");
        assertEquals("Custom Title", result.getDemoTitle());

        LocalDateTime now = LocalDateTime.now();
        result.setStartTime(now);
        assertEquals(now, result.getStartTime());

        result.setEndTime(now);
        assertEquals(now, result.getEndTime());

        result.setStatus(RunResult.RunStatus.SUCCESS);
        assertEquals(RunResult.RunStatus.SUCCESS, result.getStatus());

        result.setExitCode(42);
        assertEquals(42, result.getExitCode());

        result.setLogFilePath("C:\\logs\\test.log");
        assertEquals("C:\\logs\\test.log", result.getLogFilePath());

        result.setOutputSnapshot("test output");
        assertEquals("test output", result.getOutputSnapshot());
    }
}
