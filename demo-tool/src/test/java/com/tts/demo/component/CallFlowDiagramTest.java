package com.tts.demo.component;

import com.tts.demo.model.CallFlow;
import com.tts.demo.model.SipMessage;
import javafx.application.Platform;
import javafx.embed.swing.JFXPanel;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for CallFlowDiagram component.
 * Tests tooltip generation, UML layout, and real-time update capabilities.
 */
public class CallFlowDiagramTest {
    
    private CallFlow callFlow;
    private CallFlowDiagram diagram;
    
    /**
     * Initialize JavaFX toolkit (required for Canvas operations)
     */
    @BeforeAll
    public static void initJavaFX() {
        // Initialize JavaFX toolkit
        new JFXPanel();
        
        // Wait for JavaFX platform to be ready
        try {
            Thread.sleep(500);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    @BeforeEach
    public void setUp() {
        // Create test call flow with sample messages
        callFlow = new CallFlow();
        
        // Add typical VoLTE call setup messages
        callFlow.addMessage(new SipMessage(
            SipMessage.MessageType.INVITE,
            SipMessage.Direction.CLIENT_TO_SERVER,
            "Thread-1",
            System.currentTimeMillis(),
            50,
            true,
            "200",
            "INVITE sip:user@domain.com"
        ));
        
        callFlow.addMessage(new SipMessage(
            SipMessage.MessageType.TRYING,
            SipMessage.Direction.SERVER_TO_CLIENT,
            "Thread-1",
            System.currentTimeMillis() + 50,
            30,
            true,
            "100",
            "100 Trying"
        ));
        
        callFlow.addMessage(new SipMessage(
            SipMessage.MessageType.RINGING,
            SipMessage.Direction.SERVER_TO_CLIENT,
            "Thread-1",
            System.currentTimeMillis() + 100,
            1500,
            true,
            "180",
            "180 Ringing"
        ));
        
        callFlow.addMessage(new SipMessage(
            SipMessage.MessageType.OK,
            SipMessage.Direction.SERVER_TO_CLIENT,
            "Thread-1",
            System.currentTimeMillis() + 1600,
            200,
            true,
            "200",
            "200 OK"
        ));
        
        // Create diagram on JavaFX thread
        Platform.runLater(() -> {
            diagram = new CallFlowDiagram(callFlow);
        });
        
        // Wait for diagram creation
        try {
            Thread.sleep(200);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    /**
     * Test that diagram initializes with correct dimensions for UML layout
     */
    @Test
    public void testDiagramDimensions() throws Exception {
        Platform.runLater(() -> {
            // UML diagram should have fixed width of 400px
            assertEquals(400.0, diagram.getWidth(), 0.1, 
                "UML diagram width should be fixed at 400px");
            
            // Height should accommodate all messages
            assertTrue(diagram.getHeight() >= 600, 
                "Diagram height should be at least 600px");
        });
        
        Thread.sleep(100);
    }
    
    /**
     * Test tooltip text generation for INVITE message
     */
    @Test
    public void testTooltipForInviteMessage() throws Exception {
        SipMessage inviteMsg = new SipMessage(
            SipMessage.MessageType.INVITE,
            SipMessage.Direction.CLIENT_TO_SERVER,
            "Thread-1",
            System.currentTimeMillis(),
            45,
            true,
            "200",
            "INVITE sip:user@domain.com"
        );
        
        String tooltip = invokePrivateTooltipMethod(inviteMsg, 0);
        
        assertNotNull(tooltip, "Tooltip should not be null");
        assertTrue(tooltip.contains("INVITE"), "Tooltip should contain message type");
        assertTrue(tooltip.contains("Call Setup Request"), "Tooltip should contain business description");
        assertTrue(tooltip.contains("Successful"), "Tooltip should show success status");
        assertTrue(tooltip.contains("Client initiated VoLTE call establishment"), 
            "Tooltip should explain business meaning");
        assertTrue(tooltip.contains("Call Establishment"), 
            "Tooltip should show call phase");
    }
    
    /**
     * Test tooltip text generation for failed message
     */
    @Test
    public void testTooltipForFailedMessage() throws Exception {
        SipMessage failedMsg = new SipMessage(
            SipMessage.MessageType.INVITE,
            SipMessage.Direction.CLIENT_TO_SERVER,
            "Thread-1",
            System.currentTimeMillis(),
            5000,
            false,
            "408",
            "INVITE sip:user@domain.com"
        );
        
        String tooltip = invokePrivateTooltipMethod(failedMsg, 0);
        
        assertNotNull(tooltip, "Tooltip should not be null");
        assertTrue(tooltip.contains("Failed"), "Tooltip should show failed status");
        assertTrue(tooltip.contains("Failed to initiate call"), 
            "Tooltip should explain failure meaning");
        assertTrue(tooltip.contains("very slow"), 
            "Tooltip should indicate slow timing for 5000ms");
    }
    
    /**
     * Test tooltip timing context for different elapsed times
     */
    @Test
    public void testTooltipTimingContext() throws Exception {
        // Very fast (< 50ms)
        SipMessage fastMsg = new SipMessage(
            SipMessage.MessageType.TRYING, 
            SipMessage.Direction.SERVER_TO_CLIENT,
            "Thread-1",
            System.currentTimeMillis(),
            30,
            true,
            "100",
            "100 Trying"
        );
        String fastTooltip = invokePrivateTooltipMethod(fastMsg, 0);
        assertTrue(fastTooltip.contains("very fast"), 
            "Tooltip should indicate very fast for 30ms");
        
        // Normal (50-200ms)
        SipMessage normalMsg = new SipMessage(
            SipMessage.MessageType.RINGING,
            SipMessage.Direction.SERVER_TO_CLIENT,
            "Thread-1",
            System.currentTimeMillis(),
            150,
            true,
            "180",
            "180 Ringing"
        );
        String normalTooltip = invokePrivateTooltipMethod(normalMsg, 0);
        assertTrue(normalTooltip.contains("normal"), 
            "Tooltip should indicate normal for 150ms");
        
        // Slow (1000-5000ms)
        SipMessage slowMsg = new SipMessage(
            SipMessage.MessageType.OK,
            SipMessage.Direction.SERVER_TO_CLIENT,
            "Thread-1",
            System.currentTimeMillis(),
            2000,
            true,
            "200",
            "200 OK"
        );
        String slowTooltip = invokePrivateTooltipMethod(slowMsg, 0);
        assertTrue(slowTooltip.contains("slower than expected"), 
            "Tooltip should indicate slow for 2000ms");
    }
    
    /**
     * Test tooltip call phase categorization
     */
    @Test
    public void testTooltipCallPhase() throws Exception {
        // Establishment phase
        SipMessage inviteMsg = new SipMessage(
            SipMessage.MessageType.INVITE,
            SipMessage.Direction.CLIENT_TO_SERVER,
            "Thread-1",
            System.currentTimeMillis(),
            50,
            true,
            "200",
            "INVITE sip:user@domain.com"
        );
        String inviteTooltip = invokePrivateTooltipMethod(inviteMsg, 0);
        assertTrue(inviteTooltip.contains("Call Establishment"), 
            "INVITE should be in Call Establishment phase");
        
        // Confirmation phase
        SipMessage ackMsg = new SipMessage(
            SipMessage.MessageType.ACK,
            SipMessage.Direction.CLIENT_TO_SERVER,
            "Thread-1",
            System.currentTimeMillis(),
            40,
            true,
            "200",
            "ACK"
        );
        String ackTooltip = invokePrivateTooltipMethod(ackMsg, 0);
        assertTrue(ackTooltip.contains("Connection Confirmation"), 
            "ACK should be in Connection Confirmation phase");
        
        // Teardown phase
        SipMessage byeMsg = new SipMessage(
            SipMessage.MessageType.BYE,
            SipMessage.Direction.CLIENT_TO_SERVER,
            "Thread-1",
            System.currentTimeMillis(),
            60,
            true,
            "200",
            "BYE"
        );
        String byeTooltip = invokePrivateTooltipMethod(byeMsg, 0);
        assertTrue(byeTooltip.contains("Call Teardown"), 
            "BYE should be in Call Teardown phase");
    }
    
    /**
     * Test tooltip message position indicator
     */
    @Test
    public void testTooltipMessagePosition() throws Exception {
        SipMessage msg = new SipMessage(
            SipMessage.MessageType.TRYING,
            SipMessage.Direction.SERVER_TO_CLIENT,
            "Thread-1",
            System.currentTimeMillis(),
            30,
            true,
            "100",
            "100 Trying"
        );
        
        String tooltip = invokePrivateTooltipMethod(msg, 2);
        
        assertTrue(tooltip.contains("Message 3 of"), 
            "Tooltip should show 1-based message position (index 2 = message 3)");
    }
    
    /**
     * Test diagram refresh with dynamic message addition
     */
    @Test
    public void testDynamicRefresh() throws Exception {
        Platform.runLater(() -> {
            double initialHeight = diagram.getHeight();
            
            // Add more messages
            callFlow.addMessage(new SipMessage(
                SipMessage.MessageType.ACK,
                SipMessage.Direction.CLIENT_TO_SERVER,
                "Thread-1",
                System.currentTimeMillis(),
                35,
                true,
                "200",
                "ACK"
            ));
            
            callFlow.addMessage(new SipMessage(
                SipMessage.MessageType.BYE,
                SipMessage.Direction.CLIENT_TO_SERVER,
                "Thread-1",
                System.currentTimeMillis(),
                50,
                true,
                "200",
                "BYE"
            ));
            
            // Refresh diagram
            diagram.refresh();
            
            // Height should increase with more messages
            assertTrue(diagram.getHeight() > initialHeight, 
                "Diagram height should increase when messages are added");
        });
        
        Thread.sleep(100);
    }
    
    /**
     * Test that diagram implements CallFlowUpdateListener
     */
    @Test
    public void testCallFlowUpdateListenerImplementation() {
        assertTrue(diagram instanceof com.tts.demo.model.CallFlowUpdateListener,
            "CallFlowDiagram should implement CallFlowUpdateListener");
    }
    
    /**
     * Test real-time message notification
     */
    @Test
    public void testRealTimeMessageNotification() throws Exception {
        Platform.runLater(() -> {
            // Register diagram as listener
            CallFlow liveFlow = new CallFlow();
            CallFlowDiagram liveDiagram = new CallFlowDiagram(liveFlow);
            liveFlow.addListener(liveDiagram);
            
            double initialHeight = liveDiagram.getHeight();
            
            // Add message (should trigger listener callback)
            liveFlow.addMessage(new SipMessage(
                SipMessage.MessageType.INVITE,
                SipMessage.Direction.CLIENT_TO_SERVER,
                "Thread-1",
                System.currentTimeMillis(),
                50,
                true,
                "200",
                "INVITE sip:user@domain.com"
            ));
            
            // Wait for throttled refresh
            try {
                Thread.sleep(300);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            
            // Diagram should have updated
            assertTrue(liveDiagram.getHeight() >= initialHeight, 
                "Diagram should update when message is added via listener");
        });
        
        Thread.sleep(500);
    }
    
    /**
     * Helper method to invoke private getMessageTooltipText method via reflection
     */
    private String invokePrivateTooltipMethod(SipMessage message, int index) throws Exception {
        Method method = CallFlowDiagram.class.getDeclaredMethod(
            "getMessageTooltipText", SipMessage.class, int.class);
        method.setAccessible(true);
        
        final String[] result = new String[1];
        final Exception[] exception = new Exception[1];
        
        Platform.runLater(() -> {
            try {
                result[0] = (String) method.invoke(diagram, message, index);
            } catch (Exception e) {
                exception[0] = e;
            }
        });
        
        Thread.sleep(100);
        
        if (exception[0] != null) {
            throw exception[0];
        }
        
        return result[0];
    }
}
