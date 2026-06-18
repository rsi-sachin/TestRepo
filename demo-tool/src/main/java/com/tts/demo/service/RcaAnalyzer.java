package com.tts.demo.service;

import com.tts.demo.model.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Root Cause Analysis engine for VoLTE call failures.
 * Analyzes call flow messages to identify failure point, type, affected node, and root cause.
 * Uses pattern matching against known failure signatures to provide diagnostic insights.
 */
public class RcaAnalyzer {
    
    private static final Logger logger = LoggerFactory.getLogger(RcaAnalyzer.class);
    
    /**
     * Analyze a failed test run and generate RCA result
     * 
     * @param result The test run result
     * @param callFlow The call flow with message sequence
     * @return RCA result with diagnosis and recommendations
     */
    public RcaResult analyze(RunResult result, CallFlow callFlow) {
        logger.info("Starting RCA analysis for run: {}", result.getRunId());
        
        RcaResult rca = new RcaResult(result.getRunId());
        
        // Get message sequence
        List<SipMessage> messages = callFlow.getMessages();
        if (messages.isEmpty()) {
            logger.warn("No messages available for RCA analysis");
            rca.setFailurePoint(FailurePoint.UNKNOWN);
            rca.setFailureType(FailureType.UNKNOWN);
            rca.setRootCause("No call flow data available for analysis");
            return rca;
        }
        
        // Find last successful message and first failed message
        SipMessage lastSuccess = null;
        SipMessage firstFailure = null;
        int failureIndex = -1;
        
        for (int i = 0; i < messages.size(); i++) {
            SipMessage msg = messages.get(i);
            if (!msg.isSuccess() || isFailureCode(msg.getResponseCode())) {
                firstFailure = msg;
                failureIndex = i;
                break;
            }
            lastSuccess = msg;
        }
        
        // If no explicit failure found, check if call flow is incomplete
        if (firstFailure == null && messages.size() < 10) {
            // Incomplete call flow - likely timed out waiting for response
            firstFailure = messages.get(messages.size() - 1);
            failureIndex = messages.size() - 1;
        }
        
        if (firstFailure == null) {
            logger.warn("No failure detected in message sequence");
            rca.setFailurePoint(FailurePoint.UNKNOWN);
            rca.setFailureType(FailureType.UNKNOWN);
            rca.setRootCause("Test marked as failed but no failed messages found");
            return rca;
        }
        
        rca.setFailureMessageIndex(failureIndex);
        
        // Classify failure point based on message type
        FailurePoint failurePoint = classifyFailurePoint(firstFailure, lastSuccess);
        rca.setFailurePoint(failurePoint);
        
        // Determine failure type from response code and timing
        FailureType failureType = classifyFailureType(firstFailure);
        rca.setFailureType(failureType);
        
        // NEW: Determine HOW the failure occurred (mechanism)
        FailureMechanism failureMechanism = determineFailureMechanism(firstFailure, lastSuccess, messages);
        rca.setFailureMechanism(failureMechanism);
        
        // Identify affected node
        String affectedNode = identifyAffectedNode(firstFailure);
        rca.setAffectedNode(affectedNode);
        
        // Build evidence list
        buildEvidence(rca, firstFailure, lastSuccess);
        
        // Generate diagnosis using pattern matching (now includes mechanism)
        generateDiagnosis(rca, failurePoint, failureType, failureMechanism, firstFailure);
        
        // Generate recommendations
        generateRecommendations(rca, failurePoint, failureType);
        
        logger.info("RCA analysis complete: {} at {} via {} ({})", 
            failureType.getDisplayName(), 
            failurePoint.getDisplayName(),
            failureMechanism.getDisplayName(),
            affectedNode);
        
        return rca;
    }
    
    /**
     * Classify where in the call flow the failure occurred
     */
    private FailurePoint classifyFailurePoint(SipMessage failedMsg, SipMessage lastSuccess) {
        SipMessage.MessageType failedType = failedMsg.getMessageType();
        SipMessage.MessageType lastType = lastSuccess != null ? lastSuccess.getMessageType() : null;
        
        // Based on the failed message type
        switch (failedType) {
            case REGISTER:
                return FailurePoint.REGISTRATION;
            case INVITE:
                return lastType == SipMessage.MessageType.INVITE ? 
                    FailurePoint.INVITE_RESPONSE : FailurePoint.INVITE_SEND;
            case TRYING:
                return FailurePoint.TRYING_RESPONSE;
            case RINGING:
                return FailurePoint.RINGING_WAIT;
            case OK:
                return FailurePoint.ANSWER_WAIT;
            case ACK:
                return FailurePoint.ACK_SEND;
            case BYE:
                return lastType == SipMessage.MessageType.BYE ? 
                    FailurePoint.BYE_RESPONSE : FailurePoint.BYE_SEND;
            default:
                // Try to infer from last successful message
                if (lastType != null) {
                    switch (lastType) {
                        case INVITE:
                            return FailurePoint.TRYING_RESPONSE;
                        case TRYING:
                            return FailurePoint.RINGING_WAIT;
                        case RINGING:
                            return FailurePoint.ANSWER_WAIT;
                        case OK:
                            return FailurePoint.ACK_SEND;
                    }
                }
                return FailurePoint.UNKNOWN;
        }
    }
    
    /**
     * Classify the type of failure from response code and timing
     */
    private FailureType classifyFailureType(SipMessage failedMsg) {
        String code = failedMsg.getResponseCode();
        
        // Authentication failures
        if ("401".equals(code) || "403".equals(code) || "407".equals(code)) {
            return FailureType.AUTHENTICATION_FAILURE;
        }
        
        // Resource unavailable
        if ("480".equals(code) || "486".equals(code) || "503".equals(code)) {
            return FailureType.RESOURCE_UNAVAILABLE;
        }
        
        // 4xx client errors
        if (code != null && code.startsWith("4")) {
            return FailureType.REJECTION_4XX;
        }
        
        // 5xx server errors
        if (code != null && code.startsWith("5")) {
            return FailureType.REJECTION_5XX;
        }
        
        // Timeout - high elapsed time or no response code
        if (failedMsg.getElapsed() > 5000 || code == null || code.isEmpty() || "0".equals(code)) {
            return FailureType.TIMEOUT;
        }
        
        // Protocol error for malformed messages
        if ("400".equals(code)) {
            return FailureType.PROTOCOL_ERROR;
        }
        
        return FailureType.UNKNOWN;
    }
    
    /**
     * NEW: Determine HOW the failure occurred (the failure mechanism)
     * This answers: Was it an unsolicited message? Missing message? Incorrect content?
     * Added May 13, 2026 to improve RCA explanatory quality
     */
    private FailureMechanism determineFailureMechanism(SipMessage failedMsg, SipMessage lastSuccess, List<SipMessage> allMessages) {
        String label = failedMsg.getLabel();
        String code = failedMsg.getResponseCode();
        
        // MECHANISM 1: Unsolicited ERROR/REJECT message
        // Label contains "ERROR", "REJECT", "FAIL" but response code is 200 (success)
        if (label != null && code != null && code.startsWith("2")) {
            String upperLabel = label.toUpperCase();
            if (upperLabel.contains("ERROR") || upperLabel.contains("REJECT") || upperLabel.contains("FAIL")) {
                logger.info("Detected unsolicited error message: {}", label);
                return FailureMechanism.UNSOLICITED_ERROR_MESSAGE;
            }
        }
        
        // MECHANISM 2: Response code rejection (explicit error code)
        if (code != null && (code.startsWith("4") || code.startsWith("5") || code.startsWith("6"))) {
            return FailureMechanism.RESPONSE_CODE_REJECTION;
        }
        
        // MECHANISM 3: Timeout - no response received
        if (failedMsg.getElapsed() > 5000 || code == null || code.isEmpty() || "0".equals(code)) {
            return FailureMechanism.TIMEOUT_NO_RESPONSE;
        }
        
        // MECHANISM 4: Missing expected message (call flow incomplete)
        if (allMessages.size() < 6) {  // Normal VoLTE call has ~8-12 messages
            // Check if we're missing expected responses
            boolean hasInvite = allMessages.stream().anyMatch(m -> m.getMessageType() == SipMessage.MessageType.INVITE);
            boolean has200OK = allMessages.stream().anyMatch(m -> m.getResponseCode() != null && m.getResponseCode().equals("200"));
            
            if (hasInvite && !has200OK) {
                return FailureMechanism.MISSING_EXPECTED_MESSAGE;
            }
        }
        
        // MECHANISM 5: Sequence violation (message out of order)
        // E.g., ACK before 200 OK, BYE before call established
        if (lastSuccess != null) {
            if (failedMsg.getMessageType() == SipMessage.MessageType.ACK && 
                lastSuccess.getMessageType() != SipMessage.MessageType.OK) {
                return FailureMechanism.SEQUENCE_VIOLATION;
            }
            if (failedMsg.getMessageType() == SipMessage.MessageType.BYE && 
                lastSuccess.getMessageType() == SipMessage.MessageType.INVITE) {
                return FailureMechanism.SEQUENCE_VIOLATION;
            }
        }
        
        // MECHANISM 6: Protocol malformation
        if ("400".equals(code)) {
            return FailureMechanism.PROTOCOL_MALFORMATION;
        }
        
        // Default: treat as incorrect content if we can't determine specific mechanism
        return FailureMechanism.INCORRECT_MESSAGE_CONTENT;
    }
    
    /**
     * Identify which network node is affected
     */
    private String identifyAffectedNode(SipMessage failedMsg) {
        ActorType targetActor = failedMsg.getTargetActor();
        ActorType sourceActor = failedMsg.getSourceActor();
        String label = failedMsg.getLabel();
        
        // For error responses, the target is the affected node
        if (targetActor != null && targetActor != ActorType.UNKNOWN) {
            return targetActor.getDisplayName();
        }
        
        // For timeouts or missing responses, source is waiting for target
        if (sourceActor != null && sourceActor != ActorType.UNKNOWN) {
            return sourceActor.getDisplayName();
        }
        
        // Last resort: try to extract from label directly
        if (label != null) {
            ActorType fromLabel = ActorType.fromLabel(label);
            if (fromLabel != ActorType.UNKNOWN) {
                return fromLabel.getDisplayName();
            }
        }
        
        return "Unidentified Node (check message label: '" + (label != null ? label : "null") + "')";
    }
    
    /**
     * Build evidence list with facts about the failure
     */
    private void buildEvidence(RcaResult rca, SipMessage failedMsg, SipMessage lastSuccess) {
        // Response code evidence
        String code = failedMsg.getResponseCode();
        if (code != null && !code.isEmpty() && !"0".equals(code)) {
            rca.addEvidence(String.format("Received SIP response code: %s (%s)", 
                code, getResponseCodeDescription(code)));
        }
        
        // Timing evidence
        if (failedMsg.getElapsed() > 1000) {
            rca.addEvidence(String.format("Response time: %d ms (exceeded threshold)", 
                failedMsg.getElapsed()));
        }
        
        // Message type evidence
        rca.addEvidence(String.format("Failed at message type: %s", 
            failedMsg.getMessageType().getDisplayName()));
        
        // Last successful message
        if (lastSuccess != null) {
            rca.addEvidence(String.format("Last successful message: %s", 
                lastSuccess.getMessageType().getDisplayName()));
        }
        
        // Direction evidence with source and target
        String directionInfo;
        if (failedMsg.getSourceActor() != ActorType.UNKNOWN && failedMsg.getTargetActor() != ActorType.UNKNOWN) {
            directionInfo = String.format("Communication: %s → %s", 
                failedMsg.getSourceActor().getDisplayName(),
                failedMsg.getTargetActor().getDisplayName());
        } else if (failedMsg.getDirection() != null && failedMsg.getDirection() != SipMessage.Direction.UNKNOWN) {
            directionInfo = String.format("Direction: %s", failedMsg.getDirection().getDisplayName());
        } else {
            directionInfo = "Direction: Unable to determine from message data";
        }
        rca.addEvidence(directionInfo);
    }
    
    /**
     * Generate human-readable diagnosis using pattern matching
     * Now includes failure mechanism to explain HOW the failure occurred
     */
    private void generateDiagnosis(RcaResult rca, FailurePoint point, FailureType type, FailureMechanism mechanism, SipMessage failedMsg) {
        String code = failedMsg.getResponseCode();
        String label = failedMsg.getLabel();
        String diagnosis;
        
        // NEW: Add mechanism explanation as prefix
        String mechanismExplanation = "";
        switch (mechanism) {
            case UNSOLICITED_ERROR_MESSAGE:
                mechanismExplanation = String.format("⚠️ Unsolicited ERROR message detected: '%s'. ", 
                    label != null ? label : "Unknown");
                break;
            case MISSING_EXPECTED_MESSAGE:
                mechanismExplanation = "⏱️ Expected message never received. ";
                break;
            case INCORRECT_MESSAGE_CONTENT:
                mechanismExplanation = "📝 Message received but contains incorrect information. ";
                break;
            case RESPONSE_CODE_REJECTION:
                mechanismExplanation = String.format("🚫 Explicit rejection (code %s). ", code);
                break;
            case TIMEOUT_NO_RESPONSE:
                mechanismExplanation = "⏱️ No response received within timeout. ";
                break;
            case SEQUENCE_VIOLATION:
                mechanismExplanation = "⚡ Message received out of expected sequence. ";
                break;
            case PROTOCOL_MALFORMATION:
                mechanismExplanation = "📛 Malformed SIP protocol message. ";
                break;
        }
        
        // Pattern matching for specific failure scenarios
        if (point == FailurePoint.REGISTRATION && type == FailureType.AUTHENTICATION_FAILURE) {
            if ("403".equals(code)) {
                diagnosis = mechanismExplanation + "HSS rejected registration - Subscriber credentials are invalid or user is not authorized for IMS services";
            } else if ("401".equals(code)) {
                diagnosis = mechanismExplanation + "Authentication challenge failed - Invalid credentials or missing authentication header";
            } else {
                diagnosis = mechanismExplanation + "Registration authentication failed - Check subscriber provisioning in HSS";
            }
        }
        else if (mechanism == FailureMechanism.UNSOLICITED_ERROR_MESSAGE) {
            // Special handling for unsolicited ERROR messages (Error Scenario test case)
            diagnosis = mechanismExplanation + 
                String.format("The network sent an ERROR message at %s stage. This indicates " +
                             "%s detected a problem and is explicitly signaling failure to %s. " +
                             "This is typically used to simulate fault conditions in testing.",
                    point.getDisplayName(),
                    failedMsg.getSourceActor().getDisplayName(),
                    failedMsg.getTargetActor().getDisplayName());
        }
        else if (point == FailurePoint.INVITE_RESPONSE && type == FailureType.RESOURCE_UNAVAILABLE) {
            if ("480".equals(code)) {
                diagnosis = mechanismExplanation + "Callee temporarily unavailable - S-CSCF routing issue or user not registered";
            } else if ("486".equals(code)) {
                diagnosis = mechanismExplanation + "Callee is busy - User is in another call or has Do Not Disturb enabled";
            } else {
                diagnosis = mechanismExplanation + "Call setup failed - Target user or network resource unavailable";
            }
        }
        else if (point == FailurePoint.RINGING_WAIT && type == FailureType.TIMEOUT) {
            diagnosis = mechanismExplanation + "P-CSCF not forwarding 180 RINGING response - Possible P-CSCF failure or network congestion";
        }
        else if (point == FailurePoint.ANSWER_WAIT && type == FailureType.TIMEOUT) {
            diagnosis = mechanismExplanation + "Callee did not answer (No 200 OK received) - User did not pick up or device offline";
        }
        else if (type == FailureType.TIMEOUT) {
            diagnosis = mechanismExplanation + 
                String.format("Request timed out at %s stage - Network latency or node unresponsive", 
                    point.getDisplayName());
        }
        else if (type == FailureType.REJECTION_5XX) {
            diagnosis = mechanismExplanation + 
                String.format("Server error at %s - Network element experienced internal failure", 
                    rca.getAffectedNode());
        }
        else if (type == FailureType.PROTOCOL_ERROR) {
            diagnosis = mechanismExplanation + "SIP protocol violation - Malformed message or unsupported feature";
        }
        else {
            // Generic diagnosis - avoid text repetition
            if (type == FailureType.UNKNOWN) {
                diagnosis = mechanismExplanation + 
                    String.format("Failure detected at %s stage involving %s - Unable to determine specific cause from available data", 
                        point.getDisplayName(), 
                        rca.getAffectedNode());
            } else {
                diagnosis = mechanismExplanation + 
                    String.format("%s at %s stage involving %s", 
                        type.getDisplayName(), 
                        point.getDisplayName(), 
                        rca.getAffectedNode());
            }
        }
        
        rca.setRootCause(diagnosis);
    }
    
    /**
     * Generate actionable recommendations for fixing the issue
     */
    private void generateRecommendations(RcaResult rca, FailurePoint point, FailureType type) {
        switch (type) {
            case AUTHENTICATION_FAILURE:
                rca.addRecommendation("Verify subscriber credentials (IMSI, IMPU, private identity) in HSS");
                rca.addRecommendation("Check if subscriber is provisioned for IMS/VoLTE services");
                rca.addRecommendation("Review authentication vectors (RAND, AUTN, XRES) generation");
                rca.addRecommendation("Confirm shared secrets between network elements");
                break;
                
            case TIMEOUT:
                rca.addRecommendation("Check network connectivity between " + rca.getAffectedNode() + " and adjacent nodes");
                rca.addRecommendation("Verify " + rca.getAffectedNode() + " is running and responsive");
                rca.addRecommendation("Review firewall rules and routing tables");
                rca.addRecommendation("Increase timeout parameters if network latency is expected");
                break;
                
            case RESOURCE_UNAVAILABLE:
                rca.addRecommendation("Verify target subscriber is registered in S-CSCF");
                rca.addRecommendation("Check S-CSCF routing tables for correct subscriber location");
                rca.addRecommendation("Review HSS subscriber profile for service enablement");
                rca.addRecommendation("Confirm network capacity and resource availability");
                break;
                
            case REJECTION_5XX:
                rca.addRecommendation("Review " + rca.getAffectedNode() + " error logs for detailed failure reason");
                rca.addRecommendation("Check database connectivity (HSS/PCRF/OCS)");
                rca.addRecommendation("Verify system resources (CPU, memory, disk) on " + rca.getAffectedNode());
                rca.addRecommendation("Restart " + rca.getAffectedNode() + " service if persistent");
                break;
                
            case PROTOCOL_ERROR:
                rca.addRecommendation("Review SIP message format and mandatory headers");
                rca.addRecommendation("Check protocol version compatibility between nodes");
                rca.addRecommendation("Validate SDP content if media negotiation failed");
                rca.addRecommendation("Enable detailed protocol tracing for debugging");
                break;
                
            default:
                rca.addRecommendation("Review test configuration parameters");
                rca.addRecommendation("Check JTL log file for detailed error messages");
                rca.addRecommendation("Enable debug logging on network elements");
                rca.addRecommendation("Verify test environment setup and prerequisites");
        }
    }
    
    /**
     * Check if response code indicates failure
     */
    private boolean isFailureCode(String code) {
        if (code == null || code.isEmpty()) {
            return false;
        }
        try {
            int codeInt = Integer.parseInt(code);
            return codeInt >= 400; // 4xx and 5xx are failures
        } catch (NumberFormatException e) {
            return false;
        }
    }
    
    /**
     * Get human-readable description for SIP response code
     */
    private String getResponseCodeDescription(String code) {
        Map<String, String> descriptions = new HashMap<>();
        descriptions.put("400", "Bad Request");
        descriptions.put("401", "Unauthorized");
        descriptions.put("403", "Forbidden");
        descriptions.put("404", "Not Found");
        descriptions.put("407", "Proxy Authentication Required");
        descriptions.put("408", "Request Timeout");
        descriptions.put("480", "Temporarily Unavailable");
        descriptions.put("486", "Busy Here");
        descriptions.put("487", "Request Terminated");
        descriptions.put("500", "Internal Server Error");
        descriptions.put("503", "Service Unavailable");
        descriptions.put("504", "Server Timeout");
        
        return descriptions.getOrDefault(code, "Error");
    }
}
