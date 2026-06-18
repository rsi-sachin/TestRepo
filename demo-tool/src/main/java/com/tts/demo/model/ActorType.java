package com.tts.demo.model;

/**
 * Represents network nodes in 3GPP VoLTE architecture (Phase 3).
 * Maps simplified test actors to real network elements.
 */
public enum ActorType {
    // User Equipment
    UE_CLIENT("UE (Client)", "User Equipment - calling party", ActorRole.ENDPOINT),
    UE_SERVER("UE (Server)", "User Equipment - called party", ActorRole.ENDPOINT),
    
    // IMS Core (3GPP TS 23.228)
    P_CSCF("P-CSCF", "Proxy Call Session Control Function", ActorRole.IMS_CORE),
    I_CSCF("I-CSCF", "Interrogating CSCF", ActorRole.IMS_CORE),
    S_CSCF("S-CSCF", "Serving CSCF", ActorRole.IMS_CORE),
    
    // Application Servers
    TAS("TAS", "Telephony Application Server", ActorRole.APPLICATION_SERVER),
    MMTEL_AS("MMTel-AS", "Multimedia Telephony Application Server", ActorRole.APPLICATION_SERVER),
    
    // Subscriber & Policy
    HSS("HSS", "Home Subscriber Server", ActorRole.DATABASE),
    PCRF("PCRF", "Policy and Charging Rules Function", ActorRole.POLICY),
    OCS("OCS", "Online Charging System", ActorRole.CHARGING),
    
    // EPC/LTE Network (3GPP TS 23.401)
    MME("MME", "Mobility Management Entity", ActorRole.EPC_CORE),
    S_GW("S-GW", "Serving Gateway", ActorRole.EPC_GATEWAY),
    P_GW("P-GW", "PDN Gateway", ActorRole.EPC_GATEWAY),
    
    // Access Network
    E_NODE_B("eNodeB", "Evolved Node B (LTE base station)", ActorRole.ACCESS),
    
    // Generic/Test
    CLIENT("Client", "Generic test client", ActorRole.TEST_ACTOR),
    SERVER("Server", "Generic test server", ActorRole.TEST_ACTOR),
    UNKNOWN("Unknown", "Unknown actor", ActorRole.TEST_ACTOR);

    private final String displayName;
    private final String description;
    private final ActorRole role;

    ActorType(String displayName, String description, ActorRole role) {
        this.displayName = displayName;
        this.description = description;
        this.role = role;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getDescription() {
        return description;
    }

    public ActorRole getRole() {
        return role;
    }

    /**
     * Infer actor type from JMeter thread name or label
     * Examples:
     * - "Thread Group 1-1" -> UNKNOWN (use fromLabel instead)
     * - "A Party" or "A-Party" -> UE_CLIENT
     * - "B Party" or "B-Party" -> UE_SERVER
     * - "TAS SIM" -> TAS
     */
    public static ActorType fromThreadName(String threadName) {
        if (threadName == null) return UNKNOWN;
        
        String upper = threadName.toUpperCase().trim();
        
        // Detect party roles
        if (upper.contains("A PARTY") || upper.contains("A-PARTY") || upper.contains("APARTY")
            || upper.contains("CALLER") || upper.contains("ORIGINATING")) {
            return UE_CLIENT;
        }
        
        if (upper.contains("B PARTY") || upper.contains("B-PARTY") || upper.contains("BPARTY")
            || upper.contains("CALLEE") || upper.contains("TERMINATING")) {
            return UE_SERVER;
        }
        
        // Detect network elements
        if (upper.contains("TAS") || upper.contains("TELEPHONY APP")) {
            return TAS;
        }
        
        if (upper.contains("P-CSCF") || upper.contains("PCSCF") || upper.contains("PROXY CSCF")) {
            return P_CSCF;
        }
        
        if (upper.contains("I-CSCF") || upper.contains("ICSCF") || upper.contains("INTERROGATING")) {
            return I_CSCF;
        }
        
        if (upper.contains("S-CSCF") || upper.contains("SCSCF") || upper.contains("SERVING CSCF")) {
            return S_CSCF;
        }
        
        if (upper.contains("HSS") || upper.contains("HOME SUBSCRIBER")) {
            return HSS;
        }
        
        if (upper.contains("PCRF") || upper.contains("POLICY")) {
            return PCRF;
        }
        
        if (upper.contains("MME") || upper.contains("MOBILITY MANAGEMENT")) {
            return MME;
        }
        
        if (upper.contains("S-GW") || upper.contains("SGW") || upper.contains("SERVING GATEWAY")) {
            return S_GW;
        }
        
        if (upper.contains("P-GW") || upper.contains("PGW") || upper.contains("PDN GATEWAY")) {
            return P_GW;
        }
        
        // For generic thread groups, return UNKNOWN - caller should use fromLabel()
        return UNKNOWN;
    }
    
    /**
     * Extract actor from message label - more reliable than thread name for TTS tests
     * Examples:
     * - "Send INVITE from A Party to TAS" -> returns A Party actor (UE_CLIENT)
     * - "Listen for ERROR from TAS to A Party" -> returns TAS
     * - "Send Error to A Party" -> returns A Party (target)
     */
    public static ActorType fromLabel(String label) {
        if (label == null) return UNKNOWN;
        
        String upper = label.toUpperCase().trim();
        
        // Pattern: "from X to Y" or "from X"
        if (upper.contains(" FROM ")) {
            String afterFrom = upper.substring(upper.indexOf(" FROM ") + 6);
            String actor = afterFrom.split(" TO ")[0].trim();
            return parseActorName(actor);
        }
        
        // Pattern: "to X" (for targets)
        if (upper.contains(" TO ")) {
            String afterTo = upper.substring(upper.indexOf(" TO ") + 4).trim();
            return parseActorName(afterTo);
        }
        
        // Check if actor name is in the label itself
        return parseActorName(upper);
    }
    
    /**
     * Parse actor name from extracted text
     */
    private static ActorType parseActorName(String text) {
        if (text == null) return UNKNOWN;
        
        String upper = text.toUpperCase().trim();
        
        // Party roles
        if (upper.contains("A PARTY") || upper.contains("A-PARTY") || upper.contains("APARTY")) {
            return UE_CLIENT;
        }
        if (upper.contains("B PARTY") || upper.contains("B-PARTY") || upper.contains("BPARTY")) {
            return UE_SERVER;
        }
        
        // Network elements
        if (upper.contains("TAS") || upper.equals("TELEPHONY APP")) {
            return TAS;
        }
        if (upper.contains("P-CSCF") || upper.contains("PCSCF")) {
            return P_CSCF;
        }
        if (upper.contains("I-CSCF") || upper.contains("ICSCF")) {
            return I_CSCF;
        }
        if (upper.contains("S-CSCF") || upper.contains("SCSCF")) {
            return S_CSCF;
        }
        if (upper.contains("HSS")) {
            return HSS;
        }
        if (upper.contains("PCRF")) {
            return PCRF;
        }
        if (upper.contains("MME")) {
            return MME;
        }
        if (upper.contains("S-GW") || upper.contains("SGW")) {
            return S_GW;
        }
        if (upper.contains("P-GW") || upper.contains("PGW")) {
            return P_GW;
        }
        
        // Generic
        if (upper.contains("SERVER")) {
            return SERVER;
        }
        if (upper.contains("CLIENT")) {
            return CLIENT;
        }
        
        if (upper.contains("OCS") || upper.contains("CHARGING")) {
            return OCS;
        }
        
        if (upper.contains("ENODEB") || upper.contains("E-NODEB") || upper.contains("LTE")) {
            return E_NODE_B;
        }
        
        // Default mapping
        if (upper.contains("CLIENT") || upper.contains("SEND")) {
            return CLIENT;
        }
        
        if (upper.contains("SERVER") || upper.contains("LISTEN")) {
            return SERVER;
        }
        
        return UNKNOWN;
    }

    /**
     * Actor role categories for grouping in UI
     */
    public enum ActorRole {
        ENDPOINT("User Equipment"),
        IMS_CORE("IMS Core Network"),
        APPLICATION_SERVER("Application Servers"),
        DATABASE("Subscriber Databases"),
        POLICY("Policy & QoS"),
        CHARGING("Charging Systems"),
        EPC_CORE("EPC Core Network"),
        EPC_GATEWAY("EPC Gateways"),
        ACCESS("Access Network"),
        TEST_ACTOR("Test Simulation");

        private final String displayName;

        ActorRole(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }
    }
}
