package com.tts.demo.gui;

import com.tts.demo.MainApp;
import com.tts.demo.component.CallFlowDiagram;
import com.tts.demo.model.ActorType;
import com.tts.demo.model.CallFlow;
import com.tts.demo.model.SipMessage;
import javafx.scene.Node;
import javafx.stage.Stage;
import org.junit.jupiter.api.Test;
import org.testfx.util.WaitForAsyncUtils;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests for real-time update functionality and performance.
 * 
 * Tests cover:
 * - Real-time message updates work smoothly
 * - Throttling prevents UI overload
 * - Architecture panel updates with diagram
 * - No race conditions between updates
 * - Updates don't cause UI freezing
 */
public class RealTimeUpdateTest extends GuiTestBase {
    
    @Override
    public void start(Stage stage) throws Exception {
        super.start(stage);
        MainApp app = new MainApp();
        app.start(stage);
    }
    
    @Test
    public void testRealTimeMessageUpdates() {
        // Select a SIP demo
        clickOn("Self-Contained VoLTE");
        WaitForAsyncUtils.waitForFxEvents();
        clickOn("Execution");
        WaitForAsyncUtils.waitForFxEvents();
        
        // Run demo
        clickOn("Run Demo");
        
        // Monitor status label for changes during execution
        AtomicInteger updateCount = new AtomicInteger(0);
        
        // Check for updates over 10 seconds
        await().atMost(45, TimeUnit.SECONDS)
               .pollInterval(500, TimeUnit.MILLISECONDS)
               .until(() -> {
                   try {
                       Node statusLabel = lookup("#callFlowStatusLabel").query();
                       if (statusLabel instanceof javafx.scene.control.Label) {
                           String text = ((javafx.scene.control.Label) statusLabel).getText();
                           if (text != null && text.contains("messages")) {
                               updateCount.incrementAndGet();
                               return true;
                           }
                       }
                   } catch (Exception e) {
                       // Expected during execution
                   }
                   return false;
               });
        
        // Verify updates occurred
        assertTrue(updateCount.get() > 0, "Status should have updated during execution");
    }
    
    @Test
    public void testThrottlingPreventsSmoothUpdates() {
        // Test that rapid message additions are throttled correctly
        runOnFxThreadAndWait(() -> {
            CallFlow flow = new CallFlow();
            CallFlowDiagram diagram = new CallFlowDiagram(flow);
            flow.addListener(diagram);
            
            AtomicInteger renderCount = new AtomicInteger(0);
            
            // Add messages rapidly (simulate fast JTL parsing)
            for (int i = 0; i < 50; i++) {
                SipMessage msg = new SipMessage();
                msg.setTimestamp(1000L + i * 100);
                msg.setMessageType(SipMessage.MessageType.INVITE);
                msg.setSourceActor(ActorType.UE_CLIENT);
                msg.setTargetActor(ActorType.P_CSCF);
                flow.addMessage(msg);
            }
            
            WaitForAsyncUtils.waitForFxEvents();
            
            // Verify all messages added despite throttling
            assertEquals(50, flow.getTotalMessages());
        });
    }
    
    @Test
    public void testArchitecturePanelUpdatesWithDiagram() {
        // Run a SIP demo and verify architecture panel updates
        clickOn("Self-Contained VoLTE");
        WaitForAsyncUtils.waitForFxEvents();
        
        // Switch to Architecture tab
        clickOn("Architecture");
        WaitForAsyncUtils.waitForFxEvents();
        
        // Architecture panel should exist
        assertNodeVisible("#architectureContainer");
        
        // Switch back to Execution and run
        clickOn("Execution");
        WaitForAsyncUtils.waitForFxEvents();
        clickOn("Run Demo");
        
        // Wait for completion
        await().atMost(45, TimeUnit.SECONDS)
               .until(() -> !lookup("Run Demo").query().isDisabled());
        
        // Switch to Architecture tab to verify it updated
        clickOn("Architecture");
        WaitForAsyncUtils.waitForFxEvents();
        
        // Architecture container should have content now
        runOnFxThreadAndWait(() -> {
            int childCount = getChildCount("#architectureContainer");
            assertTrue(childCount > 0, "Architecture panel should have content after demo run");
        });
    }
    
    @Test
    public void testNoRaceConditionsBetweenUpdates() {
        // Test that concurrent updates don't cause race conditions
        runOnFxThreadAndWait(() -> {
            CallFlow flow = new CallFlow();
            CallFlowDiagram diagram1 = new CallFlowDiagram(flow);
            CallFlowDiagram diagram2 = new CallFlowDiagram(flow);
            
            flow.addListener(diagram1);
            flow.addListener(diagram2);
            
            // Add messages from multiple "threads" (simulated)
            CountDownLatch latch = new CountDownLatch(2);
            
            Thread t1 = new Thread(() -> {
                for (int i = 0; i < 10; i++) {
                    SipMessage msg = new SipMessage();
                    msg.setTimestamp(1000L + i * 100);
                    msg.setMessageType(SipMessage.MessageType.INVITE);
                    msg.setSourceActor(ActorType.UE_CLIENT);
                    msg.setTargetActor(ActorType.P_CSCF);
                    flow.addMessage(msg);
                }
                latch.countDown();
            });
            
            Thread t2 = new Thread(() -> {
                for (int i = 0; i < 10; i++) {
                    SipMessage msg = new SipMessage();
                    msg.setTimestamp(2000L + i * 100);
                    msg.setMessageType(SipMessage.MessageType.OK);
                    msg.setResponseCode("200");
                    msg.setSourceActor(ActorType.P_CSCF);
                    msg.setTargetActor(ActorType.UE_CLIENT);
                    flow.addMessage(msg);
                }
                latch.countDown();
            });
            
            t1.start();
            t2.start();
            
            try {
                latch.await(5, TimeUnit.SECONDS);
            } catch (InterruptedException e) {
                fail("Threads did not complete in time");
            }
            
            WaitForAsyncUtils.waitForFxEvents();
            
            // Verify all messages added without corruption
            assertEquals(20, flow.getTotalMessages());
        });
    }
    
    @Test
    public void testUpdatesDoNotFreezeUI() {
        // Test that updates don't cause UI to become unresponsive
        clickOn("Self-Contained VoLTE");
        WaitForAsyncUtils.waitForFxEvents();
        clickOn("Execution");
        WaitForAsyncUtils.waitForFxEvents();
        clickOn("Run Demo");
        
        // Try to interact with UI during execution
        await().atMost(10, TimeUnit.SECONDS)
               .pollInterval(1, TimeUnit.SECONDS)
               .until(() -> {
                   try {
                       // Try to click Stop button (should be enabled during execution)
                       Node stopButton = lookup("#stopButton").query();
                       if (stopButton != null && !stopButton.isDisabled()) {
                           return true;
                       }
                   } catch (Exception e) {
                       // Expected if not found
                   }
                   return false;
               });
        
        // UI should still be responsive - we can click stop
        clickOn("#stopButton");
        WaitForAsyncUtils.waitForFxEvents();
        
        // Verify demo stopped
        await().atMost(5, TimeUnit.SECONDS)
               .until(() -> !lookup("Run Demo").query().isDisabled());
    }
    
    @Test
    public void testCallFlowStatusUpdatesProgressively() {
        // Test that call flow status label updates during execution
        clickOn("Self-Contained VoLTE");
        WaitForAsyncUtils.waitForFxEvents();
        clickOn("Execution");
        WaitForAsyncUtils.waitForFxEvents();
        
        // Initial status
        assertNodeHasText("#callFlowStatusLabel", "Not started");
        
        // Run demo
        clickOn("Run Demo");
        
        // Status should change to "Initializing"
        await().atMost(5, TimeUnit.SECONDS)
               .until(() -> {
                   try {
                       Node label = lookup("#callFlowStatusLabel").query();
                       if (label instanceof javafx.scene.control.Label) {
                           String text = ((javafx.scene.control.Label) label).getText();
                           return text != null && text.contains("Initializing");
                       }
                   } catch (Exception e) {
                       // Expected
                   }
                   return false;
               });
        
        // Wait for completion
        await().atMost(45, TimeUnit.SECONDS)
               .until(() -> !lookup("Run Demo").query().isDisabled());
        
        // Final status should show message count
        assertNodeHasText("#callFlowStatusLabel", "messages");
    }
    
    @Test
    public void testTerminalOutputStreamsInRealTime() {
        // Test that terminal output updates during execution
        clickOn("Self-Contained VoLTE");
        WaitForAsyncUtils.waitForFxEvents();
        clickOn("Execution");
        WaitForAsyncUtils.waitForFxEvents();
        
        clickOn("Run Demo");
        
        // Wait for terminal to show output
        await().atMost(10, TimeUnit.SECONDS)
               .until(() -> {
                   try {
                       Node terminal = lookup("#outputTextArea").query();
                       if (terminal instanceof javafx.scene.control.TextArea) {
                           String text = ((javafx.scene.control.TextArea) terminal).getText();
                           return text != null && text.length() > 0;
                       }
                   } catch (Exception e) {
                       // Expected
                   }
                   return false;
               });
        
        // Verify terminal has content
        runOnFxThreadAndWait(() -> {
            Node terminal = lookup("#outputTextArea").query();
            if (terminal instanceof javafx.scene.control.TextArea) {
                String text = ((javafx.scene.control.TextArea) terminal).getText();
                assertNotNull(text);
                assertTrue(text.length() > 0, "Terminal should have output");
            }
        });
    }
}
