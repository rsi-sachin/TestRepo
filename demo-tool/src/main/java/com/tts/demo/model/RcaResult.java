package com.tts.demo.model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Root Cause Analysis result for a failed VoLTE call test.
 * Contains diagnostic information, affected network elements, and recommendations.
 */
public class RcaResult {
    private String runId;
    private FailurePoint failurePoint;
    private FailureType failureType;
    private FailureMechanism failureMechanism;  // HOW the failure occurred (new May 13, 2026)
    private String affectedNode;           // e.g., "P-CSCF", "HSS", "S-CSCF"
    private String rootCause;              // Human-readable diagnosis
    private List<String> evidence;         // Supporting facts (response codes, timing)
    private List<String> recommendations;  // Suggested fixes
    private int failureMessageIndex;       // Index in message list for diagram highlighting
    private LocalDateTime analysisTime;
    
    public RcaResult() {
        this.evidence = new ArrayList<>();
        this.recommendations = new ArrayList<>();
        this.analysisTime = LocalDateTime.now();
        this.failureMessageIndex = -1;
    }
    
    public RcaResult(String runId) {
        this();
        this.runId = runId;
    }
    
    // Getters and setters
    public String getRunId() {
        return runId;
    }
    
    public void setRunId(String runId) {
        this.runId = runId;
    }
    
    public FailurePoint getFailurePoint() {
        return failurePoint;
    }
    
    public void setFailurePoint(FailurePoint failurePoint) {
        this.failurePoint = failurePoint;
    }
    
    public FailureType getFailureType() {
        return failureType;
    }
    
    public void setFailureType(FailureType failureType) {
        this.failureType = failureType;
    }
    
    public FailureMechanism getFailureMechanism() {
        return failureMechanism;
    }
    
    public void setFailureMechanism(FailureMechanism failureMechanism) {
        this.failureMechanism = failureMechanism;
    }
    
    public String getAffectedNode() {
        return affectedNode;
    }
    
    public void setAffectedNode(String affectedNode) {
        this.affectedNode = affectedNode;
    }
    
    public String getRootCause() {
        return rootCause;
    }
    
    public void setRootCause(String rootCause) {
        this.rootCause = rootCause;
    }
    
    public List<String> getEvidence() {
        return evidence;
    }
    
    public void setEvidence(List<String> evidence) {
        this.evidence = evidence;
    }
    
    public void addEvidence(String item) {
        this.evidence.add(item);
    }
    
    public List<String> getRecommendations() {
        return recommendations;
    }
    
    public void setRecommendations(List<String> recommendations) {
        this.recommendations = recommendations;
    }
    
    public void addRecommendation(String recommendation) {
        this.recommendations.add(recommendation);
    }
    
    public int getFailureMessageIndex() {
        return failureMessageIndex;
    }
    
    public void setFailureMessageIndex(int failureMessageIndex) {
        this.failureMessageIndex = failureMessageIndex;
    }
    
    public LocalDateTime getAnalysisTime() {
        return analysisTime;
    }
    
    public void setAnalysisTime(LocalDateTime analysisTime) {
        this.analysisTime = analysisTime;
    }
    
    /**
     * Check if RCA analysis found a valid failure
     */
    public boolean hasFailure() {
        return failurePoint != null && failurePoint != FailurePoint.UNKNOWN;
    }
    
    /**
     * Get formatted summary for display
     */
    public String getSummary() {
        if (!hasFailure()) {
            return "No failure detected or analysis incomplete";
        }
        return String.format("%s failure at %s stage", 
            failureType.getDisplayName(), 
            failurePoint.getDisplayName());
    }
    
    @Override
    public String toString() {
        return String.format("RcaResult[runId=%s, point=%s, type=%s, node=%s]",
            runId, failurePoint, failureType, affectedNode);
    }
}
