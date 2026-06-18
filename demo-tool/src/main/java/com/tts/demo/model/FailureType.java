package com.tts.demo.model;

/**
 * Categories of failures that can occur in VoLTE calls.
 * Used by RCA engine to classify the nature of the failure.
 */
public enum FailureType {
    TIMEOUT("Timeout", "Request timed out waiting for response", "⏱️"),
    REJECTION_4XX("Client Error (4xx)", "Request rejected due to client error", "🚫"),
    REJECTION_5XX("Server Error (5xx)", "Request failed due to server error", "⚠️"),
    PROTOCOL_ERROR("Protocol Error", "SIP protocol violation or malformed message", "📛"),
    NETWORK_ERROR("Network Error", "Network connectivity or transport issue", "🔌"),
    AUTHENTICATION_FAILURE("Authentication Failure", "Credentials rejected by network", "🔒"),
    RESOURCE_UNAVAILABLE("Resource Unavailable", "Required network resource not available", "📵"),
    UNKNOWN("Unknown Failure", "Unable to determine failure type", "❓");
    
    private final String displayName;
    private final String description;
    private final String icon;
    
    FailureType(String displayName, String description, String icon) {
        this.displayName = displayName;
        this.description = description;
        this.icon = icon;
    }
    
    public String getDisplayName() {
        return displayName;
    }
    
    public String getDescription() {
        return description;
    }
    
    public String getIcon() {
        return icon;
    }
}
