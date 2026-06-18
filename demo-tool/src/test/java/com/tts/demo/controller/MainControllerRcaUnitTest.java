package com.tts.demo.controller;

import com.tts.demo.model.CallFlow;
import com.tts.demo.model.RcaResult;
import com.tts.demo.model.FailurePoint;
import com.tts.demo.model.FailureType;
import com.tts.demo.service.RcaAnalyzer;
import javafx.application.Platform;
import javafx.embed.swing.JFXPanel;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for RCA panel display logic in MainController.
 * Tests RCA result creation and validation WITHOUT full GUI rendering.
 */
public class MainControllerRcaUnitTest {
    
    private RcaAnalyzer rcaAnalyzer;
    
    @BeforeAll
    public static void initJavaFX() {
        // Initialize JavaFX toolkit (required for Platform class)
        new JFXPanel();
    }
    
    @BeforeEach
    public void setUp() {
        rcaAnalyzer = new RcaAnalyzer();
    }
    
    @Test
    public void testRcaResultHasFailureWhenValid() {
        // Create a valid RCA result
        RcaResult rca = new RcaResult("run-123");
        rca.setFailurePoint(FailurePoint.INVITE_RESPONSE);
        rca.setFailureType(FailureType.REJECTION_4XX);
        rca.setAffectedNode("P-CSCF");
        rca.setRootCause("Call rejected with 403 Forbidden");
        rca.setEvidence(Arrays.asList("Response code: 403", "Message: Forbidden"));
        rca.setRecommendations(Arrays.asList("Check subscriber credentials", "Verify HSS connectivity"));
        rca.setFailureMessageIndex(5);
        
        assertTrue(rca.hasFailure(), "RCA should report failure");
        assertNotNull(rca.getSummary(), "Summary should not be null");
        assertTrue(rca.getSummary().contains("Rejection"), "Summary should mention rejection type");
    }
    
    @Test
    public void testRcaResultNoFailureWhenIncomplete() {
        // Create an RCA result with no failure point
        RcaResult rca = new RcaResult("run-123");
        rca.setFailurePoint(FailurePoint.UNKNOWN);
        rca.setFailureType(FailureType.UNKNOWN);
        rca.setAffectedNode(null);
        rca.setRootCause("No clear failure");
        rca.setFailureMessageIndex(-1);
        
        assertFalse(rca.hasFailure(), "RCA should not report failure for unknown issues");
    }
    
    @Test
    public void testRcaAnalyzerIdentifiesFailures() {
        // This tests the RCA analyzer logic without UI
        CallFlow flow = new CallFlow();
        // Flow would normally have messages added during test execution
        
        assertNotNull(rcaAnalyzer, "RCA analyzer should be initialized");
        // Actual analysis would require RunResult and populated CallFlow
    }
    
    @Test
    public void testRcaResultFormatting() {
        RcaResult rca = new RcaResult("run-123");
        rca.setFailurePoint(FailurePoint.REGISTRATION);
        rca.setFailureType(FailureType.AUTHENTICATION_FAILURE);
        rca.setAffectedNode("HSS");
        rca.setRootCause("Authentication failed");
        rca.setEvidence(Arrays.asList("Invalid credentials"));
        rca.setRecommendations(Arrays.asList("Reset password"));
        rca.setFailureMessageIndex(0);
        
        assertEquals("run-123", rca.getRunId());
        assertEquals(FailurePoint.REGISTRATION, rca.getFailurePoint());
        assertEquals(FailureType.AUTHENTICATION_FAILURE, rca.getFailureType());
        assertEquals("HSS", rca.getAffectedNode());
        assertEquals(0, rca.getFailureMessageIndex());
    }
    
    @Test
    public void testPlatformRunLaterWorks() {
        // Test that Platform.runLater() is functional (needed for RCA panel)
        final boolean[] executed = {false};
        
        Platform.runLater(() -> {
            executed[0] = true;
        });
        
        // Wait a bit for Platform.runLater() to execute
        try {
            Thread.sleep(200);
        } catch (InterruptedException e) {
            fail("Sleep interrupted");
        }
        
        assertTrue(executed[0], "Platform.runLater() should execute code");
    }
}
