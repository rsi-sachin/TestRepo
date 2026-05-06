package com.tts.demo.service;

import com.tts.demo.model.RunResult;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.File;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class ConfigManagerTest {

    @TempDir
    Path tempDir;

    private ConfigManager configManager;

    @BeforeEach
    void setUp() {
        String runsPath = tempDir.resolve("runs").toString();
        configManager = new ConfigManager(runsPath);
    }

    @AfterEach
    void tearDown() {
        configManager.clearRunHistory();
    }

    @Test
    void testRunsDirectoryCreated() {
        Path runsDir = configManager.getRunsDirectory();
        assertTrue(runsDir.toFile().exists(), "Runs directory should be created");
        assertTrue(runsDir.toFile().isDirectory(), "Runs path should be a directory");
    }

    @Test
    void testSaveRunResult() {
        RunResult result = new RunResult("run-001", "demo-001", "Test Demo");
        result.complete(0);

        configManager.saveRunResult(result);

        // Verify file was created
        File runsDir = configManager.getRunsDirectory().toFile();
        File[] files = runsDir.listFiles((dir, name) -> name.endsWith(".json"));
        assertNotNull(files);
        assertEquals(1, files.length, "Should have created one JSON file");
    }

    @Test
    void testLoadRunHistory() {
        // Save multiple run results
        RunResult result1 = new RunResult("run-001", "demo-001", "Test Demo 1");
        result1.complete(0);
        
        RunResult result2 = new RunResult("run-002", "demo-002", "Test Demo 2");
        result2.complete(1);

        configManager.saveRunResult(result1);
        configManager.saveRunResult(result2);

        // Load history
        List<RunResult> history = configManager.loadRunHistory();
        
        assertEquals(2, history.size(), "Should load 2 run results");
    }

    @Test
    void testLoadRunHistorySortedByDate() throws InterruptedException {
        // Create runs with slight time difference
        RunResult result1 = new RunResult("run-001", "demo-001", "Test Demo 1");
        result1.complete(0);
        configManager.saveRunResult(result1);

        Thread.sleep(100);

        RunResult result2 = new RunResult("run-002", "demo-002", "Test Demo 2");
        result2.complete(0);
        configManager.saveRunResult(result2);

        List<RunResult> history = configManager.loadRunHistory();
        
        assertEquals(2, history.size());
        // Newest should be first
        assertTrue(history.get(0).getStartTime().isAfter(history.get(1).getStartTime()) ||
                   history.get(0).getStartTime().isEqual(history.get(1).getStartTime()));
    }

    @Test
    void testLoadRunResultById() {
        RunResult result = new RunResult("run-123", "demo-001", "Test Demo");
        result.complete(0);
        configManager.saveRunResult(result);

        Optional<RunResult> loaded = configManager.loadRunResult("run-123");
        
        assertTrue(loaded.isPresent(), "Should find the run result");
        assertEquals("run-123", loaded.get().getRunId());
        assertEquals("Test Demo", loaded.get().getDemoTitle());
    }

    @Test
    void testLoadRunResultByIdNotFound() {
        Optional<RunResult> loaded = configManager.loadRunResult("nonexistent-run");
        assertFalse(loaded.isPresent(), "Should not find nonexistent run");
    }

    @Test
    void testDeleteRunResult() {
        RunResult result = new RunResult("run-001", "demo-001", "Test Demo");
        result.complete(0);
        configManager.saveRunResult(result);

        boolean deleted = configManager.deleteRunResult("run-001");
        
        assertTrue(deleted, "Deletion should succeed");
        
        List<RunResult> history = configManager.loadRunHistory();
        assertEquals(0, history.size(), "History should be empty after deletion");
    }

    @Test
    void testDeleteRunResultNotFound() {
        boolean deleted = configManager.deleteRunResult("nonexistent-run");
        assertFalse(deleted, "Deletion should fail for nonexistent run");
    }

    @Test
    void testClearRunHistory() {
        // Save multiple runs
        for (int i = 1; i <= 5; i++) {
            RunResult result = new RunResult("run-" + i, "demo-001", "Test Demo " + i);
            result.complete(0);
            configManager.saveRunResult(result);
        }

        int cleared = configManager.clearRunHistory();
        
        assertEquals(5, cleared, "Should clear 5 runs");
        
        List<RunResult> history = configManager.loadRunHistory();
        assertEquals(0, history.size(), "History should be empty");
    }

    @Test
    void testGetRunStatistics() {
        // Save runs with different statuses
        RunResult success1 = new RunResult("run-001", "demo-001", "Success Demo 1");
        success1.complete(0);
        
        RunResult success2 = new RunResult("run-002", "demo-001", "Success Demo 2");
        success2.complete(0);
        
        RunResult failed = new RunResult("run-003", "demo-002", "Failed Demo");
        failed.complete(1);

        configManager.saveRunResult(success1);
        configManager.saveRunResult(success2);
        configManager.saveRunResult(failed);

        Map<String, Object> stats = configManager.getRunStatistics();
        
        assertEquals(3, stats.get("totalRuns"));
        assertEquals(2L, stats.get("successfulRuns"));
        assertEquals(1L, stats.get("failedRuns"));
        assertNotNull(stats.get("latestRun"));
    }

    @Test
    void testGetRunStatisticsEmpty() {
        Map<String, Object> stats = configManager.getRunStatistics();
        
        assertEquals(0, stats.get("totalRuns"));
        assertEquals(0L, stats.get("successfulRuns"));
        assertEquals(0L, stats.get("failedRuns"));
        assertNull(stats.get("latestRun"));
    }

    @Test
    void testPersistenceAcrossInstances() {
        // Save with first instance
        RunResult result = new RunResult("run-001", "demo-001", "Test Demo");
        result.complete(0);
        configManager.saveRunResult(result);

        // Create new instance with same directory
        ConfigManager newManager = new ConfigManager(tempDir.resolve("runs").toString());
        List<RunResult> history = newManager.loadRunHistory();
        
        assertEquals(1, history.size(), "New instance should load existing data");
        assertEquals("run-001", history.get(0).getRunId());
    }

    @Test
    void testLocalDateTimeSerializationRoundTrip() {
        RunResult original = new RunResult("run-001", "demo-001", "Test Demo");
        LocalDateTime now = LocalDateTime.now();
        original.setStartTime(now);
        original.setEndTime(now.plusMinutes(5));
        original.complete(0);

        configManager.saveRunResult(original);

        Optional<RunResult> loaded = configManager.loadRunResult("run-001");
        assertTrue(loaded.isPresent());
        
        // Verify timestamps are preserved (within 1 second due to serialization precision)
        assertEquals(original.getStartTime().withNano(0), 
                    loaded.get().getStartTime().withNano(0));
        assertEquals(original.getEndTime().withNano(0), 
                    loaded.get().getEndTime().withNano(0));
    }
}
