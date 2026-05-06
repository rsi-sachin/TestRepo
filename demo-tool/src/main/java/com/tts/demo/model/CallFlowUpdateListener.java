package com.tts.demo.model;

/**
 * Listener interface for receiving updates when SIP messages are added to a call flow.
 * Used for real-time visualization updates during demo execution (Phase 2.2).
 */
public interface CallFlowUpdateListener {
    
    /**
     * Called when a new SIP message is added to the call flow.
     * Implementers should update their visualization or state accordingly.
     * 
     * @param message The SIP message that was added
     * @param callFlow The call flow that was updated
     */
    void onMessageAdded(SipMessage message, CallFlow callFlow);
}
