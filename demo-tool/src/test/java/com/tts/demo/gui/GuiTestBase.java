package com.tts.demo.gui;

import javafx.application.Platform;
import javafx.scene.Node;
import javafx.scene.control.*;
import javafx.scene.layout.Pane;
import javafx.stage.Stage;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.testfx.api.FxRobot;
import org.testfx.api.FxToolkit;
import org.testfx.framework.junit5.ApplicationTest;
import org.testfx.util.WaitForAsyncUtils;

import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Base class for all TestFX GUI tests.
 * Provides common utilities and test infrastructure.
 */
public abstract class GuiTestBase extends ApplicationTest {
    
    protected Stage stage;
    protected FxRobot robot;
    
    @BeforeAll
    public static void setUpHeadlessMode() {
        // Configure headless mode for CI/CD
        if (Boolean.getBoolean("testfx.headless")) {
            System.setProperty("java.awt.headless", "true");
            System.setProperty("testfx.robot", "glass");
            System.setProperty("testfx.headless", "true");
            System.setProperty("prism.order", "sw");
            System.setProperty("prism.text", "t2k");
            System.setProperty("glass.platform", "Monocle");
            System.setProperty("monocle.platform", "Headless");
        }
    }
    
    @Override
    public void start(Stage stage) throws Exception {
        this.stage = stage;
        this.robot = new FxRobot();
    }
    
    @BeforeEach
    public void setUpEach() throws TimeoutException {
        // Clean up any existing stages
        FxToolkit.cleanupStages();
    }
    
    @AfterEach
    public void tearDownEach() throws TimeoutException {
        // Release all pressed keys and buttons
        FxToolkit.cleanupStages();
        
        // Clear any pending Platform.runLater() tasks
        WaitForAsyncUtils.waitForFxEvents();
    }
    
    /**
     * Wait for a JavaFX node to become visible
     */
    protected <T extends Node> T waitForNode(String query, int timeoutSeconds) {
        await().atMost(timeoutSeconds, TimeUnit.SECONDS)
               .until(() -> lookup(query).tryQuery().isPresent());
        return lookup(query).query();
    }
    
    /**
     * Wait for a condition on the JavaFX thread
     */
    protected void waitForCondition(org.awaitility.core.ThrowingRunnable condition, int timeoutSeconds) {
        await().atMost(timeoutSeconds, TimeUnit.SECONDS)
               .untilAsserted(condition);
    }
    
    /**
     * Execute code on JavaFX thread and wait for completion
     */
    protected void runOnFxThreadAndWait(Runnable action) {
        Platform.runLater(action);
        WaitForAsyncUtils.waitForFxEvents();
    }
    
    /**
     * Verify a node exists and is visible
     */
    protected void assertNodeVisible(String query) {
        Node node = lookup(query).query();
        assertNotNull(node, "Node not found: " + query);
        assertTrue(node.isVisible(), "Node is not visible: " + query);
    }
    
    /**
     * Verify a node exists but is not visible
     */
    protected void assertNodeNotVisible(String query) {
        Node node = lookup(query).queryAll().stream().findFirst().orElse(null);
        if (node != null) {
            assertFalse(node.isVisible(), "Node should not be visible: " + query);
        }
    }
    
    /**
     * Verify a node contains specific text
     */
    protected void assertNodeHasText(String query, String expectedText) {
        Node node = lookup(query).query();
        assertNotNull(node, "Node not found: " + query);
        
        String actualText = null;
        if (node instanceof Labeled) {
            actualText = ((Labeled) node).getText();
        } else if (node instanceof TextInputControl) {
            actualText = ((TextInputControl) node).getText();
        }
        
        assertNotNull(actualText, "Node does not contain text: " + query);
        assertTrue(actualText.contains(expectedText), 
            String.format("Expected text '%s' not found in '%s'", expectedText, actualText));
    }
    
    /**
     * Get the number of children in a Pane
     */
    protected int getChildCount(String query) {
        Node node = lookup(query).query();
        if (node instanceof Pane) {
            return ((Pane) node).getChildren().size();
        }
        return 0;
    }
    
    /**
     * Verify a button is enabled
     */
    protected void assertButtonEnabled(String query) {
        Button button = lookup(query).query();
        assertNotNull(button, "Button not found: " + query);
        assertFalse(button.isDisabled(), "Button should be enabled: " + query);
    }
    
    /**
     * Verify a button is disabled
     */
    protected void assertButtonDisabled(String query) {
        Button button = lookup(query).query();
        assertNotNull(button, "Button not found: " + query);
        assertTrue(button.isDisabled(), "Button should be disabled: " + query);
    }
    
    /**
     * Click a button and wait for UI updates
     */
    protected void clickButtonAndWait(String query) {
        clickOn(query);
        WaitForAsyncUtils.waitForFxEvents();
    }
    
    /**
     * Type text and wait for UI updates
     */
    protected void typeTextAndWait(String text) {
        write(text);
        WaitForAsyncUtils.waitForFxEvents();
    }
    
    /**
     * Wait for async operations to complete
     */
    protected void waitForAsyncOperations(int seconds) {
        await().atMost(seconds, TimeUnit.SECONDS)
               .pollInterval(100, TimeUnit.MILLISECONDS)
               .until(() -> {
                   WaitForAsyncUtils.waitForFxEvents();
                   return true;
               });
    }
    
    /**
     * Verify a SplitPane has expected number of items
     */
    protected void assertSplitPaneItemCount(String query, int expectedCount) {
        SplitPane splitPane = lookup(query).query();
        assertNotNull(splitPane, "SplitPane not found: " + query);
        assertEquals(expectedCount, splitPane.getItems().size(), 
            "SplitPane should have " + expectedCount + " items");
    }
    
    /**
     * Print node hierarchy for debugging
     */
    protected void printNodeHierarchy(Node root, int depth) {
        StringBuilder indent = new StringBuilder();
        for (int i = 0; i < depth; i++) {
            indent.append("  ");
        }
        
        System.out.println(indent + root.getClass().getSimpleName() + 
            " [id=" + root.getId() + ", visible=" + root.isVisible() + "]");
        
        if (root instanceof Pane) {
            for (Node child : ((Pane) root).getChildren()) {
                printNodeHierarchy(child, depth + 1);
            }
        }
    }
}
