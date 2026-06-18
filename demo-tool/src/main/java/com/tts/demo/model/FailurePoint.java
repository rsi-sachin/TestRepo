package com.tts.demo.model;

/**
 * Represents specific points in a VoLTE call flow where failures can occur.
 * Used by RCA engine to classify where in the call sequence the failure happened.
 */
public enum FailurePoint {
    REGISTRATION("Registration", "Initial UE registration with IMS network"),
    INVITE_SEND("Invite Send", "Client sending INVITE request"),
    INVITE_RESPONSE("Invite Response", "Server processing INVITE"),
    TRYING_RESPONSE("100 Trying", "Provisional response to INVITE"),
    RINGING_WAIT("Ringing Wait", "Waiting for 180 RINGING response"),
    ANSWER_WAIT("Answer Wait", "Waiting for 200 OK response"),
    ACK_SEND("ACK Send", "Client sending ACK to confirm call"),
    CALL_ACTIVE("Call Active", "During active call session"),
    BYE_SEND("BYE Send", "Client sending BYE to terminate"),
    BYE_RESPONSE("BYE Response", "Server processing BYE request"),
    UNKNOWN("Unknown", "Unable to determine failure point");
    
    private final String displayName;
    private final String description;
    
    FailurePoint(String displayName, String description) {
        this.displayName = displayName;
        this.description = description;
    }
    
    public String getDisplayName() {
        return displayName;
    }
    
    public String getDescription() {
        return description;
    }
}
