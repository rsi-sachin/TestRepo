package com.tts.demo.model;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for TrafficStats model with per-node tracking.
 * Tests thread safety, statistics calculation, and per-node message tracking.
 */
class TrafficStatsTest {

    private TrafficStats stats;

    @BeforeEach
    void setUp() {
        stats = new TrafficStats();
    }

    @Test
    void testInitialState() {
        assertEquals(0, stats.getTotalAttempts());
        assertEquals(0, stats.getSuccessfulCalls());
        assertEquals(0, stats.getFailedCalls());
        assertEquals(0.0, stats.getSuccessRate(), 0.01);
        assertEquals(0.0, stats.getFailureRate(), 0.01);
        assertEquals(0.0, stats.getAverageResponseTime(), 0.01);
        assertEquals(0.0, stats.getCallsPerSecond(), 0.01);
        assertTrue(stats.getActiveNodes().isEmpty());
    }

    @Test
    void testRecordAttemptWithNode() {
        ActorType node = ActorType.P_CSCF;
        stats.recordAttempt(node);
        
        assertEquals(1, stats.getTotalAttempts());
        Set<ActorType> activeNodes = stats.getActiveNodes();
        assertEquals(1, activeNodes.size());
        assertTrue(activeNodes.contains(node));
    }

    @Test
    void testRecordSuccessWithNode() {
        ActorType node = ActorType.HSS;
        long responseTime = 150L;
        
        stats.recordSuccess(node, responseTime);
        
        assertEquals(1, stats.getTotalAttempts());
        assertEquals(1, stats.getSuccessfulCalls());
        assertEquals(0, stats.getFailedCalls());
        assertEquals(100.0, stats.getSuccessRate(), 0.01);
        assertEquals(150.0, stats.getAverageResponseTime(), 0.01);
        assertTrue(stats.getActiveNodes().contains(node));
    }

    @Test
    void testRecordFailureWithNode() {
        ActorType node = ActorType.S_CSCF;
        
        stats.recordAttempt(node);
        stats.recordFailure(node);
        
        assertEquals(1, stats.getTotalAttempts());
        assertEquals(0, stats.getSuccessfulCalls());
        assertEquals(1, stats.getFailedCalls());
        assertEquals(0.0, stats.getSuccessRate(), 0.01);
        assertEquals(100.0, stats.getFailureRate(), 0.01);
        assertTrue(stats.getActiveNodes().contains(node));
    }

    @Test
    void testMultipleNodesTracking() {
        stats.recordSuccess(ActorType.P_CSCF, 100L);
        stats.recordSuccess(ActorType.S_CSCF, 150L);
        stats.recordSuccess(ActorType.HSS, 80L);
        stats.recordFailure(ActorType.I_CSCF);
        
        Set<ActorType> activeNodes = stats.getActiveNodes();
        assertEquals(4, activeNodes.size());
        assertTrue(activeNodes.contains(ActorType.P_CSCF));
        assertTrue(activeNodes.contains(ActorType.S_CSCF));
        assertTrue(activeNodes.contains(ActorType.HSS));
        assertTrue(activeNodes.contains(ActorType.I_CSCF));
        
        assertEquals(4, stats.getTotalAttempts());
        assertEquals(3, stats.getSuccessfulCalls());
        assertEquals(1, stats.getFailedCalls());
    }

    @Test
    void testGetMessagesPerSecond() throws InterruptedException {
        ActorType node = ActorType.P_CSCF;
        LocalDateTime timestamp = LocalDateTime.now().withNano(0);
        
        // Record multiple messages in the same second
        stats.recordSuccess(node, 100L);
        stats.recordSuccess(node, 110L);
        stats.recordSuccess(node, 120L);
        
        // Small delay to ensure timestamp alignment
        Thread.sleep(100);
        
        int mps = stats.getMessagesPerSecond(node, timestamp);
        assertEquals(3, mps);
    }

    @Test
    void testGetTimestampsForNode() {
        ActorType node = ActorType.HSS;
        LocalDateTime now = LocalDateTime.now().withNano(0);
        
        stats.recordSuccess(node, 100L);
        
        Set<LocalDateTime> timestamps = stats.getTimestamps(node);
        assertNotNull(timestamps);
        assertFalse(timestamps.isEmpty());
    }

    @Test
    void testSuccessRateCalculation() {
        stats.recordSuccess(ActorType.P_CSCF, 100L);
        stats.recordSuccess(ActorType.S_CSCF, 120L);
        stats.recordSuccess(ActorType.HSS, 90L);
        stats.recordFailure(ActorType.I_CSCF);
        
        assertEquals(75.0, stats.getSuccessRate(), 0.01);
        assertEquals(25.0, stats.getFailureRate(), 0.01);
    }

    @Test
    void testAverageResponseTime() {
        stats.recordSuccess(ActorType.P_CSCF, 100L);
        stats.recordSuccess(ActorType.S_CSCF, 200L);
        stats.recordSuccess(ActorType.HSS, 150L);
        
        assertEquals(150.0, stats.getAverageResponseTime(), 0.01);
    }

    @Test
    void testCallsPerSecond() throws InterruptedException {
        // Record multiple calls
        for (int i = 0; i < 10; i++) {
            stats.recordSuccess(ActorType.P_CSCF, 100L);
        }
        
        // Wait a moment and check CPS
        Thread.sleep(1100);
        
        double cps = stats.getCallsPerSecond();
        assertTrue(cps > 0, "CPS should be greater than 0");
    }

    @Test
    void testReset() {
        stats.recordSuccess(ActorType.P_CSCF, 100L);
        stats.recordSuccess(ActorType.S_CSCF, 120L);
        stats.recordFailure(ActorType.HSS);
        
        stats.reset();
        
        assertEquals(0, stats.getTotalAttempts());
        assertEquals(0, stats.getSuccessfulCalls());
        assertEquals(0, stats.getFailedCalls());
        assertTrue(stats.getActiveNodes().isEmpty());
    }

    @Test
    void testConcurrentAccess() throws InterruptedException {
        int threadCount = 10;
        int operationsPerThread = 100;
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        CountDownLatch latch = new CountDownLatch(threadCount);
        
        ActorType[] nodes = ActorType.values();
        
        for (int i = 0; i < threadCount; i++) {
            final int threadIndex = i;
            executor.submit(() -> {
                try {
                    for (int j = 0; j < operationsPerThread; j++) {
                        ActorType node = nodes[j % nodes.length];
                        if (j % 2 == 0) {
                            stats.recordSuccess(node, 100L + j);
                        } else {
                            stats.recordFailure(node);
                        }
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        assertTrue(latch.await(10, TimeUnit.SECONDS), "Concurrent operations should complete");
        executor.shutdown();
        
        // Verify total operations
        int expectedTotal = threadCount * operationsPerThread;
        assertEquals(expectedTotal, stats.getTotalAttempts());
        assertEquals(expectedTotal / 2, stats.getSuccessfulCalls());
        assertEquals(expectedTotal / 2, stats.getFailedCalls());
        
        // Verify all nodes were tracked
        Set<ActorType> activeNodes = stats.getActiveNodes();
        assertTrue(activeNodes.size() > 0, "Should have tracked multiple nodes");
    }

    @Test
    void testGetMessagesPerSecondForNonExistentNode() {
        ActorType node = ActorType.AS;
        LocalDateTime timestamp = LocalDateTime.now().withNano(0);
        
        int mps = stats.getMessagesPerSecond(node, timestamp);
        assertEquals(0, mps, "Should return 0 for node with no messages");
    }

    @Test
    void testGetTimestampsForNonExistentNode() {
        ActorType node = ActorType.AS;
        
        Set<LocalDateTime> timestamps = stats.getTimestamps(node);
        assertNotNull(timestamps);
        assertTrue(timestamps.isEmpty(), "Should return empty set for non-existent node");
    }

    @Test
    void testPerNodeMessageDistribution() {
        // Record different message counts for different nodes
        for (int i = 0; i < 5; i++) {
            stats.recordSuccess(ActorType.P_CSCF, 100L);
        }
        for (int i = 0; i < 3; i++) {
            stats.recordSuccess(ActorType.S_CSCF, 120L);
        }
        for (int i = 0; i < 7; i++) {
            stats.recordSuccess(ActorType.HSS, 90L);
        }
        
        assertEquals(15, stats.getTotalAttempts());
        assertEquals(15, stats.getSuccessfulCalls());
        
        Set<ActorType> activeNodes = stats.getActiveNodes();
        assertEquals(3, activeNodes.size());
    }
}
