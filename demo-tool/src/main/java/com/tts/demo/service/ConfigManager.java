package com.tts.demo.service;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.tts.demo.model.RunResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Manages application configuration and run history persistence.
 * Stores run results as JSON files in the runs/ folder.
 */
public class ConfigManager {
    
    private static final Logger logger = LoggerFactory.getLogger(ConfigManager.class);
    private static final String RUNS_DIR = "runs";
    private static final DateTimeFormatter FILE_DATE_FORMAT = 
            DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");
    
    private final Gson gson;
    private final Path runsDirectory;

    public ConfigManager() {
        this(RUNS_DIR);
    }

    public ConfigManager(String runsDirectoryPath) {
        this.gson = new GsonBuilder()
                .setPrettyPrinting()
                .registerTypeAdapter(LocalDateTime.class, new LocalDateTimeAdapter())
                .create();
        this.runsDirectory = Paths.get(runsDirectoryPath);
        ensureRunsDirectoryExists();
    }

    /**
     * Creates the runs directory if it doesn't exist.
     */
    private void ensureRunsDirectoryExists() {
        try {
            if (!Files.exists(runsDirectory)) {
                Files.createDirectories(runsDirectory);
                logger.info("Created runs directory: {}", runsDirectory.toAbsolutePath());
            }
        } catch (IOException e) {
            logger.error("Failed to create runs directory", e);
        }
    }

    /**
     * Saves a run result to a JSON file.
     */
    public void saveRunResult(RunResult result) {
        try {
            String fileName = generateRunFileName(result);
            Path filePath = runsDirectory.resolve(fileName);
            
            try (FileWriter writer = new FileWriter(filePath.toFile())) {
                gson.toJson(result, writer);
                logger.info("Saved run result: {}", fileName);
            }
        } catch (IOException e) {
            logger.error("Failed to save run result: {}", result.getRunId(), e);
        }
    }

    /**
     * Generates a unique file name for a run result.
     * Format: run_{timestamp}_{demoId}.json
     */
    private String generateRunFileName(RunResult result) {
        String timestamp = result.getStartTime().format(FILE_DATE_FORMAT);
        return String.format("run_%s_%s.json", timestamp, result.getDemoId());
    }

    /**
     * Loads all run results from the runs directory.
     * Results are sorted by start time in descending order (newest first).
     */
    public List<RunResult> loadRunHistory() {
        List<RunResult> results = new ArrayList<>();
        
        File runsDir = runsDirectory.toFile();
        if (!runsDir.exists() || !runsDir.isDirectory()) {
            logger.warn("Runs directory does not exist: {}", runsDirectory);
            return results;
        }

        File[] files = runsDir.listFiles((dir, name) -> name.endsWith(".json"));
        if (files == null) {
            return results;
        }

        for (File file : files) {
            try (FileReader reader = new FileReader(file)) {
                RunResult result = gson.fromJson(reader, RunResult.class);
                if (result != null) {
                    results.add(result);
                }
            } catch (IOException e) {
                logger.error("Failed to load run result from: {}", file.getName(), e);
            }
        }

        // Sort by start time, newest first
        results.sort(Comparator.comparing(RunResult::getStartTime).reversed());
        
        logger.info("Loaded {} run results from history", results.size());
        return results;
    }

    /**
     * Loads a specific run result by ID.
     */
    public Optional<RunResult> loadRunResult(String runId) {
        return loadRunHistory().stream()
                .filter(r -> r.getRunId().equals(runId))
                .findFirst();
    }

    /**
     * Deletes a run result file.
     */
    public boolean deleteRunResult(String runId) {
        Optional<RunResult> result = loadRunResult(runId);
        if (result.isEmpty()) {
            return false;
        }

        try {
            String fileName = generateRunFileName(result.get());
            Path filePath = runsDirectory.resolve(fileName);
            Files.deleteIfExists(filePath);
            logger.info("Deleted run result: {}", fileName);
            return true;
        } catch (IOException e) {
            logger.error("Failed to delete run result: {}", runId, e);
            return false;
        }
    }

    /**
     * Clears all run history (deletes all JSON files).
     */
    public int clearRunHistory() {
        File runsDir = runsDirectory.toFile();
        if (!runsDir.exists()) {
            return 0;
        }

        File[] files = runsDir.listFiles((dir, name) -> name.endsWith(".json"));
        if (files == null) {
            return 0;
        }

        int deletedCount = 0;
        for (File file : files) {
            if (file.delete()) {
                deletedCount++;
            }
        }

        logger.info("Cleared {} run results from history", deletedCount);
        return deletedCount;
    }

    /**
     * Returns statistics about run history.
     */
    public Map<String, Object> getRunStatistics() {
        List<RunResult> history = loadRunHistory();
        
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalRuns", history.size());
        stats.put("successfulRuns", history.stream()
                .filter(r -> r.getStatus() == RunResult.RunStatus.SUCCESS)
                .count());
        stats.put("failedRuns", history.stream()
                .filter(r -> r.getStatus() == RunResult.RunStatus.FAILED)
                .count());
        
        if (!history.isEmpty()) {
            stats.put("latestRun", history.get(0).getStartTime());
        }
        
        return stats;
    }

    /**
     * Gets the runs directory path.
     */
    public Path getRunsDirectory() {
        return runsDirectory;
    }
}
