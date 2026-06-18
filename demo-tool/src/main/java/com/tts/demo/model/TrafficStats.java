package com.tts.demo.model;

import java.time.LocalDateTime;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Real-time statistics for traffic generation runs.
 * Thread-safe tracking of call attempts, successes, failures, and response times.
 * 
 * Added May 13, 2026 for traffic generation engine.
 */
public class TrafficStats {
    
    private final String sessionId;
    private final LocalDateTime startTime;
    private LocalDateTime endTime;
    
    // Call counters (thread-safe)
    private final AtomicInteger totalAttempts = new AtomicInteger(0);
    private final AtomicInteger successfulCalls = new AtomicInteger(0);
    private final AtomicInteger failedCalls = new AtomicInteger(0);
    
    // Failure breakdown by type (thread-safe)
    private final Map<String, AtomicInteger> failuresByType = new ConcurrentHashMap<>();
    private final Map<ActorType, AtomicInteger> failuresByNode = new ConcurrentHashMap<>();
    private final Map<String, AtomicInteger> failuresByResponseCode = new ConcurrentHashMap<>();
    
    // Response time tracking (in milliseconds)
    private final List<Long> responseTimes = Collections.synchronizedList(new ArrayList<>());
    private long minResponseTime = Long.MAX_VALUE;
    private long maxResponseTime = 0;
    
    // Throughput tracking
    private final Map<LocalDateTime, AtomicInteger> callsPerSecond = new ConcurrentHashMap<>();
    
    // Per-node throughput tracking (for multi-node chart visualization)
    private final Map<ActorType, Map<LocalDateTime, AtomicInteger>> messagesPerSecondByNode = new ConcurrentHashMap<>();
    
    // Traffic profile used
    private TrafficProfile profile;
    
    public TrafficStats(String sessionId) {
        this.sessionId = sessionId;
        this.startTime = LocalDateTime.now();
    }
    
    public TrafficStats(String sessionId, TrafficProfile profile) {
        this(sessionId);
        this.profile = profile;
    }
    
    /**
     * Record a call attempt
     */
    public synchronized void recordAttempt() {
        totalAttempts.incrementAndGet();
        
        // Track calls per second
        LocalDateTime now = LocalDateTime.now().withNano(0);
        AtomicInteger counter = callsPerSecond.computeIfAbsent(now, k -> new AtomicInteger(0));
        counter.incrementAndGet();
    }
    
    /**
     * Record a call attempt with node information (for per-node tracking)
     */
    public synchronized void recordAttempt(ActorType node) {
        recordAttempt();
        
        if (node != null && node != ActorType.UNKNOWN) {
            LocalDateTime now = LocalDateTime.now().withNano(0);
            Map<LocalDateTime, AtomicInteger> nodeStats = messagesPerSecondByNode.computeIfAbsent(node, k -> new ConcurrentHashMap<>());
            AtomicInteger counter = nodeStats.computeIfAbsent(now, k -> new AtomicInteger(0));
            counter.incrementAndGet();
        }
    }
    
    /**
     * Record a successful call with response time
     */
    public synchronized void recordSuccess(long responseTimeMs) {
        successfulCalls.incrementAndGet();
        recordResponseTime(responseTimeMs);
    }
    
    /**
     * Record a successful call with node information
     */
    public synchronized void recordSuccess(ActorType node, long responseTimeMs) {
        recordSuccess(responseTimeMs);
        
        if (node != null && node != ActorType.UNKNOWN) {
            LocalDateTime now = LocalDateTime.now().withNano(0);
            Map<LocalDateTime, AtomicInteger> nodeStats = messagesPerSecondByNode.computeIfAbsent(node, k -> new ConcurrentHashMap<>());
            AtomicInteger counter = nodeStats.computeIfAbsent(now, k -> new AtomicInteger(0));
            counter.incrementAndGet();
        }
    }
    
    /**
     * Record a failed call with failure details
     */
    public synchronized void recordFailure(String failureType, ActorType failedNode, String responseCode, long responseTimeMs) {
        failedCalls.incrementAndGet();
        recordResponseTime(responseTimeMs);
        
        // Track failure breakdown
        failuresByType.computeIfAbsent(failureType, k -> new AtomicInteger(0)).incrementAndGet();
        
        if (failedNode != null && failedNode != ActorType.UNKNOWN) {
            failuresByNode.computeIfAbsent(failedNode, k -> new AtomicInteger(0)).incrementAndGet();
        }
        
        if (responseCode != null && !responseCode.isEmpty()) {
            failuresByResponseCode.computeIfAbsent(responseCode, k -> new AtomicInteger(0)).incrementAndGet();
        }
    }
    
    /**
     * Record response time
     */
    private void recordResponseTime(long responseTimeMs) {
        responseTimes.add(responseTimeMs);
        
        if (responseTimeMs < minResponseTime) {
            minResponseTime = responseTimeMs;
        }
        if (responseTimeMs > maxResponseTime) {
            maxResponseTime = responseTimeMs;
        }
    }
    
    /**
     * Mark session as completed
     */
    public void markComplete() {
        if (endTime == null) {
            endTime = LocalDateTime.now();
        }
    }
    
    // ============ Computed Statistics ============
    
    public double getSuccessRate() {
        int total = totalAttempts.get();
        return total > 0 ? (successfulCalls.get() * 100.0 / total) : 0.0;
    }
    
    public double getFailureRate() {
        int total = totalAttempts.get();
        return total > 0 ? (failedCalls.get() * 100.0 / total) : 0.0;
    }
    
    public double getAverageResponseTime() {
        synchronized (responseTimes) {
            if (responseTimes.isEmpty()) return 0.0;
            return responseTimes.stream().mapToLong(Long::longValue).average().orElse(0.0);
        }
    }
    
    public long getMedianResponseTime() {
        synchronized (responseTimes) {
            if (responseTimes.isEmpty()) return 0;
            List<Long> sorted = new ArrayList<>(responseTimes);
            Collections.sort(sorted);
            return sorted.get(sorted.size() / 2);
        }
    }
    
    public long get95thPercentileResponseTime() {
        synchronized (responseTimes) {
            if (responseTimes.isEmpty()) return 0;
            List<Long> sorted = new ArrayList<>(responseTimes);
            Collections.sort(sorted);
            int index = (int) Math.ceil(sorted.size() * 0.95) - 1;
            return sorted.get(Math.max(0, index));
        }
    }
    
    public double getCallsPerSecond() {
        if (startTime == null || endTime == null) return 0.0;
        long durationSeconds = Duration.between(startTime, endTime).getSeconds();
        return durationSeconds > 0 ? (totalAttempts.get() / (double) durationSeconds) : 0.0;
    }
    
    public Duration getDuration() {
        LocalDateTime end = endTime != null ? endTime : LocalDateTime.now();
        return Duration.between(startTime, end);
    }
    
    // ============ Getters ============
    
    public String getSessionId() {
        return sessionId;
    }
    
    public LocalDateTime getStartTime() {
        return startTime;
    }
    
    public LocalDateTime getEndTime() {
        return endTime;
    }
    
    public int getTotalAttempts() {
        return totalAttempts.get();
    }
    
    public int getSuccessfulCalls() {
        return successfulCalls.get();
    }
    
    public int getFailedCalls() {
        return failedCalls.get();
    }
    
    public Map<String, Integer> getFailuresByType() {
        Map<String, Integer> result = new HashMap<>();
        failuresByType.forEach((k, v) -> result.put(k, v.get()));
        return result;
    }
    
    public Map<ActorType, Integer> getFailuresByNode() {
        Map<ActorType, Integer> result = new HashMap<>();
        failuresByNode.forEach((k, v) -> result.put(k, v.get()));
        return result;
    }
    
    public Map<String, Integer> getFailuresByResponseCode() {
        Map<String, Integer> result = new HashMap<>();
        failuresByResponseCode.forEach((k, v) -> result.put(k, v.get()));
        return result;
    }
    
    public long getMinResponseTime() {
        return minResponseTime == Long.MAX_VALUE ? 0 : minResponseTime;
    }
    
    public long getMaxResponseTime() {
        return maxResponseTime;
    }
    
    public TrafficProfile getProfile() {
        return profile;
    }
    
    public void setProfile(TrafficProfile profile) {
        this.profile = profile;
    }
    
    /**
     * Get messages per second for a specific node at a specific time
     */
    public int getMessagesPerSecond(ActorType node, LocalDateTime timestamp) {
        Map<LocalDateTime, AtomicInteger> nodeStats = messagesPerSecondByNode.get(node);
        if (nodeStats == null) {
            return 0;
        }
        AtomicInteger counter = nodeStats.get(timestamp);
        return counter != null ? counter.get() : 0;
    }
    
    /**
     * Get all active nodes being tracked
     */
    public Set<ActorType> getActiveNodes() {
        return new HashSet<>(messagesPerSecondByNode.keySet());
    }
    
    /**
     * Get all timestamps with data for a specific node
     */
    public Set<LocalDateTime> getTimestamps(ActorType node) {
        Map<LocalDateTime, AtomicInteger> nodeStats = messagesPerSecondByNode.get(node);
        if (nodeStats == null) {
            return new HashSet<>();
        }
        return new HashSet<>(nodeStats.keySet());
    }
    
    /**
     * Generate summary report
     */
    public String getSummaryReport() {
        StringBuilder sb = new StringBuilder();
        sb.append("=== Traffic Generation Summary ===\n");
        sb.append(String.format("Session ID: %s\n", sessionId));
        sb.append(String.format("Duration: %d seconds\n", getDuration().getSeconds()));
        sb.append(String.format("\nCall Statistics:\n"));
        sb.append(String.format("  Total Attempts: %d\n", getTotalAttempts()));
        sb.append(String.format("  Successful: %d (%.2f%%)\n", getSuccessfulCalls(), getSuccessRate()));
        sb.append(String.format("  Failed: %d (%.2f%%)\n", getFailedCalls(), getFailureRate()));
        sb.append(String.format("\nPerformance Metrics:\n"));
        sb.append(String.format("  Avg Response Time: %.0f ms\n", getAverageResponseTime()));
        sb.append(String.format("  Median Response Time: %d ms\n", getMedianResponseTime()));
        sb.append(String.format("  95th Percentile: %d ms\n", get95thPercentileResponseTime()));
        sb.append(String.format("  Min/Max: %d / %d ms\n", getMinResponseTime(), getMaxResponseTime()));
        sb.append(String.format("  Throughput: %.2f calls/sec\n", getCallsPerSecond()));
        
        if (!failuresByType.isEmpty()) {
            sb.append(String.format("\nFailure Breakdown by Type:\n"));
            failuresByType.forEach((type, count) -> 
                sb.append(String.format("  %s: %d (%.1f%%)\n", type, count.get(), 
                    count.get() * 100.0 / getFailedCalls())));
        }
        
        if (!failuresByNode.isEmpty()) {
            sb.append(String.format("\nFailure Breakdown by Node:\n"));
            failuresByNode.forEach((node, count) -> 
                sb.append(String.format("  %s: %d (%.1f%%)\n", node.getDisplayName(), count.get(),
                    count.get() * 100.0 / getFailedCalls())));
        }
        
        return sb.toString();
    }
    
    @Override
    public String toString() {
        return String.format("TrafficStats[%s: %d calls, %.2f%% success, %.0f ms avg]",
            sessionId, getTotalAttempts(), getSuccessRate(), getAverageResponseTime());
    }
}
