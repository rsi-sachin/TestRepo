package com.tts.demo.component;

import com.tts.demo.model.ActorType;
import com.tts.demo.model.ProtocolType;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.scene.paint.Color;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.TextAlignment;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * 3GPP VoLTE Network Architecture Reference Diagram (Phase 3).
 * Educational component showing complete network topology with protocol interfaces.
 * Helps users understand how simplified test scenarios map to real network deployments.
 */
public class NetworkArchitecturePanel extends VBox {
    
    private static final double DIAGRAM_WIDTH = 800;
    private static final double DIAGRAM_HEIGHT = 500;
    private static final double NODE_WIDTH = 90;
    private static final double NODE_HEIGHT = 60;
    private static final double LAYER_SPACING = 120;
    
    private Canvas architectureCanvas;
    private List<ActorType> activeActors;
    private TextArea descriptionArea;
    
    /**
     * Create a network architecture panel
     */
    public NetworkArchitecturePanel() {
        this.activeActors = new ArrayList<>();
        setupUI();
        renderArchitecture();
    }
    
    /**
     * Setup the UI components
     */
    private void setupUI() {
        setSpacing(10);
        setPadding(new Insets(15));
        setStyle("-fx-background-color: white;");
        
        // Title
        Label titleLabel = new Label("3GPP VoLTE Network Architecture");
        titleLabel.setFont(Font.font("Segoe UI", FontWeight.BOLD, 16));
        
        // Architecture canvas
        architectureCanvas = new Canvas(DIAGRAM_WIDTH, DIAGRAM_HEIGHT);
        architectureCanvas.setStyle("-fx-border-color: #bdc3c7; -fx-border-width: 1px;");
        
        // Description area
        descriptionArea = new TextArea();
        descriptionArea.setEditable(false);
        descriptionArea.setPrefRowCount(4);
        descriptionArea.setWrapText(true);
        descriptionArea.setStyle("-fx-font-family: 'Segoe UI'; -fx-font-size: 11px;");
        descriptionArea.setText(getDefaultDescription());
        
        // Legend
        VBox legend = createLegend();
        
        getChildren().addAll(titleLabel, architectureCanvas, legend, 
                            new Label("Description:"), descriptionArea);
    }
    
    /**
     * Create legend explaining the diagram
     */
    private VBox createLegend() {
        VBox legendBox = new VBox(5);
        legendBox.setPadding(new Insets(10));
        legendBox.setStyle("-fx-background-color: #f9f9f9; -fx-border-color: #bdc3c7; -fx-border-width: 1px;");
        
        Label legendTitle = new Label("Legend:");
        legendTitle.setFont(Font.font("Segoe UI", FontWeight.BOLD, 11));
        
        HBox colorRow = new HBox(20);
        colorRow.getChildren().addAll(
            createLegendItem("User Equipment", Color.rgb(52, 152, 219)),
            createLegendItem("IMS Core", Color.rgb(142, 68, 173)),
            createLegendItem("EPC/LTE", Color.rgb(155, 89, 182)),
            createLegendItem("Support Systems", Color.rgb(231, 76, 60)),
            createLegendItem("Active in Test", Color.rgb(46, 204, 113))
        );
        
        legendBox.getChildren().addAll(legendTitle, colorRow);
        return legendBox;
    }
    
    /**
     * Create a single legend item
     */
    private HBox createLegendItem(String text, Color color) {
        HBox item = new HBox(5);
        item.setAlignment(Pos.CENTER_LEFT);
        
        Region colorBox = new Region();
        colorBox.setMinSize(15, 15);
        colorBox.setMaxSize(15, 15);
        colorBox.setStyle(String.format("-fx-background-color: #%02x%02x%02x; -fx-border-color: black; -fx-border-width: 1px;",
            (int)(color.getRed() * 255),
            (int)(color.getGreen() * 255),
            (int)(color.getBlue() * 255)));
        
        Label label = new Label(text);
        label.setFont(Font.font("Segoe UI", 10));
        
        item.getChildren().addAll(colorBox, label);
        return item;
    }
    
    /**
     * Update which actors are active in the current test
     */
    public void setActiveActors(List<ActorType> actors) {
        this.activeActors = new ArrayList<>(actors);
        renderArchitecture();
        updateDescription();
    }
    
    /**
     * Render the complete 3GPP network architecture
     */
    private void renderArchitecture() {
        GraphicsContext gc = architectureCanvas.getGraphicsContext2D();
        
        // Clear canvas
        gc.setFill(Color.WHITE);
        gc.fillRect(0, 0, DIAGRAM_WIDTH, DIAGRAM_HEIGHT);
        
        // Define network topology layers
        double startY = 40;
        double centerX = DIAGRAM_WIDTH / 2;
        
        // Layer 1: User Equipment
        drawNode(gc, centerX - 350, startY, ActorType.UE_CLIENT, "UE-A\n(Caller)");
        drawNode(gc, centerX + 250, startY, ActorType.UE_SERVER, "UE-B\n(Callee)");
        
        // Layer 2: IMS Core
        double imsY = startY + LAYER_SPACING;
        drawNode(gc, centerX - 280, imsY, ActorType.P_CSCF, "P-CSCF\n(Proxy)");
        drawNode(gc, centerX - 100, imsY, ActorType.I_CSCF, "I-CSCF\n(Interrogating)");
        drawNode(gc, centerX + 80, imsY, ActorType.S_CSCF, "S-CSCF\n(Serving)");
        drawNode(gc, centerX + 260, imsY, ActorType.TAS, "TAS/AS\n(Application)");
        
        // Layer 3: Support Systems
        double supportY = startY + LAYER_SPACING * 2;
        drawNode(gc, centerX - 200, supportY, ActorType.HSS, "HSS\n(Subscriber DB)");
        drawNode(gc, centerX, supportY, ActorType.PCRF, "PCRF\n(Policy)");
        drawNode(gc, centerX + 200, supportY, ActorType.OCS, "OCS\n(Charging)");
        
        // Layer 4: EPC/LTE Network
        double epcY = startY + LAYER_SPACING * 3;
        drawNode(gc, centerX - 200, epcY, ActorType.MME, "MME\n(Mobility)");
        drawNode(gc, centerX, epcY, ActorType.S_GW, "S-GW\n(Serving GW)");
        drawNode(gc, centerX + 200, epcY, ActorType.P_GW, "P-GW\n(PDN GW)");
        
        // Draw protocol interfaces
        drawProtocolLink(gc, centerX - 350, startY + NODE_HEIGHT, centerX - 280, imsY, ProtocolType.SIP, "SIP");
        drawProtocolLink(gc, centerX - 280, imsY + NODE_HEIGHT / 2, centerX - 100, imsY + NODE_HEIGHT / 2, ProtocolType.SIP, "SIP");
        drawProtocolLink(gc, centerX - 100, imsY + NODE_HEIGHT / 2, centerX + 80, imsY + NODE_HEIGHT / 2, ProtocolType.SIP, "SIP");
        drawProtocolLink(gc, centerX + 80, imsY + NODE_HEIGHT / 2, centerX + 260, imsY + NODE_HEIGHT / 2, ProtocolType.SIP, "ISC");
        drawProtocolLink(gc, centerX + 80, imsY + NODE_HEIGHT, centerX - 200, supportY, ProtocolType.DIAMETER_CX, "Cx");
        drawProtocolLink(gc, centerX + 260, imsY + NODE_HEIGHT, centerX - 200, supportY, ProtocolType.DIAMETER_SH, "Sh");
        drawProtocolLink(gc, centerX - 280, imsY + NODE_HEIGHT, centerX, supportY, ProtocolType.DIAMETER_RX, "Rx");
        drawProtocolLink(gc, centerX, supportY + NODE_HEIGHT, centerX + 200, epcY, ProtocolType.DIAMETER_GX, "Gx");
        drawProtocolLink(gc, centerX - 200, supportY + NODE_HEIGHT, centerX - 200, epcY, ProtocolType.DIAMETER_S6A, "S6a");
        
        // Add layer labels
        gc.setFill(Color.GRAY);
        gc.setFont(Font.font("Segoe UI", FontWeight.BOLD, 11));
        gc.setTextAlign(TextAlignment.LEFT);
        gc.fillText("User Equipment", 10, startY + 20);
        gc.fillText("IMS Core", 10, imsY + 20);
        gc.fillText("Support Systems", 10, supportY + 20);
        gc.fillText("EPC/LTE Network", 10, epcY + 20);
    }
    
    /**
     * Draw a network node
     */
    private void drawNode(GraphicsContext gc, double x, double y, ActorType actorType, String label) {
        boolean isActive = activeActors.contains(actorType);
        
        // Get base color
        Color baseColor;
        if (actorType.getRole() == ActorType.ActorRole.ENDPOINT) {
            baseColor = Color.rgb(52, 152, 219);
        } else if (actorType.getRole() == ActorType.ActorRole.IMS_CORE) {
            baseColor = Color.rgb(142, 68, 173);
        } else if (actorType.getRole() == ActorType.ActorRole.EPC_CORE || actorType.getRole() == ActorType.ActorRole.EPC_GATEWAY) {
            baseColor = Color.rgb(155, 89, 182);
        } else {
            baseColor = Color.rgb(231, 76, 60);
        }
        
        // Highlight active nodes
        if (isActive) {
            // Draw glow effect
            gc.setFill(Color.rgb(46, 204, 113, 0.3));
            gc.fillRoundRect(x - 5, y - 5, NODE_WIDTH + 10, NODE_HEIGHT + 10, 10, 10);
            gc.setStroke(Color.rgb(46, 204, 113));
            gc.setLineWidth(3);
            gc.strokeRoundRect(x, y, NODE_WIDTH, NODE_HEIGHT, 8, 8);
        }
        
        // Draw node box
        gc.setFill(baseColor);
        gc.fillRoundRect(x, y, NODE_WIDTH, NODE_HEIGHT, 8, 8);
        gc.setStroke(Color.BLACK);
        gc.setLineWidth(1);
        gc.strokeRoundRect(x, y, NODE_WIDTH, NODE_HEIGHT, 8, 8);
        
        // Draw label
        gc.setFill(Color.WHITE);
        gc.setFont(Font.font("Segoe UI", FontWeight.BOLD, 10));
        gc.setTextAlign(TextAlignment.CENTER);
        
        String[] lines = label.split("\n");
        double textY = y + (NODE_HEIGHT - lines.length * 12) / 2 + 10;
        for (String line : lines) {
            gc.fillText(line, x + NODE_WIDTH / 2, textY);
            textY += 14;
        }
    }
    
    /**
     * Draw a protocol interface link between nodes
     */
    private void drawProtocolLink(GraphicsContext gc, double x1, double y1, double x2, double y2, 
                                   ProtocolType protocol, String label) {
        gc.setStroke(protocol.getColor());
        gc.setLineWidth(2);
        gc.setLineDashes(5, 5);
        gc.strokeLine(x1 + NODE_WIDTH / 2, y1, x2 + NODE_WIDTH / 2, y2);
        gc.setLineDashes(0);
        
        // Draw label
        double midX = (x1 + x2) / 2 + NODE_WIDTH / 2;
        double midY = (y1 + y2) / 2;
        gc.setFill(Color.WHITE);
        gc.fillRect(midX - 15, midY - 8, 30, 16);
        gc.setFill(protocol.getColor());
        gc.setFont(Font.font("Segoe UI", FontWeight.BOLD, 9));
        gc.setTextAlign(TextAlignment.CENTER);
        gc.fillText(label, midX, midY + 4);
    }
    
    /**
     * Get default description text
     */
    private String getDefaultDescription() {
        return "This diagram shows the complete 3GPP VoLTE network architecture with all protocol interfaces. " +
               "In actual tests, simplified scenarios may simulate only a subset of these nodes. " +
               "Active nodes in the current test scenario are highlighted in green.";
    }
    
    /**
     * Update description based on active actors
     */
    private void updateDescription() {
        if (activeActors.isEmpty()) {
            descriptionArea.setText(getDefaultDescription());
            return;
        }
        
        StringBuilder desc = new StringBuilder();
        desc.append("Current Test Scenario Active Nodes:\n\n");
        
        for (ActorType actor : activeActors) {
            desc.append("• ").append(actor.getDisplayName())
                .append(" - ").append(actor.getDescription()).append("\n");
        }
        
        desc.append("\nSimplified tests validate core functionality without requiring full network deployment. ");
        desc.append("The TAS node often represents multiple IMS/EPC nodes in a consolidated simulation environment.");
        
        descriptionArea.setText(desc.toString());
    }
}
