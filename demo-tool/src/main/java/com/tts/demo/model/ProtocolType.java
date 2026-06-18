package com.tts.demo.model;

import javafx.scene.paint.Color;

/**
 * Represents protocol types used in telecom testing scenarios.
 * Each protocol has associated metadata for visualization (Phase 2).
 */
public enum ProtocolType {
    // SIP/IMS Protocols
    SIP("SIP", "Session Initiation Protocol", Color.rgb(52, 152, 219), "IMS Core signaling"),
    
    // Diameter Interfaces (3GPP specifications)
    DIAMETER_CX("Diameter-Cx", "S-CSCF ↔ HSS interface", Color.rgb(231, 76, 60), "User profile & authentication"),
    DIAMETER_RX("Diameter-Rx", "P-CSCF ↔ PCRF interface", Color.rgb(155, 89, 182), "Policy control"),
    DIAMETER_GX("Diameter-Gx", "PCRF ↔ P-GW interface", Color.rgb(52, 73, 94), "Bearer control"),
    DIAMETER_S6A("Diameter-S6a", "MME ↔ HSS interface", Color.rgb(230, 126, 34), "LTE subscriber data"),
    DIAMETER_RO("Diameter-Ro", "P-CSCF ↔ OCS interface", Color.rgb(26, 188, 156), "Online charging"),
    DIAMETER_SH("Diameter-Sh", "TAS ↔ HSS interface", Color.rgb(241, 196, 15), "Application server data"),
    
    // RADIUS
    RADIUS("RADIUS", "Remote Authentication Dial-In User Service", Color.rgb(149, 165, 166), "AAA protocol"),
    
    // HTTP/REST APIs
    HTTP("HTTP", "Hypertext Transfer Protocol", Color.rgb(39, 174, 96), "Web APIs"),
    
    // Media Protocols
    RTP("RTP", "Real-time Transport Protocol", Color.rgb(142, 68, 173), "Voice/video media"),
    RTCP("RTCP", "RTP Control Protocol", Color.rgb(192, 57, 43), "Media quality control"),
    
    // Generic/Unknown
    OTHER("Other", "Other protocol", Color.rgb(127, 140, 141), "Unspecified protocol");

    private final String displayName;
    private final String description;
    private final Color color;
    private final String usage;

    ProtocolType(String displayName, String description, Color color, String usage) {
        this.displayName = displayName;
        this.description = description;
        this.color = color;
        this.usage = usage;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getDescription() {
        return description;
    }

    public Color getColor() {
        return color;
    }

    public String getUsage() {
        return usage;
    }

    /**
     * Infer protocol type from JMeter sampler label
     * 
     * @param label The JMeter sampler label (e.g., "Send INVITE", "CCR Request")
     * @return Detected protocol type
     */
    public static ProtocolType fromLabel(String label) {
        if (label == null) return OTHER;
        
        String upper = label.toUpperCase();
        
        // SIP message patterns
        if (upper.contains("INVITE") || upper.contains("BYE") || upper.contains("ACK") 
            || upper.contains("TRYING") || upper.contains("RINGING") || upper.contains("SIP")) {
            return SIP;
        }
        
        // Diameter patterns
        if (upper.contains("UAR") || upper.contains("UAA") || upper.contains("SAR") 
            || upper.contains("SAA") || upper.contains("LIR") || upper.contains("LIA")
            || upper.contains("MAR") || upper.contains("MAA")) {
            return DIAMETER_CX;
        }
        
        if (upper.contains("AAR") || upper.contains("AAA") || upper.contains("STR") 
            || upper.contains("STA") && upper.contains("RX")) {
            return DIAMETER_RX;
        }
        
        if (upper.contains("CCR") || upper.contains("CCA")) {
            if (upper.contains("GX")) {
                return DIAMETER_GX;
            } else if (upper.contains("RO") || upper.contains("CHARGING")) {
                return DIAMETER_RO;
            }
        }
        
        if (upper.contains("AIR") || upper.contains("AIA") || upper.contains("ULR") 
            || upper.contains("ULA") || upper.contains("CLR") || upper.contains("CLA")
            || upper.contains("IDR") || upper.contains("IDA") || upper.contains("DSR") 
            || upper.contains("DSA") || upper.contains("S6A")) {
            return DIAMETER_S6A;
        }
        
        if (upper.contains("PUR") || upper.contains("PUA") || upper.contains("SNR") 
            || upper.contains("SNA") || upper.contains("UDR") || upper.contains("UDA")
            || upper.contains("SH")) {
            return DIAMETER_SH;
        }
        
        // RADIUS patterns
        if (upper.contains("RADIUS") || upper.contains("ACCESS-REQUEST") 
            || upper.contains("ACCESS-ACCEPT") || upper.contains("ACCOUNTING")) {
            return RADIUS;
        }
        
        // HTTP/REST patterns
        if (upper.contains("HTTP") || upper.contains("GET") || upper.contains("POST") 
            || upper.contains("PUT") || upper.contains("DELETE") || upper.contains("REST")) {
            return HTTP;
        }
        
        // Media protocols
        if (upper.contains("RTP") && !upper.contains("RTCP")) {
            return RTP;
        }
        if (upper.contains("RTCP")) {
            return RTCP;
        }
        
        return OTHER;
    }

    /**
     * Get a lighter shade of this protocol's color for backgrounds
     */
    public Color getLightColor() {
        return Color.color(
            Math.min(1.0, color.getRed() + 0.3),
            Math.min(1.0, color.getGreen() + 0.3),
            Math.min(1.0, color.getBlue() + 0.3),
            0.3  // Semi-transparent
        );
    }
}
