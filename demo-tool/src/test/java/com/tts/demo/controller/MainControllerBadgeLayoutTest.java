package com.tts.demo.controller;

import com.tts.demo.model.Demo;
import javafx.embed.swing.JFXPanel;
import javafx.geometry.Pos;
import javafx.scene.control.Label;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;

import static org.junit.jupiter.api.Assertions.*;

/**
 * UI tests for badge layout in demo cards.
 * Verifies that protocol and complexity badges are displayed horizontally.
 */
public class MainControllerBadgeLayoutTest {
    
    @BeforeAll
    public static void initJavaFX() {
        // Initialize JavaFX toolkit
        new JFXPanel();
        
        try {
            Thread.sleep(500);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    @Test
    public void testBadgesAreInHorizontalBox() throws Exception {
        // Create a test demo
        Demo testDemo = new Demo(
            "test-001",
            "Test Demo",
            "Test description",
            "Expected outcome",
            Demo.Protocol.SIP_IMS,
            Demo.Complexity.INTERMEDIATE,
            "test.jmx",
            null
        );
        
        // Use reflection to call createDemoCard (private method)
        MainController controller = new MainController();
        Method createDemoCardMethod = MainController.class.getDeclaredMethod("createDemoCard", Demo.class);
        createDemoCardMethod.setAccessible(true);
        
        VBox demoCard = (VBox) createDemoCardMethod.invoke(controller, testDemo);
        
        assertNotNull(demoCard, "Demo card should not be null");
        assertTrue(demoCard.getChildren().size() >= 3, "Demo card should have at least 3 children (title, badges, description)");
        
        // Second child should be the badges HBox
        assertTrue(demoCard.getChildren().get(1) instanceof HBox, "Second child should be HBox containing badges");
        
        HBox badgesBox = (HBox) demoCard.getChildren().get(1);
        assertEquals(2, badgesBox.getChildren().size(), "Badges HBox should contain exactly 2 children (protocol and complexity)");
    }
    
    @Test
    public void testBadgesHaveCorrectAlignment() throws Exception {
        Demo testDemo = new Demo(
            "test-002",
            "Test Demo 2",
            "Test description",
            "Expected outcome",
            Demo.Protocol.DIAMETER,
            Demo.Complexity.ADVANCED,
            "test.jmx",
            null
        );
        
        MainController controller = new MainController();
        Method createDemoCardMethod = MainController.class.getDeclaredMethod("createDemoCard", Demo.class);
        createDemoCardMethod.setAccessible(true);
        
        VBox demoCard = (VBox) createDemoCardMethod.invoke(controller, testDemo);
        HBox badgesBox = (HBox) demoCard.getChildren().get(1);
        
        // Verify HBox alignment is CENTER_LEFT
        assertEquals(Pos.CENTER_LEFT, badgesBox.getAlignment(), "Badges HBox should have CENTER_LEFT alignment");
    }
    
    @Test
    public void testBadgeLabelsDoNotWrap() throws Exception {
        Demo testDemo = new Demo(
            "test-003",
            "Test Demo 3",
            "Test description",
            "Expected outcome",
            Demo.Protocol.RADIUS,
            Demo.Complexity.BASIC,
            "test.jmx",
            null
        );
        
        MainController controller = new MainController();
        Method createDemoCardMethod = MainController.class.getDeclaredMethod("createDemoCard", Demo.class);
        createDemoCardMethod.setAccessible(true);
        
        VBox demoCard = (VBox) createDemoCardMethod.invoke(controller, testDemo);
        HBox badgesBox = (HBox) demoCard.getChildren().get(1);
        
        // Both children should be Labels
        assertTrue(badgesBox.getChildren().get(0) instanceof Label, "First badge should be a Label");
        assertTrue(badgesBox.getChildren().get(1) instanceof Label, "Second badge should be a Label");
        
        Label protocolBadge = (Label) badgesBox.getChildren().get(0);
        Label complexityBadge = (Label) badgesBox.getChildren().get(1);
        
        // Verify wrap text is disabled
        assertFalse(protocolBadge.isWrapText(), "Protocol badge should not wrap text");
        assertFalse(complexityBadge.isWrapText(), "Complexity badge should not wrap text");
    }
    
    @Test
    public void testBadgeLabelsHaveCorrectStyles() throws Exception {
        Demo testDemo = new Demo(
            "test-004",
            "Test Demo 4",
            "Test description",
            "Expected outcome",
            Demo.Protocol.SIP_IMS,
            Demo.Complexity.INTERMEDIATE,
            "test.jmx",
            null
        );
        
        MainController controller = new MainController();
        Method createDemoCardMethod = MainController.class.getDeclaredMethod("createDemoCard", Demo.class);
        createDemoCardMethod.setAccessible(true);
        
        VBox demoCard = (VBox) createDemoCardMethod.invoke(controller, testDemo);
        HBox badgesBox = (HBox) demoCard.getChildren().get(1);
        
        Label protocolBadge = (Label) badgesBox.getChildren().get(0);
        Label complexityBadge = (Label) badgesBox.getChildren().get(1);
        
        // Verify style classes are applied
        assertTrue(protocolBadge.getStyleClass().contains("protocol-badge"), "Protocol badge should have protocol-badge style class");
        assertTrue(complexityBadge.getStyleClass().contains("complexity-badge"), "Complexity badge should have complexity-badge style class");
        
        // Verify protocol-specific style
        assertTrue(protocolBadge.getStyleClass().contains("protocol-sip"), "SIP protocol badge should have protocol-sip style class");
        
        // Verify complexity-specific style
        assertTrue(complexityBadge.getStyleClass().contains("complexity-intermediate"), "Intermediate complexity badge should have complexity-intermediate style class");
    }
    
    @Test
    public void testBadgesHaveCorrectSpacing() throws Exception {
        Demo testDemo = new Demo(
            "test-005",
            "Test Demo 5",
            "Test description",
            "Expected outcome",
            Demo.Protocol.DIAMETER,
            Demo.Complexity.BASIC,
            "test.jmx",
            null
        );
        
        MainController controller = new MainController();
        Method createDemoCardMethod = MainController.class.getDeclaredMethod("createDemoCard", Demo.class);
        createDemoCardMethod.setAccessible(true);
        
        VBox demoCard = (VBox) createDemoCardMethod.invoke(controller, testDemo);
        HBox badgesBox = (HBox) demoCard.getChildren().get(1);
        
        // Verify HBox spacing is 8px
        assertEquals(8.0, badgesBox.getSpacing(), 0.01, "Badges HBox should have 8px spacing");
    }
    
    @Test
    public void testBadgeMaxHeightAllowsVerticalStretch() throws Exception {
        Demo testDemo = new Demo(
            "test-006",
            "Test Demo 6",
            "Test description",
            "Expected outcome",
            Demo.Protocol.RADIUS,
            Demo.Complexity.ADVANCED,
            "test.jmx",
            null
        );
        
        MainController controller = new MainController();
        Method createDemoCardMethod = MainController.class.getDeclaredMethod("createDemoCard", Demo.class);
        createDemoCardMethod.setAccessible(true);
        
        VBox demoCard = (VBox) createDemoCardMethod.invoke(controller, testDemo);
        HBox badgesBox = (HBox) demoCard.getChildren().get(1);
        
        Label protocolBadge = (Label) badgesBox.getChildren().get(0);
        Label complexityBadge = (Label) badgesBox.getChildren().get(1);
        
        // Verify max height allows stretching
        assertEquals(Double.MAX_VALUE, protocolBadge.getMaxHeight(), 0.01, "Protocol badge should allow vertical stretch");
        assertEquals(Double.MAX_VALUE, complexityBadge.getMaxHeight(), 0.01, "Complexity badge should allow vertical stretch");
    }
}
