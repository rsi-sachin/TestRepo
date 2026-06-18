package com.tts.demo.model;

/**
 * Describes HOW the failure occurred - the failure mechanism.
 * Different from FailureType (WHAT failed) and FailurePoint (WHERE it failed).
 * 
 * Added May 13, 2026 to address RCA quality issues:
 * - "RCA does not mention if an unsolicited message is observed"
 * - "or an expected message is not observed"  
 * - "or a message is observed at expected sequence of time but with incorrect information"
 */
public enum FailureMechanism {
    UNSOLICITED_ERROR_MESSAGE(
        "Unsolicited Error Message", 
        "An ERROR or REJECT message was received that was not expected in normal call flow"
    ),
    
    MISSING_EXPECTED_MESSAGE(
        "Missing Expected Message",
        "An expected message (e.g., 180 RINGING, 200 OK) was never received within timeout period"
    ),
    
    INCORRECT_MESSAGE_CONTENT(
        "Incorrect Message Content",
        "Message was received but contained incorrect or invalid information"
    ),
    
    RESPONSE_CODE_REJECTION(
        "Response Code Rejection",
        "Received explicit rejection response code (4xx, 5xx, 6xx)"
    ),
    
    TIMEOUT_NO_RESPONSE(
        "Timeout - No Response",
        "Request sent but no response received within expected time window"
    ),
    
    SEQUENCE_VIOLATION(
        "Call Flow Sequence Violation",
        "Message received out of expected sequence or at wrong stage of call setup"
    ),
    
    PROTOCOL_MALFORMATION(
        "Protocol Malformation",
        "Message violated SIP protocol specification or had malformed headers"
    ),
    
    NORMAL_FLOW(
        "Normal Flow",
        "No failure mechanism detected - call completed normally"
    );
    
    private final String displayName;
    private final String explanation;
    
    FailureMechanism(String displayName, String explanation) {
        this.displayName = displayName;
        this.explanation = explanation;
    }
    
    public String getDisplayName() {
        return displayName;
    }
    
    public String getExplanation() {
        return explanation;
    }
}
