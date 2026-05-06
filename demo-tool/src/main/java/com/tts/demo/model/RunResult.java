package com.tts.demo.model;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Objects;

/**
 * Represents the execution result of a demo run.
 * Includes metadata, status, and timing information.
 */
public class RunResult {
    
    private String runId;
    private String demoId;
    private String demoTitle;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private RunStatus status;
    private int exitCode;
    private String logFilePath;
    private String outputSnapshot;

    public RunResult() {
    }

    public RunResult(String runId, String demoId, String demoTitle) {
        this.runId = runId;
        this.demoId = demoId;
        this.demoTitle = demoTitle;
        this.startTime = LocalDateTime.now();
        this.status = RunStatus.RUNNING;
    }

    /**
     * Calculates the duration of the run in seconds.
     * Returns 0 if the run hasn't completed yet.
     */
    public long getDurationSeconds() {
        if (endTime == null || startTime == null) {
            return 0;
        }
        return ChronoUnit.SECONDS.between(startTime, endTime);
    }

    /**
     * Marks the run as completed with the given exit code.
     */
    public void complete(int exitCode) {
        this.endTime = LocalDateTime.now();
        this.exitCode = exitCode;
        this.status = (exitCode == 0) ? RunStatus.SUCCESS : RunStatus.FAILED;
    }

    /**
     * Marks the run as failed with an error message.
     */
    public void fail(String errorMessage) {
        this.endTime = LocalDateTime.now();
        this.status = RunStatus.FAILED;
        this.outputSnapshot = errorMessage;
    }

    // Getters and Setters
    public String getRunId() {
        return runId;
    }

    public void setRunId(String runId) {
        this.runId = runId;
    }

    public String getDemoId() {
        return demoId;
    }

    public void setDemoId(String demoId) {
        this.demoId = demoId;
    }

    public String getDemoTitle() {
        return demoTitle;
    }

    public void setDemoTitle(String demoTitle) {
        this.demoTitle = demoTitle;
    }

    public LocalDateTime getStartTime() {
        return startTime;
    }

    public void setStartTime(LocalDateTime startTime) {
        this.startTime = startTime;
    }

    public LocalDateTime getEndTime() {
        return endTime;
    }

    public void setEndTime(LocalDateTime endTime) {
        this.endTime = endTime;
    }

    public RunStatus getStatus() {
        return status;
    }

    public void setStatus(RunStatus status) {
        this.status = status;
    }

    public int getExitCode() {
        return exitCode;
    }

    public void setExitCode(int exitCode) {
        this.exitCode = exitCode;
    }

    public String getLogFilePath() {
        return logFilePath;
    }

    public void setLogFilePath(String logFilePath) {
        this.logFilePath = logFilePath;
    }

    public String getOutputSnapshot() {
        return outputSnapshot;
    }

    public void setOutputSnapshot(String outputSnapshot) {
        this.outputSnapshot = outputSnapshot;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        RunResult runResult = (RunResult) o;
        return Objects.equals(runId, runResult.runId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(runId);
    }

    @Override
    public String toString() {
        return "RunResult{" +
                "runId='" + runId + '\'' +
                ", demoTitle='" + demoTitle + '\'' +
                ", status=" + status +
                ", duration=" + getDurationSeconds() + "s" +
                '}';
    }

    /**
     * Run execution status
     */
    public enum RunStatus {
        RUNNING("Running"),
        SUCCESS("Success"),
        FAILED("Failed");

        private final String displayName;

        RunStatus(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }
    }
}
