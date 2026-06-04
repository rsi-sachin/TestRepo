package com.tts.demo.model;

import java.util.Objects;

/**
 * Represents a single SIP message in a VoLTE call flow.
 * Extracted from JTL test results for visualization.
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

    public SipMessage() {
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
               Objects.equals(threadName, that.threadName) &&
               Objects.equals(responseCode, that.responseCode) &&
               Objects.equals(label, that.label);
    }

    @Override
    public int hashCode() {
        return Objects.hash(messageType, direction, threadName, timestamp, elapsed, success, responseCode, label);
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
