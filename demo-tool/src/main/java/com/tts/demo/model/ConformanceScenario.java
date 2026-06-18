package com.tts.demo.model;

/**
 * 3GPP conformance test scenarios for failure injection.
 * Based on 3GPP TS 24.229 (IMS Call Control), TS 23.228 (IMS Architecture).
 * 
 * Each scenario represents a specific protocol conformance issue that can be
 * injected during traffic generation for testing and fix identification.
 * 
 * Added May 13, 2026 for traffic generation with 3GPP conformance testing.
 */
public enum ConformanceScenario {
    
    // === SIP Protocol Conformance (3GPP TS 24.229) ===
    
    INVALID_SIP_URI(
        "CONF-SIP-001",
        "Invalid SIP URI Format",
        "SIP URI violates RFC 3261 syntax (missing angle brackets, invalid characters)",
        ActorType.P_CSCF,
        "400 Bad Request"
    ),
    
    MISSING_MANDATORY_HEADER(
        "CONF-SIP-002",
        "Missing Mandatory SIP Header",
        "INVITE missing required headers (From, To, Call-ID, CSeq, Via)",
        ActorType.P_CSCF,
        "400 Bad Request"
    ),
    
    INVALID_CSEQ_NUMBER(
        "CONF-SIP-003",
        "Invalid CSeq Number Sequence",
        "CSeq number not incrementing or out of sequence",
        ActorType.S_CSCF,
        "400 Bad Request"
    ),
    
    MALFORMED_SDP_OFFER(
        "CONF-SIP-004",
        "Malformed SDP in INVITE",
        "SDP body violates RFC 4566 (missing session name, invalid media format)",
        ActorType.P_CSCF,
        "488 Not Acceptable Here"
    ),
    
    // === Authentication Conformance (3GPP TS 33.203) ===
    
    INVALID_AUTH_HEADER(
        "CONF-AUTH-001",
        "Invalid Authentication Header",
        "Authorization header missing required parameters (realm, nonce, response)",
        ActorType.P_CSCF,
        "401 Unauthorized"
    ),
    
    EXPIRED_NONCE(
        "CONF-AUTH-002",
        "Expired Authentication Nonce",
        "Nonce expired, requires fresh authentication challenge",
        ActorType.P_CSCF,
        "401 Unauthorized"
    ),
    
    WRONG_CREDENTIALS(
        "CONF-AUTH-003",
        "Incorrect Subscriber Credentials",
        "Authentication response does not match expected value (XRES mismatch)",
        ActorType.HSS,
        "403 Forbidden"
    ),
    
    // === Registration Conformance (3GPP TS 24.229 Section 5.1) ===
    
    REGISTRATION_TIMEOUT(
        "CONF-REG-001",
        "Registration Timeout",
        "No 200 OK received within T1 timer (default 500ms * 64 = 32s)",
        ActorType.S_CSCF,
        "408 Request Timeout"
    ),
    
    INVALID_CONTACT_HEADER(
        "CONF-REG-002",
        "Invalid Contact Header in REGISTER",
        "Contact header missing required parameters (+g.3gpp.icsi-ref)",
        ActorType.P_CSCF,
        "400 Bad Request"
    ),
    
    REGISTRATION_REJECTED_NOT_PROVISIONED(
        "CONF-REG-003",
        "User Not Provisioned in HSS",
        "Subscriber not found in HSS database (IMPU not provisioned)",
        ActorType.HSS,
        "403 Forbidden"
    ),
    
    // === Session Setup Conformance (3GPP TS 24.229 Section 5.2) ===
    
    INVITE_TIMEOUT(
        "CONF-CALL-001",
        "INVITE Timeout - No 100 Trying",
        "No provisional response (100 Trying) received within Timer B (32s)",
        ActorType.S_CSCF,
        "408 Request Timeout"
    ),
    
    PRECONDITION_FAILURE(
        "CONF-CALL-002",
        "QoS Precondition Not Met",
        "Bearer establishment failed, QoS preconditions not satisfied (RFC 3312)",
        ActorType.P_GW,
        "580 Precondition Failure"
    ),
    
    RESOURCE_ALLOCATION_FAILURE(
        "CONF-CALL-003",
        "Media Resource Allocation Failed",
        "TAS unable to allocate media resources for call",
        ActorType.TAS,
        "503 Service Unavailable"
    ),
    
    INCOMPATIBLE_MEDIA(
        "CONF-CALL-004",
        "Incompatible Media Codecs",
        "No common codec in SDP offer/answer exchange",
        ActorType.UE_SERVER,
        "488 Not Acceptable Here"
    ),
    
    // === Call Termination Conformance (3GPP TS 24.229 Section 5.3) ===
    
    BYE_TIMEOUT(
        "CONF-TERM-001",
        "BYE Request Timeout",
        "No response to BYE within Timer F (32s)",
        ActorType.S_CSCF,
        "408 Request Timeout"
    ),
    
    // === Routing Conformance (3GPP TS 23.228 Section 5.6) ===
    
    ROUTING_FAILURE_USER_NOT_FOUND(
        "CONF-ROUTE-001",
        "Called User Not Registered",
        "S-CSCF unable to find subscriber location (not registered)",
        ActorType.S_CSCF,
        "480 Temporarily Unavailable"
    ),
    
    ROUTING_FAILURE_NO_PATH(
        "CONF-ROUTE-002",
        "No Route to Destination",
        "I-CSCF unable to route to serving network",
        ActorType.I_CSCF,
        "404 Not Found"
    ),
    
    // === Emergency Call Conformance (3GPP TS 24.229 Section 5.4) ===
    
    EMERGENCY_CALL_REJECTION(
        "CONF-EMERG-001",
        "Emergency Call Not Allowed",
        "Emergency service not enabled for subscriber or network",
        ActorType.S_CSCF,
        "380 Alternative Service"
    ),
    
    // === No Failure (Control) ===
    
    NONE(
        "CONF-NONE",
        "No Failure - Normal Flow",
        "Control scenario with no injected failures",
        ActorType.UNKNOWN,
        "200 OK"
    );
    
    private final String scenarioId;
    private final String scenarioName;
    private final String description;
    private final ActorType affectedNode;
    private final String expectedResponse;
    
    ConformanceScenario(String scenarioId, String scenarioName, String description, 
                        ActorType affectedNode, String expectedResponse) {
        this.scenarioId = scenarioId;
        this.scenarioName = scenarioName;
        this.description = description;
        this.affectedNode = affectedNode;
        this.expectedResponse = expectedResponse;
    }
    
    public String getScenarioId() {
        return scenarioId;
    }
    
    public String getScenarioName() {
        return scenarioName;
    }
    
    public String getDescription() {
        return description;
    }
    
    public ActorType getAffectedNode() {
        return affectedNode;
    }
    
    public String getExpectedResponse() {
        return expectedResponse;
    }
    
    /**
     * Get display string for UI dropdown
     */
    public String getDisplayString() {
        return String.format("%s - %s (%s)", scenarioId, scenarioName, affectedNode.getDisplayName());
    }
    
    /**
     * Find scenario by ID
     */
    public static ConformanceScenario fromId(String id) {
        for (ConformanceScenario scenario : values()) {
            if (scenario.scenarioId.equals(id)) {
                return scenario;
            }
        }
        return NONE;
    }
}
