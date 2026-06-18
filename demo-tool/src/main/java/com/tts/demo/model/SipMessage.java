package com.tts.demo.model;

import java.util.Objects;

/**
 * Represents a single SIP message in a VoLTE call flow.
 * Extracted from JTL test results for visualization.
 * Enhanced with actor and protocol information for multi-node visualization (Phase 1, Phase 2).
 */
public class SipMessage {
    
    private MessageType messageType;
    private Direction direction;
    private String threadName;
    private long timestamp;
    private long elapsed;
    private boolean success;
    private String responseCode;
    private String label;
    
    // Phase 1: Multi-actor support
    private ActorType sourceActor;
    private ActorType targetActor;
    
    // Phase 2: Protocol annotation
    private ProtocolType protocolType;

    public SipMessage() {
        this.sourceActor = ActorType.UNKNOWN;
        this.targetActor = ActorType.UNKNOWN;
        this.protocolType = ProtocolType.SIP;  // Default to SIP
    }

    public SipMessage(MessageType messageType, Direction direction, String threadName,
                     long timestamp, long elapsed, boolean success, String responseCode, String label) {
        this.messageType = messageType;
        this.direction = direction;
        this.threadName = threadName;
        this.timestamp = timestamp;
        this.elapsed = elapsed;
        this.success = success;
        this.responseCode = responseCode;
        this.label = label;
        
        // Auto-detect actor and protocol from label (more reliable than thread name)
        this.sourceActor = extractSourceFromLabel(label, threadName);
        this.targetActor = extractTargetFromLabel(label, direction, sourceActor);
        this.protocolType = ProtocolType.fromLabel(label);
    }
    
    /**
     * Extract source actor from label with fallback to thread name
     */
    private ActorType extractSourceFromLabel(String label, String threadName) {
        if (label == null) return ActorType.UNKNOWN;
        
        String upper = label.toUpperCase();
        
        // Pattern: "Send X from SOURCE to TARGET"
        if (upper.contains(" FROM ")) {
            String afterFrom = upper.substring(upper.indexOf(" FROM ") + 6);
            String source = afterFrom.contains(" TO ") ? 
                afterFrom.substring(0, afterFrom.indexOf(" TO ")).trim() : 
                afterFrom.trim();
            ActorType actor = ActorType.fromLabel("from " + source);
            if (actor != ActorType.UNKNOWN) return actor;
        }
        
        // Pattern: "Listen for X from SOURCE"
        if (upper.contains("LISTEN") && upper.contains(" FROM ")) {
            String afterFrom = upper.substring(upper.indexOf(" FROM ") + 6).trim();
            ActorType actor = ActorType.fromLabel("from " + afterFrom);
            if (actor != ActorType.UNKNOWN) return actor;
        }
        
        // Fallback to thread name (might be UNKNOWN for generic thread groups)
        return ActorType.fromThreadName(threadName);
    }
    
    /**
     * Extract target actor from label with fallback to direction inference
     */
    private ActorType extractTargetFromLabel(String label, Direction direction, ActorType source) {
        if (label == null) return inferTargetActor(direction, source);
        
        String upper = label.toUpperCase();
        
        // Pattern: "Send X from SOURCE to TARGET"
        if (upper.contains(" TO ")) {
            String afterTo = upper.substring(upper.indexOf(" TO ") + 4).trim();
            ActorType actor = ActorType.fromLabel("to " + afterTo);
            if (actor != ActorType.UNKNOWN) return actor;
        }
        
        // Fallback to direction-based inference
        return inferTargetActor(direction, source);
    }
    
    /**
     * Infer target actor based on source actor and direction
     */
    private ActorType inferTargetActor(Direction direction, ActorType source) {
        // Simple bidirectional mapping for basic tests
        if (direction == Direction.CLIENT_TO_SERVER) {
            return source == ActorType.CLIENT ? ActorType.SERVER : ActorType.UE_SERVER;
        } else if (direction == Direction.SERVER_TO_CLIENT) {
            return source == ActorType.SERVER ? ActorType.CLIENT : ActorType.UE_CLIENT;
        }
        return ActorType.UNKNOWN;
    }

    // Getters and Setters
    public MessageType getMessageType() {
        return messageType;
    }

    public void setMessageType(MessageType messageType) {
        this.messageType = messageType;
    }

    public Direction getDirection() {
        return direction;
    }

    public void setDirection(Direction direction) {
        this.direction = direction;
    }

    public String getThreadName() {
        return threadName;
    }

    public void setThreadName(String threadName) {
        this.threadName = threadName;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(long timestamp) {
        this.timestamp = timestamp;
    }

    public long getElapsed() {
        return elapsed;
    }

    public void setElapsed(long elapsed) {
        this.elapsed = elapsed;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public String getResponseCode() {
        return responseCode;
    }

    public void setResponseCode(String responseCode) {
        this.responseCode = responseCode;
    }

    public String getLabel() {
        return label;
    }

    public void setLabel(String label) {
        this.label = label;
    }

    public ActorType getSourceActor() {
        return sourceActor;
    }

    public void setSourceActor(ActorType sourceActor) {
        this.sourceActor = sourceActor;
    }

    public ActorType getTargetActor() {
        return targetActor;
    }

    public void setTargetActor(ActorType targetActor) {
        this.targetActor = targetActor;
    }

    public ProtocolType getProtocolType() {
        return protocolType;
    }

    public void setProtocolType(ProtocolType protocolType) {
        this.protocolType = protocolType;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        SipMessage that = (SipMessage) o;
        return timestamp == that.timestamp &&
               elapsed == that.elapsed &&
               success == that.success &&
               messageType == that.messageType &&
               direction == that.direction &&
               sourceActor == that.sourceActor &&
               targetActor == that.targetActor &&
               protocolType == that.protocolType &&
               Objects.equals(threadName, that.threadName) &&
               Objects.equals(responseCode, that.responseCode) &&
               Objects.equals(label, that.label);
    }

    @Override
    public int hashCode() {
        return Objects.hash(messageType, direction, threadName, timestamp, elapsed, success, 
                           responseCode, label, sourceActor, targetActor, protocolType);
    }

    @Override
    public String toString() {
        return "SipMessage{" +
                "messageType=" + messageType +
                ", direction=" + direction +
                ", threadName='" + threadName + '\'' +
                ", timestamp=" + timestamp +
                ", elapsed=" + elapsed +
                ", success=" + success +
                ", responseCode='" + responseCode + '\'' +
                ", label='" + label + '\'' +
                ", sourceActor=" + sourceActor +
                ", targetActor=" + targetActor +
                ", protocolType=" + protocolType +
                '}';
    }

    /**
     * SIP message types identified in call flow
     */
    public enum MessageType {
        INVITE("INVITE"),
        TRYING("100 TRYING"),
        RINGING("180 RINGING"),
        OK("200 OK"),
        ACK("ACK"),
        BYE("BYE"),
        CANCEL("CANCEL"),
        REGISTER("REGISTER"),
        OPTIONS("OPTIONS"),
        INFO("INFO"),
        PRACK("PRACK"),
        UPDATE("UPDATE"),
        SUBSCRIBE("SUBSCRIBE"),
        NOTIFY("NOTIFY"),
        OTHER("OTHER");

        private final String displayName;

        MessageType(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }

        /**
         * Parse message type from JTL label field
         * Examples: "Send INVITE" -> INVITE, "Listen for TRYING" -> TRYING
         */
        public static MessageType fromLabel(String label) {
            if (label == null) return OTHER;
            
            String upper = label.toUpperCase();
            if (upper.contains("INVITE")) return INVITE;
            if (upper.contains("TRYING") || upper.contains("100")) return TRYING;
            if (upper.contains("RINGING") || upper.contains("180")) return RINGING;
            if (upper.contains("OK") || upper.contains("200")) return OK;
            if (upper.contains("ACK")) return ACK;
            if (upper.contains("BYE")) return BYE;
            if (upper.contains("CANCEL")) return CANCEL;
            if (upper.contains("REGISTER")) return REGISTER;
            if (upper.contains("OPTIONS")) return OPTIONS;
            if (upper.contains("INFO")) return INFO;
            if (upper.contains("PRACK")) return PRACK;
            if (upper.contains("UPDATE")) return UPDATE;
            if (upper.contains("SUBSCRIBE")) return SUBSCRIBE;
            if (upper.contains("NOTIFY")) return NOTIFY;
            
            return OTHER;
        }
    }

    /**
     * Message direction in client-server communication
     */
    public enum Direction {
        CLIENT_TO_SERVER("Client → Server"),
        SERVER_TO_CLIENT("Server → Client"),
        UNKNOWN("Unknown");

        private final String displayName;

        Direction(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }

        /**
         * Determine direction from thread name and label
         * Server thread (e.g., "Server 1-1") sends responses to client
         * Client thread (e.g., "Client 2-1") sends requests to server
         */
        public static Direction fromThreadAndLabel(String threadName, String label) {
            if (threadName == null || label == null) return UNKNOWN;
            
            String threadLower = threadName.toLowerCase();
            String labelLower = label.toLowerCase();
            
            // Server thread actions
            if (threadLower.contains("server")) {
                // Server "Send" messages go to client (responses)
                if (labelLower.contains("send")) {
                    return SERVER_TO_CLIENT;
                }
                // Server "Listen" messages receive from client (requests)
                if (labelLower.contains("listen")) {
                    return CLIENT_TO_SERVER;
                }
            }
            
            // Client thread actions
            if (threadLower.contains("client")) {
                // Client "Send" messages go to server (requests)
                if (labelLower.contains("send")) {
                    return CLIENT_TO_SERVER;
                }
                // Client "Listen" messages receive from server (responses)
                if (labelLower.contains("listen")) {
                    return SERVER_TO_CLIENT;
                }
            }
            
            return UNKNOWN;
        }
    }
}
