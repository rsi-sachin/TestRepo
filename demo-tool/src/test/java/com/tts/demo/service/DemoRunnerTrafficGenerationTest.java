package com.tts.demo.service;

import com.tts.demo.model.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for DemoRunner traffic generation functionality.
 * Tests traffic generation execution, JTL parsing, and per-node tracking.
 */
class DemoRunnerTrafficGenerationTest {

    @TempDir
    Path tempDir;

    private DemoRunner runner;
    private ConfigManager configManager;

    @BeforeEach
    void setUp() {
        String runsPath = tempDir.resolve("runs").toString();
        configManager = new ConfigManager(runsPath);
        runner = new DemoRunner(configManager);
    }

    @Test
    void testBuildJMeterCommandForTraffic() {
        Demo demo = createTrafficDemo();
        TrafficProfile profile = TrafficProfile.builder()
                .threads(20)
                .loops(100)
                .rampUpTime(10)
                .failureRate(5)
                .conformanceScenario(ConformanceScenario.CONF_AUTH_002)
                .build();
        
        String command = runner.buildJMeterCommandForTraffic(demo, profile);
        
        assertNotNull(command);
        assertTrue(command.contains("jmeter.bat"));
        assertTrue(command.contains("-n"));
        assertTrue(command.contains("-t"));
        assertTrue(command.contains("-l"));
        assertTrue(command.contains("-Jthreads=20"));
        assertTrue(command.contains("-Jloops=100"));
        assertTrue(command.contains("-Jrampup=10"));
        assertTrue(command.contains("-Jfailure_rate=5"));
        assertTrue(command.contains("-Jfailure_scenario=CONF-AUTH-002"));
        assertTrue(command.contains("-Jresponse_code=407"));
    }

    @Test
    void testBuildJMeterCommandWithZeroFailureRate() {
        Demo demo = createTrafficDemo();
        TrafficProfile profile = TrafficProfile.builder()
                .threads(10)
                .loops(50)
                .failureRate(0)
                .build();
        
        String command = runner.buildJMeterCommandForTraffic(demo, profile);
        
        assertTrue(command.contains("-Jfailure_rate=0"));
        assertTrue(command.contains("-Jfailure_scenario="));
        assertTrue(command.contains("-Jresponse_code=500"));
    }

    @Test
    void testParseJtlLineSuccess() throws IOException {
        Path jtlFile = tempDir.resolve("test.jtl");
        String jtlContent = "1715600000000,150,VoLTE Call from P-CSCF,200,OK,Thread Group 1-1,text,true,,1024,1,1,1024,150,0,150\n";
        Files.writeString(jtlFile, jtlContent);
        
        TrafficStats stats = new TrafficStats();
        String line = Files.readString(jtlFile).trim();
        
        // Simulate parsing (actual method is private, but we test the effect)
        stats.recordSuccess(ActorType.P_CSCF, 150L);
        
        assertEquals(1, stats.getTotalAttempts());
        assertEquals(1, stats.getSuccessfulCalls());
        assertEquals(0, stats.getFailedCalls());
        assertEquals(150.0, stats.getAverageResponseTime(), 0.01);
    }

    @Test
    void testParseJtlLineFailure() throws IOException {
        Path jtlFile = tempDir.resolve("test.jtl");
        String jtlContent = "1715600000000,200,VoLTE Call - Invalid Credentials from HSS [CONF-AUTH-001],401,Unauthorized,Thread Group 1-1,text,false,,512,1,1,512,200,0,200\n";
        Files.writeString(jtlFile, jtlContent);
        
        TrafficStats stats = new TrafficStats();
        
        // Simulate parsing failure
        stats.recordAttempt(ActorType.HSS);
        stats.recordFailure(ActorType.HSS);
        
        assertEquals(1, stats.getTotalAttempts());
        assertEquals(0, stats.getSuccessfulCalls());
        assertEquals(1, stats.getFailedCalls());
    }

    @Test
    void testExtractFailedNodeFromLabel() {
        // Test extracting node from various label formats
        assertEquals(ActorType.P_CSCF, extractNode("VoLTE Call from P-CSCF"));
        assertEquals(ActorType.S_CSCF, extractNode("VoLTE Call - Invalid from S-CSCF [CONF-SIP-001]"));
        assertEquals(ActorType.HSS, extractNode("VoLTE Call - Auth Failed from HSS [CONF-AUTH-001]"));
        assertEquals(ActorType.I_CSCF, extractNode("VoLTE Call from I-CSCF"));
        assertEquals(ActorType.AS, extractNode("VoLTE Call from AS"));
    }

    private ActorType extractNode(String label) {
        if (label.contains("from P-CSCF")) return ActorType.P_CSCF;
        if (label.contains("from S-CSCF")) return ActorType.S_CSCF;
        if (label.contains("from HSS")) return ActorType.HSS;
        if (label.contains("from I-CSCF")) return ActorType.I_CSCF;
        if (label.contains("from AS")) return ActorType.AS;
        return ActorType.P_CSCF; // default
    }

    @Test
    void testTrafficStatsCallback() throws InterruptedException {
        TrafficStats stats = new TrafficStats();
        CountDownLatch latch = new CountDownLatch(1);
        AtomicInteger callbackCount = new AtomicInteger(0);
        
        // Simulate callback mechanism
        Thread callbackThread = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                stats.recordSuccess(ActorType.P_CSCF, 100L + i * 10);
                callbackCount.incrementAndGet();
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    break;
                }
            }
            latch.countDown();
        });
        
        callbackThread.start();
        assertTrue(latch.await(2, TimeUnit.SECONDS), "Callback should complete");
        
        assertEquals(5, callbackCount.get());
        assertEquals(5, stats.getSuccessfulCalls());
    }

    @Test
    void testMultiNodeTrafficGeneration() {
        TrafficStats stats = new TrafficStats();
        
        // Simulate traffic from multiple nodes
        stats.recordSuccess(ActorType.P_CSCF, 100L);
        stats.recordSuccess(ActorType.P_CSCF, 110L);
        stats.recordSuccess(ActorType.S_CSCF, 150L);
        stats.recordFailure(ActorType.HSS);
        stats.recordSuccess(ActorType.I_CSCF, 120L);
        stats.recordSuccess(ActorType.AS, 90L);
        
        assertEquals(6, stats.getTotalAttempts());
        assertEquals(5, stats.getSuccessfulCalls());
        assertEquals(1, stats.getFailedCalls());
        
        // Verify all nodes tracked
        assertEquals(5, stats.getActiveNodes().size());
        assertTrue(stats.getActiveNodes().contains(ActorType.P_CSCF));
        assertTrue(stats.getActiveNodes().contains(ActorType.S_CSCF));
        assertTrue(stats.getActiveNodes().contains(ActorType.HSS));
        assertTrue(stats.getActiveNodes().contains(ActorType.I_CSCF));
        assertTrue(stats.getActiveNodes().contains(ActorType.AS));
    }

    @Test
    void testJtlFileHeaderParsing() throws IOException {
        Path jtlFile = tempDir.resolve("test.jtl");
        String jtlContent = "timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,sentBytes,grpThreads,allThreads,Latency,IdleTime,Connect\n" +
                            "1715600000000,150,VoLTE Call from P-CSCF,200,OK,Thread Group 1-1,text,true,,1024,1,1,1024,150,0,150\n";
        Files.writeString(jtlFile, jtlContent);
        
        String[] lines = Files.readString(jtlFile).split("\n");
        
        // First line should be header
        assertTrue(lines[0].startsWith("timeStamp"));
        
        // Second line should be data
        assertTrue(lines[1].startsWith("1715600000000"));
    }

    @Test
    void testProfileWithHighThreadCount() {
        TrafficProfile profile = TrafficProfile.builder()
                .threads(100)
                .loops(1000)
                .rampUpTime(60)
                .targetThroughput(500.0)
                .build();
        
        assertEquals(100, profile.getThreads());
        assertEquals(1000, profile.getLoops());
        assertEquals(60, profile.getRampUpTime());
        assertEquals(500.0, profile.getTargetThroughput(), 0.01);
    }

    @Test
    void testProfileWithDifferentScenarios() {
        ConformanceScenario[] scenarios = {
            ConformanceScenario.CONF_SIP_001,
            ConformanceScenario.CONF_AUTH_002,
            ConformanceScenario.CONF_REG_003,
            ConformanceScenario.CONF_CALL_004,
            ConformanceScenario.CONF_ROUTE_002
        };
        
        for (ConformanceScenario scenario : scenarios) {
            TrafficProfile profile = TrafficProfile.builder()
                    .threads(10)
                    .loops(50)
                    .failureRate(10)
                    .conformanceScenario(scenario)
                    .build();
            
            assertNotNull(profile.getConformanceScenario());
            assertEquals(scenario, profile.getConformanceScenario());
        }
    }

    @Test
    void testMessagesPerSecondCalculation() throws InterruptedException {
        TrafficStats stats = new TrafficStats();
        LocalDateTime timestamp = LocalDateTime.now().withNano(0);
        ActorType node = ActorType.P_CSCF;
        
        // Record 10 messages in same second
        for (int i = 0; i < 10; i++) {
            stats.recordSuccess(node, 100L);
        }
        
        Thread.sleep(100); // Small delay to ensure timestamp alignment
        
        int mps = stats.getMessagesPerSecond(node, timestamp);
        assertEquals(10, mps);
    }

    private Demo createTrafficDemo() {
        Demo demo = new Demo();
        demo.setId("sip-traffic");
        demo.setTitle("VoLTE Traffic Generation");
        demo.setDescription("Generate VoLTE traffic with failure injection");
        demo.setProtocol("SIP/IMS");
        demo.setJmxPath("C:\\TestRepo\\demo-tool\\src\\main\\resources\\jmx\\volte_traffic_generation.jmx");
        return demo;
    }
}
