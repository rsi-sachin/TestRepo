package com.tts.demo.model;

import java.util.HashMap;
import java.util.Map;

/**
 * Traffic generation profile for load testing and failure simulation.
 * Configures call volume, rate, duration, and failure injection parameters.
 * 
 * Added May 13, 2026 for traffic generation engine capability.
 */
public class TrafficProfile {
    
    private String profileId;
    private String profileName;
    private String description;
    
    // Traffic volume configuration
    private int concurrentCalls;        // Number of simultaneous calls (threads)
    private int totalCalls;             // Total number of calls to generate (loops)
    private int rampUpSeconds;          // Time to ramp up to full load
    private int durationSeconds;        // Test duration (0 = run until loops complete)
    
    // Failure injection configuration
    private double failureRate;         // Percentage: 0.0 to 100.0
    private ActorType failureNode;      // Which node should inject failures
    private String failureScenario;     // 3GPP conformance scenario ID
    private FailureType failureType;    // Type of failure to inject
    
    // Call flow configuration
    private int callHoldTimeMs;         // How long each call stays active
    private int interCallDelayMs;       // Delay between successive calls from same thread
    
    // Statistics tracking
    private boolean collectDetailedStats;
    private boolean exportRawData;
    
    public TrafficProfile() {
        // Defaults
        this.concurrentCalls = 10;
        this.totalCalls = 100;
        this.rampUpSeconds = 10;
        this.durationSeconds = 0;
        this.failureRate = 0.0;
        this.failureNode = ActorType.UNKNOWN;
        this.failureScenario = "NONE";
        this.failureType = FailureType.UNKNOWN;
        this.callHoldTimeMs = 5000;
        this.interCallDelayMs = 100;
        this.collectDetailedStats = true;
        this.exportRawData = false;
    }
    
    // Getters and Setters
    
    public String getProfileId() {
        return profileId;
    }
    
    public void setProfileId(String profileId) {
        this.profileId = profileId;
    }
    
    public String getProfileName() {
        return profileName;
    }
    
    public void setProfileName(String profileName) {
        this.profileName = profileName;
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public int getConcurrentCalls() {
        return concurrentCalls;
    }
    
    public void setConcurrentCalls(int concurrentCalls) {
        this.concurrentCalls = concurrentCalls;
    }
    
    public int getTotalCalls() {
        return totalCalls;
    }
    
    public void setTotalCalls(int totalCalls) {
        this.totalCalls = totalCalls;
    }
    
    public int getRampUpSeconds() {
        return rampUpSeconds;
    }
    
    public void setRampUpSeconds(int rampUpSeconds) {
        this.rampUpSeconds = rampUpSeconds;
    }
    
    public int getDurationSeconds() {
        return durationSeconds;
    }
    
    public void setDurationSeconds(int durationSeconds) {
        this.durationSeconds = durationSeconds;
    }
    
    public double getFailureRate() {
        return failureRate;
    }
    
    public void setFailureRate(double failureRate) {
        this.failureRate = Math.max(0.0, Math.min(100.0, failureRate));
    }
    
    public ActorType getFailureNode() {
        return failureNode;
    }
    
    public void setFailureNode(ActorType failureNode) {
        this.failureNode = failureNode;
    }
    
    public String getFailureScenario() {
        return failureScenario;
    }
    
    public void setFailureScenario(String failureScenario) {
        this.failureScenario = failureScenario;
    }
    
    public FailureType getFailureType() {
        return failureType;
    }
    
    public void setFailureType(FailureType failureType) {
        this.failureType = failureType;
    }
    
    public int getCallHoldTimeMs() {
        return callHoldTimeMs;
    }
    
    public void setCallHoldTimeMs(int callHoldTimeMs) {
        this.callHoldTimeMs = callHoldTimeMs;
    }
    
    public int getInterCallDelayMs() {
        return interCallDelayMs;
    }
    
    public void setInterCallDelayMs(int interCallDelayMs) {
        this.interCallDelayMs = interCallDelayMs;
    }
    
    public boolean isCollectDetailedStats() {
        return collectDetailedStats;
    }
    
    public void setCollectDetailedStats(boolean collectDetailedStats) {
        this.collectDetailedStats = collectDetailedStats;
    }
    
    public boolean isExportRawData() {
        return exportRawData;
    }
    
    public void setExportRawData(boolean exportRawData) {
        this.exportRawData = exportRawData;
    }
    
    /**
     * Convert to JMeter properties map
     */
    public Map<String, String> toJMeterProperties() {
        Map<String, String> props = new HashMap<>();
        
        // Basic load parameters
        props.put("threads", String.valueOf(concurrentCalls));
        props.put("loops", String.valueOf(totalCalls / concurrentCalls)); // Loops per thread
        props.put("rampup", String.valueOf(rampUpSeconds));
        props.put("duration", String.valueOf(durationSeconds));
        
        // Call timing
        props.put("call_hold_time", String.valueOf(callHoldTimeMs));
        props.put("inter_call_delay", String.valueOf(interCallDelayMs));
        
        // Failure injection
        props.put("failure_rate", String.valueOf(failureRate));
        props.put("failure_node", failureNode.name());
        props.put("failure_scenario", failureScenario);
        props.put("failure_type", failureType.name());
        
        // Extract response code from failure scenario if available
        String responseCode = extractResponseCodeFromScenario(failureScenario);
        if (responseCode != null && !responseCode.isEmpty()) {
            props.put("failure_response_code", responseCode);
        }
        
        return props;
    }
    
    /**
     * Extract response code from conformance scenario
     */
    private String extractResponseCodeFromScenario(String scenarioId) {
        if (scenarioId == null || scenarioId.equals("NONE")) {
            return "";
        }
        
        try {
            ConformanceScenario scenario = ConformanceScenario.fromId(scenarioId);
            if (scenario != null) {
                String expectedResponse = scenario.getExpectedResponse();
                // Extract just the numeric code (e.g., "403 Forbidden" -> "403")
                if (expectedResponse != null && !expectedResponse.isEmpty()) {
                    String[] parts = expectedResponse.split(" ");
                    if (parts.length > 0) {
                        return parts[0];
                    }
                }
            }
        } catch (Exception e) {
            // Ignore errors, just return empty
        }
        
        return "";
    }
    
    /**
     * Validation
     */
    public boolean isValid() {
        return concurrentCalls > 0 
            && totalCalls > 0 
            && rampUpSeconds >= 0
            && failureRate >= 0.0 && failureRate <= 100.0;
    }
    
    @Override
    public String toString() {
        return String.format("TrafficProfile[%s: %d calls @ %d concurrent, %.1f%% failure at %s]",
            profileName,
            totalCalls,
            concurrentCalls,
            failureRate,
            failureNode.getDisplayName());
    }
}
