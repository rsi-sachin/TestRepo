package com.tts.demo.model;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.stream.Collectors;

/**
 * Represents a complete VoLTE call flow with all SIP messages.
 * Provides analysis methods to determine call completion and success.
 * Supports listeners for real-time visualization updates (Phase 2.2).
 */
public class CallFlow {
    
    private List<SipMessage> messages;
    private int totalMessages;
    private int successfulMessages;
    private boolean callCompleted;
    private long totalDuration;
    
    // Observer pattern support for real-time updates (Phase 2.2)
    private final List<CallFlowUpdateListener> listeners = new CopyOnWriteArrayList<>();

    public CallFlow() {
        this.messages = new ArrayList<>();
        this.totalMessages = 0;
        this.successfulMessages = 0;
        this.callCompleted = false;
        this.totalDuration = 0;
    }

    public CallFlow(List<SipMessage> messages) {
        this.messages = messages != null ? new ArrayList<>(messages) : new ArrayList<>();
        analyze();
    }

    /**
     * Analyze the call flow to determine completion status and statistics.
     * A complete VoLTE call should have: INVITE, OK, ACK, BYE sequence
     */
    public void analyze() {
        this.totalMessages = messages.size();
        this.successfulMessages = (int) messages.stream()
                .filter(SipMessage::isSuccess)
                .count();
        
        // Determine if call completed successfully
        // A complete call must have at least: INVITE, TRYING, RINGING, OK, ACK, BYE
        boolean hasInvite = messages.stream()
                .anyMatch(m -> m.getMessageType() == SipMessage.MessageType.INVITE);
        boolean hasOk = messages.stream()
                .anyMatch(m -> m.getMessageType() == SipMessage.MessageType.OK);
        boolean hasAck = messages.stream()
                .anyMatch(m -> m.getMessageType() == SipMessage.MessageType.ACK);
        boolean hasBye = messages.stream()
                .anyMatch(m -> m.getMessageType() == SipMessage.MessageType.BYE);
        
        this.callCompleted = hasInvite && hasOk && hasAck && hasBye && (successfulMessages == totalMessages);
        
        // Calculate total duration (from first to last message)
        if (!messages.isEmpty()) {
            long firstTimestamp = messages.stream()
                    .mapToLong(SipMessage::getTimestamp)
                    .min()
                    .orElse(0);
            long lastTimestamp = messages.stream()
                    .mapToLong(SipMessage::getTimestamp)
                    .max()
                    .orElse(0);
            this.totalDuration = lastTimestamp - firstTimestamp;
        }
    }

    /**
     * Get all messages sent by the client to the server
     */
    public List<SipMessage> getClientMessages() {
        return messages.stream()
                .filter(m -> m.getDirection() == SipMessage.Direction.CLIENT_TO_SERVER)
                .collect(Collectors.toList());
    }

    /**
     * Get all messages sent by the server to the client
     */
    public List<SipMessage> getServerMessages() {
        return messages.stream()
                .filter(m -> m.getDirection() == SipMessage.Direction.SERVER_TO_CLIENT)
                .collect(Collectors.toList());
    }

    /**
     * Get messages of a specific type
     */
    public List<SipMessage> getMessagesByType(SipMessage.MessageType type) {
        return messages.stream()
                .filter(m -> m.getMessageType() == type)
                .collect(Collectors.toList());
    }

    /**
     * Get failed messages (where success = false)
     */
    public List<SipMessage> getFailedMessages() {
        return messages.stream()
                .filter(m -> !m.isSuccess())
                .collect(Collectors.toList());
    }

    /**
     * Add a message to the call flow and re-analyze
     */
    public void addMessage(SipMessage message) {
        this.messages.add(message);
        analyze();
        
        // Notify listeners about the new message (Phase 2.2)
        notifyListeners(message);
    }
    
    /**
     * Add a listener for call flow updates (Phase 2.2).
     * 
     * @param listener The listener to add
     */
    public void addListener(CallFlowUpdateListener listener) {
        if (listener != null && !listeners.contains(listener)) {
            listeners.add(listener);
        }
    }
    
    /**
     * Remove a listener from call flow updates (Phase 2.2).
     * 
     * @param listener The listener to remove
     */
    public void removeListener(CallFlowUpdateListener listener) {
        listeners.remove(listener);
    }
    
    /**
     * Notify all listeners that a message was added (Phase 2.2).
     * 
     * @param message The message that was added
     */
    private void notifyListeners(SipMessage message) {
        for (CallFlowUpdateListener listener : listeners) {
            try {
                listener.onMessageAdded(message, this);
            } catch (Exception e) {
                // Log but don't fail if a listener throws an exception
                System.err.println("Error notifying listener: " + e.getMessage());
            }
        }
    }
    
    /**
     * Get success rate as percentage (0-100)
     */
    public double getSuccessRate() {
        if (totalMessages == 0) return 0.0;
        return (successfulMessages * 100.0) / totalMessages;
    }

    // Getters and Setters
    public List<SipMessage> getMessages() {
        return new ArrayList<>(messages);
    }

    public void setMessages(List<SipMessage> messages) {
        this.messages = messages != null ? new ArrayList<>(messages) : new ArrayList<>();
        analyze();
    }

    public int getTotalMessages() {
        return totalMessages;
    }

    public int getSuccessfulMessages() {
        return successfulMessages;
    }

    public boolean isCallCompleted() {
        return callCompleted;
    }

    public long getTotalDuration() {
        return totalDuration;
    }

    @Override
    public String toString() {
        return "CallFlow{" +
                "totalMessages=" + totalMessages +
                ", successfulMessages=" + successfulMessages +
                ", callCompleted=" + callCompleted +
                ", totalDuration=" + totalDuration + "ms" +
                ", successRate=" + String.format("%.1f%%", getSuccessRate()) +
                '}';
    }
}
