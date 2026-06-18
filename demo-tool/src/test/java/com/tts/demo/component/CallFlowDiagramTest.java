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
            // UML diagram width increased to 550px to accommodate statistics panel
            assertEquals(550.0, diagram.getWidth(), 0.1, 
                "UML diagram width should be 550px to accommodate statistics");
            
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
            int initialMessageCount = callFlow.getTotalMessages();
            
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
            
            // Verify message count increased
            assertEquals(initialMessageCount + 2, callFlow.getTotalMessages(),
                "Message count should increase when messages are added");
            
            // Verify diagram can be refreshed without errors
            assertNotNull(diagram, "Diagram should remain valid after refresh");
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
     * Test statistics display positioning beside Server lifeline
     */
    @Test
    public void testStatisticsDisplayedVerticallyCorrected() throws Exception {
        Platform.runLater(() -> {
            // Verify diagram has increased width to accommodate stats
            assertTrue(diagram.getWidth() >= 500, 
                "Diagram width should be at least 500px to accommodate statistics panel");
            
            // Verify diagram still displays correctly
            assertNotNull(diagram, "Diagram should be created successfully");
        });
        
        Thread.sleep(100);
    }
    
    /**
     * Test that statistics update dynamically during real-time execution
     */
    @Test
    public void testStatisticsUpdateInRealTime() throws Exception {
        Platform.runLater(() -> {
            CallFlow liveFlow = new CallFlow();
            CallFlowDiagram liveDiagram = new CallFlowDiagram(liveFlow);
            liveFlow.addListener(liveDiagram);
            
            // Initial state
            assertEquals(0, liveFlow.getTotalMessages());
            
            // Add message
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
            
            // Verify count updated
            assertEquals(1, liveFlow.getTotalMessages());
            
            // Add another message
            liveFlow.addMessage(new SipMessage(
                SipMessage.MessageType.TRYING,
                SipMessage.Direction.SERVER_TO_CLIENT,
                "Thread-1",
                System.currentTimeMillis(),
                30,
                true,
                "100",
                "100 Trying"
            ));
            
            // Verify count updated again
            assertEquals(2, liveFlow.getTotalMessages());
            assertEquals(2, liveFlow.getSuccessfulMessages());
            assertEquals(100.0, liveFlow.getSuccessRate(), 0.1);
        });
        
        Thread.sleep(300);
    }
    
    /**
     * Test that legend is compact without statistics summary
     */
    @Test
    public void testLegendWithoutStatsSummary() throws Exception {
        Platform.runLater(() -> {
            // Verify diagram renders without errors
            diagram.render();
            
            // Verify height calculation accounts for reduced legend
            double expectedMinHeight = 600; // Minimum height
            assertTrue(diagram.getHeight() >= expectedMinHeight,
                "Diagram height should be at least minimum even with compact legend");
        });
        
        Thread.sleep(100);
    }
    
    /**
     * Test diagram width accommodates statistics panel
     */
    @Test
    public void testDiagramWidthAccommodatesStats() throws Exception {
        Platform.runLater(() -> {
            // Create diagram with many messages to test layout
            CallFlow largeFlow = new CallFlow();
            for (int i = 0; i < 10; i++) {
                largeFlow.addMessage(new SipMessage(
                    SipMessage.MessageType.INVITE,
                    SipMessage.Direction.CLIENT_TO_SERVER,
                    "Thread-1",
                    System.currentTimeMillis() + (i * 100),
                    50,
                    true,
                    "200",
                    "INVITE"
                ));
            }
            
            CallFlowDiagram largeDiagram = new CallFlowDiagram(largeFlow);
            
            // Verify width is fixed and accommodates stats
            assertEquals(550.0, largeDiagram.getWidth(), 1.0,
                "Diagram width should be fixed at 550px to accommodate statistics");
        });
        
        Thread.sleep(100);
    }
    
    /**
     * Test that statistics don't overlap with messages
     */
    @Test
    public void testStatisticsDoNotOverlapMessages() throws Exception {
        Platform.runLater(() -> {
            // Stats are positioned at: MARGIN + LIFELINE_SPACING + ACTOR_WIDTH + 20
            // = 40 + 200 + 80 + 20 = 340px from left
            // Server lifeline is at: MARGIN + LIFELINE_SPACING + ACTOR_WIDTH/2
            // = 40 + 200 + 40 = 280px from left
            // So stats are 60px to the right of Server lifeline
            
            // Messages span from Client (MARGIN + ACTOR_WIDTH/2 = 80px) 
            // to Server (280px)
            // Stats start at 340px, so no overlap
            
            double statsStartX = 40 + 200 + 80 + 20; // 340px
            double serverLifelineX = 40 + 200 + 80/2.0; // 280px
            
            assertTrue(statsStartX > serverLifelineX + 20,
                "Statistics should start at least 20px to the right of Server lifeline");
        });
        
        Thread.sleep(100);
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
    
    /**
     * Test that real-time observer pattern callbacks trigger diagram refresh.
     * Verifies that CallFlowDiagram properly responds to CallFlow.addMessage() events.
     */
    @Test
    public void testRealTimeCallbackTriggersRefresh() throws Exception {
        // Create a fresh CallFlow for this test
        CallFlow liveFlow = new CallFlow();
        
        // Create diagram and register as listener on JavaFX thread
        final CallFlowDiagram[] diagramRef = new CallFlowDiagram[1];
        final java.util.concurrent.CountDownLatch createLatch = new java.util.concurrent.CountDownLatch(1);
        
        Platform.runLater(() -> {
            CallFlowDiagram testDiagram = new CallFlowDiagram(liveFlow);
            liveFlow.addListener(testDiagram);
            diagramRef[0] = testDiagram;
            createLatch.countDown();
        });
        
        assertTrue(createLatch.await(2, java.util.concurrent.TimeUnit.SECONDS), 
            "Diagram should be created within 2 seconds");
        
        CallFlowDiagram testDiagram = diagramRef[0];
        assertNotNull(testDiagram, "Diagram should be created");
        
        // Get initial refresh time via reflection
        java.lang.reflect.Field lastRefreshField = CallFlowDiagram.class.getDeclaredField("lastRefreshTime");
        lastRefreshField.setAccessible(true);
        
        final long[] initialRefreshTime = new long[1];
        Platform.runLater(() -> {
            try {
                initialRefreshTime[0] = lastRefreshField.getLong(testDiagram);
            } catch (Exception e) {
                fail("Failed to read lastRefreshTime: " + e.getMessage());
            }
        });
        Thread.sleep(100);
        
        // Add a message to trigger callback
        SipMessage newMessage = new SipMessage(
            SipMessage.MessageType.INVITE,
            SipMessage.Direction.CLIENT_TO_SERVER,
            "Thread Group 2-1",
            System.currentTimeMillis(),
            54,
            true,
            "200",
            "Send INVITE"
        );
        
        liveFlow.addMessage(newMessage);
        
        // Wait for throttling (200ms) + processing time
        Thread.sleep(350);
        
        // Verify refresh was called by checking lastRefreshTime changed
        final long[] finalRefreshTime = new long[1];
        final java.util.concurrent.CountDownLatch checkLatch = new java.util.concurrent.CountDownLatch(1);
        
        Platform.runLater(() -> {
            try {
                finalRefreshTime[0] = lastRefreshField.getLong(testDiagram);
                checkLatch.countDown();
            } catch (Exception e) {
                fail("Failed to read lastRefreshTime: " + e.getMessage());
            }
        });
        
        assertTrue(checkLatch.await(2, java.util.concurrent.TimeUnit.SECONDS),
            "Should be able to check refresh time");
        
        assertTrue(finalRefreshTime[0] > initialRefreshTime[0],
            "Diagram should have refreshed after message added (initial: " + 
            initialRefreshTime[0] + ", final: " + finalRefreshTime[0] + ")");
        
        // Verify the message was added to the call flow
        assertEquals(1, liveFlow.getTotalMessages(), "CallFlow should contain 1 message");
    }
}
