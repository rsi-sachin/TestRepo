package com.tts.demo.component;

import com.tts.demo.model.ActorType;
import com.tts.demo.model.CallFlow;
import com.tts.demo.model.CallFlowUpdateListener;
import com.tts.demo.model.ProtocolType;
import com.tts.demo.model.SipMessage;
import javafx.application.Platform;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.paint.Color;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;
import javafx.scene.text.TextAlignment;
import javafx.geometry.VPos;
import javafx.scene.input.MouseEvent;
import javafx.scene.control.Tooltip;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Custom JavaFX Canvas control for rendering SIP call flow sequence diagrams.
 * Displays multi-actor message exchanges with protocol annotations (Phase 1, Phase 2).
 * Supports real-time updates via CallFlowUpdateListener and 3GPP architecture mapping (Phase 3).
 */
public class CallFlowDiagram extends Canvas implements CallFlowUpdateListener {
    
    private static final Logger logger = LoggerFactory.getLogger(CallFlowDiagram.class);
    
    // Layout constants for UML sequence diagram
    private static final double MARGIN = 40;
    private static final double ACTOR_WIDTH = 90;      // Increased for longer names (P-CSCF, etc.)
    private static final double ACTOR_HEIGHT = 50;     // Increased for better visibility
    private static final double LIFELINE_SPACING = 180; // Spacing between lifelines
    private static final double MESSAGE_HEIGHT = 55;    // Increased for protocol labels
    private static final double TOP_MARGIN = 80;        // Space for actors at top
    private static final double LEGEND_HEIGHT = 80;     // Increased for protocol legend
    private static final double ARROW_HEAD_SIZE = 8;
    private static final double LIFELINE_DASH = 5;      // Dash pattern for lifelines
    private static final double STATS_WIDTH = 160;      // Width for statistics panel
    private static final double MIN_DIAGRAM_WIDTH = 600; // Minimum width
    
    // Throttling for real-time updates (Phase 2.2)
    private static final long THROTTLE_MS = 200; // Max 1 refresh per 200ms
    private volatile long lastRefreshTime = 0;
    private volatile boolean refreshPending = false;
    
    // Color constants
    private static final Color COLOR_SUCCESS = Color.rgb(39, 174, 96);      // Green
    private static final Color COLOR_FAILURE = Color.rgb(231, 76, 60);      // Red
    private static final Color COLOR_IN_PROGRESS = Color.rgb(52, 152, 219); // Blue
    private static final Color COLOR_INFO = Color.rgb(149, 165, 166);       // Gray
    private static final Color COLOR_BACKGROUND = Color.WHITE;
    private static final Color COLOR_LANE = Color.rgb(236, 240, 241);       // Light gray
    private static final Color COLOR_TEXT = Color.rgb(44, 62, 80);          // Dark gray
    private static final Color COLOR_BORDER = Color.rgb(189, 195, 199);     // Border gray
    
    private final CallFlow callFlow;
    private Tooltip messageTooltip;
    
    // Phase 1: Dynamic actor support
    private List<ActorType> actors;  // Ordered list of unique actors in the call flow
    private double diagramWidth;     // Calculated width based on number of actors
    
    // RCA: Failure highlighting support
    private int failureMessageIndex = -1;  // Index of failed message to highlight (-1 = none)
    private String failureReason = null;    // Root cause description for tooltip
    
    /**
     * Create a CallFlowDiagram for visualizing the given call flow
     * 
     * @param callFlow The call flow to visualize
     */
    public CallFlowDiagram(CallFlow callFlow) {
        this.callFlow = callFlow;
        
        // Phase 1: Extract unique actors from messages
        this.actors = extractActors(callFlow.getMessages());
        
        // Calculate required canvas size based on UML layout and number of actors
        this.diagramWidth = calculateDiagramWidth(actors.size());
        double requiredHeight = MARGIN * 2 + TOP_MARGIN + (callFlow.getMessages().size() * MESSAGE_HEIGHT) + LEGEND_HEIGHT;
        
        setWidth(diagramWidth);
        setHeight(Math.max(600, requiredHeight));
        
        // Setup tooltip for hover interactions
        messageTooltip = new Tooltip();
        
        // Add mouse hover handler
        setOnMouseMoved(this::handleMouseMoved);
        
        // Render the diagram
        render();
    }
    
    /**
     * Extract unique actors from messages in order of first appearance (Phase 1).
     * Falls back to Client/Server if no actor information available.
     */
    private List<ActorType> extractActors(List<SipMessage> messages) {
        Set<ActorType> actorSet = new LinkedHashSet<>();
        
        for (SipMessage message : messages) {
            if (message.getSourceActor() != null && message.getSourceActor() != ActorType.UNKNOWN) {
                actorSet.add(message.getSourceActor());
            }
            if (message.getTargetActor() != null && message.getTargetActor() != ActorType.UNKNOWN) {
                actorSet.add(message.getTargetActor());
            }
        }
        
        // If no actors found, use default Client/Server
        if (actorSet.isEmpty()) {
            actorSet.add(ActorType.CLIENT);
            actorSet.add(ActorType.SERVER);
        }
        
        return new ArrayList<>(actorSet);
    }
    
    /**
     * Calculate diagram width based on number of actors
     */
    private double calculateDiagramWidth(int actorCount) {
        // Width = left margin + actors + spacing + stats panel + right margin
        double actorsWidth = actorCount * ACTOR_WIDTH + (actorCount - 1) * (LIFELINE_SPACING - ACTOR_WIDTH);
        double totalWidth = MARGIN + actorsWidth + STATS_WIDTH + MARGIN;
        return Math.max(MIN_DIAGRAM_WIDTH, totalWidth);
    }
    
    /**
     * Set failure highlighting for RCA visualization
     * 
     * @param messageIndex Index of the failed message in the call flow
     * @param reason Root cause description for tooltip
     */
    public void setFailureHighlight(int messageIndex, String reason) {
        this.failureMessageIndex = messageIndex;
        this.failureReason = reason;
        refresh();
        logger.info("Set failure highlight at message index {} with reason: {}", messageIndex, reason);
    }
    
    /**
     * Clear failure highlighting
     */
    public void clearFailureHighlight() {
        this.failureMessageIndex = -1;
        this.failureReason = null;
        refresh();
    }
    
    /**
     * Refresh the diagram with current data.
     * Updates canvas size dynamically and re-renders all elements.
     * Used for incremental updates during real-time visualization (Phase 2.1).
     */
    public void refresh() {
        updateCanvasSize();
        render();
    }
    
    /**
     * Update canvas size based on current number of messages.
     * Allows diagram to grow dynamically as messages are added in real-time.
     */
    private void updateCanvasSize() {
        // Recalculate actors in case new ones were added
        List<SipMessage> messages = callFlow.getMessages();
        this.actors = extractActors(messages);
        this.diagramWidth = calculateDiagramWidth(actors.size());
        
        double requiredHeight = MARGIN * 2 + TOP_MARGIN + (messages.size() * MESSAGE_HEIGHT) + LEGEND_HEIGHT;
        
        setWidth(diagramWidth);
        setHeight(Math.max(600, requiredHeight));
    }
    
    /**
     * Callback when a message is added to the call flow (Phase 2.2).
     * Implements CallFlowUpdateListener interface for real-time updates.
     * Uses throttling to prevent excessive redraws (max 1 per 200ms).
     * 
     * @param message The message that was added
     * @param callFlow The call flow that was updated
     */
    @Override
    public void onMessageAdded(SipMessage message, CallFlow callFlow) {
        long now = System.currentTimeMillis();
        
        logger.debug("[DIAGRAM-REFRESH] onMessageAdded called for message #{} (type: {})", 
            callFlow.getTotalMessages(), message.getMessageType().getDisplayName());
        
        // Check if throttle period has passed
        if (now - lastRefreshTime >= THROTTLE_MS) {
            // Immediate refresh
            lastRefreshTime = now;
            refreshPending = false;
            logger.debug("[DIAGRAM-REFRESH] Triggering immediate refresh (last refresh {}ms ago)", 
                now - lastRefreshTime);
            Platform.runLater(this::refresh);
        } else {
            // Schedule a delayed refresh if not already pending
            if (!refreshPending) {
                refreshPending = true;
                long delay = THROTTLE_MS - (now - lastRefreshTime);
                logger.debug("[DIAGRAM-REFRESH] Scheduling delayed refresh in {}ms", delay);
                
                // Schedule refresh after throttle period
                new Thread(() -> {
                    try {
                        Thread.sleep(delay);
                        lastRefreshTime = System.currentTimeMillis();
                        refreshPending = false;
                        Platform.runLater(this::refresh);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }).start();
            } else {
                logger.debug("[DIAGRAM-REFRESH] Refresh already pending, skipping");
            }
        }
    }
    
    /**
     * Render the complete call flow diagram in UML sequence diagram style.
     * Changed to public for incremental rendering support (Phase 2.1).
     */
    public void render() {
        try {
            List<SipMessage> messages = callFlow.getMessages();
            logger.debug("[DIAGRAM-REFRESH] render() called - drawing {} messages with {} actors", 
                messages.size(), actors.size());
            
            GraphicsContext gc = getGraphicsContext2D();
            
            // Clear canvas
            gc.setFill(COLOR_BACKGROUND);
            gc.fillRect(0, 0, getWidth(), getHeight());
            
            // Draw UML components in order
            drawActors(gc);
            drawLifelines(gc);
            drawMessages(gc, messages);
            drawStatistics(gc, messages);  // Statistics beside Server lifeline
            drawLegend(gc);      // Compact legend at bottom
            
            logger.debug("[DIAGRAM-REFRESH] render() completed successfully");
        } catch (Exception e) {
            logger.error("[DIAGRAM-REFRESH] Error during render()", e);
        }
    }
    
    /**
     * Draw the actor boxes at the top (dynamic number of actors - Phase 1)
     */
    private void drawActors(GraphicsContext gc) {
        double actorY = MARGIN;
        
        for (int i = 0; i < actors.size(); i++) {
            ActorType actor = actors.get(i);
            double actorX = getActorX(i);
            
            // Draw actor box with role-based color
            gc.setFill(getActorRoleColor(actor));
            gc.fillRect(actorX, actorY, ACTOR_WIDTH, ACTOR_HEIGHT);
            
            // Draw actor border
            gc.setStroke(COLOR_BORDER);
            gc.setLineWidth(2);
            gc.strokeRect(actorX, actorY, ACTOR_WIDTH, ACTOR_HEIGHT);
            
            // Draw actor label
            gc.setFill(Color.WHITE);
            gc.setFont(Font.font("Segoe UI", FontWeight.BOLD, 12));
            gc.setTextAlign(TextAlignment.CENTER);
            gc.setTextBaseline(VPos.CENTER);
            
            String displayName = actor.getDisplayName();
            gc.fillText(displayName, actorX + ACTOR_WIDTH / 2, actorY + ACTOR_HEIGHT / 2);
        }
    }
    
    /**
     * Get X coordinate for actor at given index
     */
    private double getActorX(int actorIndex) {
        return MARGIN + (actorIndex * LIFELINE_SPACING);
    }
    
    /**
     * Get X coordinate for actor's lifeline center
     */
    private double getLifelineX(int actorIndex) {
        return getActorX(actorIndex) + ACTOR_WIDTH / 2;
    }
    
    /**
     * Get color based on actor role (Phase 1, Phase 3)
     */
    private Color getActorRoleColor(ActorType actor) {
        switch (actor.getRole()) {
            case ENDPOINT:
                return Color.rgb(52, 152, 219);  // Blue - UE
            case IMS_CORE:
                return Color.rgb(142, 68, 173);  // Purple - CSCF nodes
            case APPLICATION_SERVER:
                return Color.rgb(230, 126, 34);  // Orange - TAS/AS
            case DATABASE:
                return Color.rgb(231, 76, 60);   // Red - HSS
            case POLICY:
                return Color.rgb(26, 188, 156);  // Teal - PCRF
            case CHARGING:
                return Color.rgb(241, 196, 15);  // Yellow - OCS
            case EPC_CORE:
                return Color.rgb(155, 89, 182);  // Light purple - MME
            case EPC_GATEWAY:
                return Color.rgb(52, 73, 94);    // Dark blue - gateways
            case ACCESS:
                return Color.rgb(149, 165, 166); // Gray - eNodeB
            default:
                return Color.rgb(52, 73, 94);    // Default dark blue-gray
        }
    }
    
    /**
     * Draw the vertical lifelines extending down from actors (Phase 1)
     */
    private void drawLifelines(GraphicsContext gc) {
        double startY = MARGIN + ACTOR_HEIGHT;
        double endY = MARGIN + TOP_MARGIN + (callFlow.getMessages().size() * MESSAGE_HEIGHT);
        
        // Draw dashed lifelines for each actor
        gc.setStroke(COLOR_BORDER);
        gc.setLineWidth(1);
        gc.setLineDashes(LIFELINE_DASH, LIFELINE_DASH);
        
        for (int i = 0; i < actors.size(); i++) {
            double lifelineX = getLifelineX(i);
            gc.strokeLine(lifelineX, startY, lifelineX, endY);
        }
        
        // Reset line dashes for other drawing
        gc.setLineDashes(0);
    }
    
    /**
     * Draw all SIP messages as horizontal arrows between lifelines (Phase 1, Phase 2)
     */
    private void drawMessages(GraphicsContext gc, List<SipMessage> messages) {
        double startY = MARGIN + TOP_MARGIN;
        
        for (int i = 0; i < messages.size(); i++) {
            SipMessage message = messages.get(i);
            double y = startY + (i * MESSAGE_HEIGHT);
            
            // RCA: Highlight failed message if this is the failure point
            boolean isFailureMessage = (i == failureMessageIndex);
            
            if (isFailureMessage) {
                // Draw red highlight background
                drawFailureHighlight(gc, y, message);
            }
            
            drawMessage(gc, message, y, isFailureMessage);
        }
    }
    
    /**
     * Draw a single message arrow in UML style with protocol annotation (Phase 2)
     * Enhanced with RCA failure highlighting
     */
    private void drawMessage(GraphicsContext gc, SipMessage message, double y, boolean isFailureMessage) {
        // Find actor indices
        int sourceIndex = actors.indexOf(message.getSourceActor());
        int targetIndex = actors.indexOf(message.getTargetActor());
        
        // Fallback to client-server if actors not found
        if (sourceIndex == -1) sourceIndex = 0;
        if (targetIndex == -1) targetIndex = actors.size() > 1 ? 1 : 0;
        
        double startX = getLifelineX(sourceIndex);
        double endX = getLifelineX(targetIndex);
        boolean isLeftToRight = startX < endX;
        
        // Get protocol color (override with red for failure highlight)
        ProtocolType protocol = message.getProtocolType();
        Color arrowColor;
        if (isFailureMessage) {
            arrowColor = Color.rgb(200, 0, 0); // Dark red for failed message
        } else {
            arrowColor = protocol != null ? protocol.getColor() : 
                              (message.isSuccess() ? COLOR_SUCCESS : COLOR_FAILURE);
        }
        
        // Draw arrow line (thicker for failure)
        gc.setStroke(arrowColor);
        gc.setLineWidth(isFailureMessage ? 4.0 : 2.5);
        gc.strokeLine(startX, y, endX, y);
        
        // Draw arrowhead
        drawArrowHead(gc, endX, y, isLeftToRight, arrowColor);
        
        // Draw message label above arrow
        String label = message.getMessageType().getDisplayName();
        gc.setFill(COLOR_TEXT);
        gc.setFont(Font.font("Segoe UI", FontWeight.BOLD, 11));
        gc.setTextAlign(isLeftToRight ? TextAlignment.LEFT : TextAlignment.RIGHT);
        gc.setTextBaseline(VPos.BOTTOM);
        
        double labelX = isLeftToRight ? startX + 8 : startX - 8;
        gc.fillText(label, labelX, y - 8);
        
        // Phase 2: Draw protocol annotation below arrow
        if (protocol != null && protocol != ProtocolType.SIP) {
            gc.setFill(protocol.getColor());
            gc.setFont(Font.font("Segoe UI", FontWeight.NORMAL, 9));
            gc.setTextBaseline(VPos.TOP);
            gc.fillText("[" + protocol.getDisplayName() + "]", labelX, y + 2);
        } else {
            // Draw elapsed time if no special protocol
            gc.setFill(COLOR_INFO);
            gc.setFont(Font.font("Segoe UI", FontWeight.NORMAL, 9));
            gc.setTextBaseline(VPos.TOP);
            gc.fillText(message.getElapsed() + "ms", labelX, y + 2);
        }
        
        // Draw status indicator at end of arrow
        String statusIcon = message.isSuccess() ? "✓" : "✗";
        gc.setFill(message.isSuccess() ? COLOR_SUCCESS : COLOR_FAILURE);
        gc.setFont(Font.font("Segoe UI", FontWeight.BOLD, 12));
        gc.setTextAlign(TextAlignment.CENTER);
        double statusX = isLeftToRight ? endX + 12 : endX - 12;
        gc.fillText(statusIcon, statusX, y + 5);
    }
    
    /**
     * Draw an arrowhead at the specified position
     */
    private void drawArrowHead(GraphicsContext gc, double x, double y, boolean pointingRight, Color color) {
        gc.setFill(color);
        
        double[] xPoints;
        double[] yPoints;
        
        if (pointingRight) {
            xPoints = new double[]{x, x - ARROW_HEAD_SIZE, x - ARROW_HEAD_SIZE};
            yPoints = new double[]{y, y - ARROW_HEAD_SIZE / 2, y + ARROW_HEAD_SIZE / 2};
        } else {
            xPoints = new double[]{x, x + ARROW_HEAD_SIZE, x + ARROW_HEAD_SIZE};
            yPoints = new double[]{y, y - ARROW_HEAD_SIZE / 2, y + ARROW_HEAD_SIZE / 2};
        }
        
        gc.fillPolygon(xPoints, yPoints, 3);
    }
    
    /**
     * Draw statistics panel vertically to the right of all actors (Phase 1)
     */
    private void drawStatistics(GraphicsContext gc, List<SipMessage> messages) {
        // Position after last actor
        double statsX = getActorX(actors.size() - 1) + ACTOR_WIDTH + 30;
        double statsY = MARGIN;
        double statsBoxWidth = STATS_WIDTH - 40;
        double statsBoxHeight = 130;
        
        // Draw statistics background
        gc.setFill(Color.rgb(250, 250, 250));
        gc.fillRoundRect(statsX, statsY, statsBoxWidth, statsBoxHeight, 8, 8);
        gc.setStroke(COLOR_BORDER);
        gc.setLineWidth(1);
        gc.strokeRoundRect(statsX, statsY, statsBoxWidth, statsBoxHeight, 8, 8);
        
        // Draw statistics title
        gc.setFill(COLOR_TEXT);
        gc.setFont(Font.font("Segoe UI", FontWeight.BOLD, 12));
        gc.setTextAlign(TextAlignment.LEFT);
        gc.setTextBaseline(VPos.TOP);
        gc.fillText("Call Flow Stats", statsX + 10, statsY + 8);
        
        // Draw statistics items
        gc.setFont(Font.font("Segoe UI", FontWeight.NORMAL, 11));
        double lineY = statsY + 28;
        double lineHeight = 18;
        
        // Actors count (Phase 1)
        gc.setFill(COLOR_TEXT);
        gc.fillText(String.format("Actors: %d", actors.size()), 
            statsX + 10, lineY);
        lineY += lineHeight;
        
        // Messages count
        gc.fillText(String.format("Messages: %d", callFlow.getTotalMessages()), 
            statsX + 10, lineY);
        lineY += lineHeight;
        
        // Successful count with color
        gc.setFill(COLOR_SUCCESS);
        gc.fillText(String.format("Success: %d (%.0f%%)", 
            callFlow.getSuccessfulMessages(), callFlow.getSuccessRate()), 
            statsX + 10, lineY);
        lineY += lineHeight;
        
        // Duration
        gc.setFill(COLOR_TEXT);
        gc.fillText(String.format("Duration: %.1fs", callFlow.getTotalDuration() / 1000.0), 
            statsX + 10, lineY);
        lineY += lineHeight;
        
        // Status with icon
        if (callFlow.isCallCompleted()) {
            gc.setFill(COLOR_SUCCESS);
            gc.fillText("Status: ✓ Complete", statsX + 10, lineY);
        } else {
            gc.setFill(COLOR_FAILURE);
            gc.fillText("Status: ✗ Incomplete", statsX + 10, lineY);
        }
    }
    
    /**
     * Draw red background highlight for failed message (RCA support)
     */
    private void drawFailureHighlight(GraphicsContext gc, double y, SipMessage message) {
        // Draw red background rectangle across the full width
        gc.setFill(Color.rgb(255, 200, 200, 0.3)); // Light red with transparency
        gc.fillRect(MARGIN, y - MESSAGE_HEIGHT / 2 + 10, diagramWidth - (2 * MARGIN), MESSAGE_HEIGHT - 5);
        
        // Draw red border
        gc.setStroke(Color.rgb(200, 0, 0));
        gc.setLineWidth(2);
        gc.setLineDashes(5, 5);
        gc.strokeRect(MARGIN, y - MESSAGE_HEIGHT / 2 + 10, diagramWidth - (2 * MARGIN), MESSAGE_HEIGHT - 5);
        gc.setLineDashes(0); // Reset
        
        // Draw failure icon
        gc.setFill(Color.rgb(200, 0, 0));
        gc.setFont(Font.font("Segoe UI", FontWeight.BOLD, 20));
        gc.setTextAlign(TextAlignment.LEFT);
        gc.setTextBaseline(VPos.CENTER);
        gc.fillText("⚠", MARGIN + 5, y);
    }
    
    /**
     * Draw the legend explaining colors, symbols, and protocols (Phase 2)
     */
    private void drawLegend(GraphicsContext gc) {
        double legendY = getHeight() - LEGEND_HEIGHT - MARGIN / 2;
        double legendX = MARGIN;
        double legendWidth = getWidth() - MARGIN * 2;
        
        // Draw legend background
        gc.setFill(Color.rgb(250, 250, 250));
        gc.fillRect(legendX, legendY, legendWidth, LEGEND_HEIGHT);
        gc.setStroke(COLOR_BORDER);
        gc.setLineWidth(1);
        gc.strokeRect(legendX, legendY, legendWidth, LEGEND_HEIGHT);
        
        // Draw legend title
        gc.setFill(COLOR_TEXT);
        gc.setFont(Font.font("Segoe UI", FontWeight.BOLD, 11));
        gc.setTextAlign(TextAlignment.LEFT);
        gc.setTextBaseline(VPos.TOP);
        gc.fillText("Legend:", legendX + 10, legendY + 8);
        
        // Row 1: Status indicators
        double itemY = legendY + 26;
        double itemSpacing = 120;
        gc.setFont(Font.font("Segoe UI", FontWeight.NORMAL, 10));
        
        drawLegendItem(gc, legendX + 10, itemY, COLOR_SUCCESS, "✓ Success");
        drawLegendItem(gc, legendX + 10 + itemSpacing, itemY, COLOR_FAILURE, "✗ Failed");
        
        // Row 2: Key protocols (Phase 2)
        double protocolRow2Y = itemY + 24;
        gc.setFill(COLOR_TEXT);
        gc.fillText("Protocols:", legendX + 10, protocolRow2Y - 6);
        
        double protocolX = legendX + 80;
        drawProtocolLegendItem(gc, protocolX, protocolRow2Y, ProtocolType.SIP);
        protocolX += 100;
        drawProtocolLegendItem(gc, protocolX, protocolRow2Y, ProtocolType.DIAMETER_CX);
        protocolX += 120;
        drawProtocolLegendItem(gc, protocolX, protocolRow2Y, ProtocolType.DIAMETER_S6A);
    }
    
    /**
     * Draw a single legend item with color indicator
     */
    private void drawLegendItem(GraphicsContext gc, double x, double y, Color color, String text) {
        // Draw color indicator
        gc.setFill(color);
        gc.fillOval(x, y, 12, 12);
        
        // Draw text
        gc.setFill(COLOR_TEXT);
        gc.setFont(Font.font("Segoe UI", FontWeight.NORMAL, 10));
        gc.setTextAlign(TextAlignment.LEFT);
        gc.fillText(text, x + 18, y + 2);
    }
    
    /**
     * Draw a protocol legend item (Phase 2)
     */
    private void drawProtocolLegendItem(GraphicsContext gc, double x, double y, ProtocolType protocol) {
        // Draw protocol color bar
        gc.setFill(protocol.getColor());
        gc.fillRect(x, y, 20, 8);
        gc.setStroke(COLOR_BORDER);
        gc.setLineWidth(0.5);
        gc.strokeRect(x, y, 20, 8);
        
        // Draw protocol name
        gc.setFill(COLOR_TEXT);
        gc.setFont(Font.font("Segoe UI", FontWeight.NORMAL, 9));
        gc.setTextAlign(TextAlignment.LEFT);
        gc.fillText(protocol.getDisplayName(), x + 24, y + 2);
    }
    
    /**
     * Generate message-specific tooltip text with contextual explanation.
     * Provides business-level interpretation based on message type and status.
     * 
     * @param message The SIP message to generate tooltip for
     * @param messageIndex The index of this message in the call flow (0-based)
     * @return Formatted tooltip text with contextual information
     */
    private String getMessageTooltipText(SipMessage message, int messageIndex) {
        StringBuilder tooltip = new StringBuilder();
        
        // Header with message type and status indicator
        String statusIcon = message.isSuccess() ? "✓" : "✗";
        String statusText = message.isSuccess() ? "Successful" : "Failed";
        
        tooltip.append("═══════════════════════════════\n");
        tooltip.append(String.format("%s %s - %s\n", 
            statusIcon, 
            message.getMessageType().getDisplayName(),
            getMessageTypeDescription(message.getMessageType())));
        tooltip.append("═══════════════════════════════\n\n");
        
        // Status section with business meaning
        tooltip.append("Status: ").append(statusText).append("\n");
        tooltip.append("Meaning: ").append(getMessageMeaning(message)).append("\n");
        tooltip.append("Direction: ").append(message.getDirection().getDisplayName()).append("\n\n");
        
        // Timing section
        tooltip.append("Timing: ").append(message.getElapsed()).append("ms");
        tooltip.append(getTimingContext(message.getElapsed())).append("\n");
        tooltip.append("Position: Message ").append(messageIndex + 1)
            .append(" of ").append(callFlow.getMessages().size()).append("\n");
        tooltip.append("Phase: ").append(getCallPhase(message.getMessageType())).append("\n\n");
        
        // Technical Details section
        tooltip.append("Technical Details:\n");
        tooltip.append("Response Code: ").append(message.getResponseCode()).append("\n");
        tooltip.append("Thread: ").append(message.getThreadName()).append("\n");
        
        // Show raw label for OTHER messages to help with debugging
        if (message.getMessageType() == SipMessage.MessageType.OTHER) {
            tooltip.append("Raw Label: ").append(message.getLabel()).append("\n");
            tooltip.append("(This message type is not recognized by the parser)\n");
        }
        
        tooltip.append("Timestamp: ").append(new java.text.SimpleDateFormat("HH:mm:ss.SSS")
            .format(new java.util.Date(message.getTimestamp()))).append("\n");
        
        return tooltip.toString();
    }
    
    /**
     * Get a short description of the message type
     */
    private String getMessageTypeDescription(SipMessage.MessageType type) {
        switch (type) {
            case INVITE: return "Call Setup Request";
            case TRYING: return "Processing";
            case RINGING: return "Alerting";
            case OK: return "Acknowledgment";
            case ACK: return "Confirmation";
            case BYE: return "Hangup";
            case CANCEL: return "Cancellation";
            case REGISTER: return "Registration";
            case OPTIONS: return "Capability Query";
            case INFO: return "Mid-Call Info";
            case PRACK: return "Provisional ACK";
            case UPDATE: return "Session Update";
            case SUBSCRIBE: return "Event Subscription";
            case NOTIFY: return "Event Notification";
            case OTHER: return "Unrecognized Message";
            default: return "Message";
        }
    }
    
    /**
     * Get business-level meaning based on message type and success status
     */
    private String getMessageMeaning(SipMessage message) {
        boolean success = message.isSuccess();
        
        switch (message.getMessageType()) {
            case INVITE:
                return success ? 
                    "Client initiated VoLTE call establishment" :
                    "Failed to initiate call - check network connectivity";
            case TRYING:
                return success ?
                    "Server processing request, waiting for final response" :
                    "Server failed to process request";
            case RINGING:
                return success ?
                    "Destination is ringing, waiting for answer" :
                    "Failed to alert remote party";
            case OK:
                if (message.getDirection() == SipMessage.Direction.SERVER_TO_CLIENT) {
                    return success ?
                        "Call established - server confirmed connection" :
                        "Expected confirmation but got error or timeout";
                } else {
                    return success ?
                        "Acknowledgment sent successfully" :
                        "Failed to send acknowledgment";
                }
            case ACK:
                return success ?
                    "Call flow handshake completed successfully" :
                    "Handshake failed - connection may be unstable";
            case BYE:
                return success ?
                    "Call terminated gracefully" :
                    "Failed to terminate call properly";
            case CANCEL:
                return success ?
                    "Call attempt cancelled successfully" :
                    "Failed to cancel call";
            case REGISTER:
                return success ?
                    "Device registered with IMS network" :
                    "Registration failed - authentication issue";
            case OPTIONS:
                return success ?
                    "Capability negotiation successful" :
                    "Failed to query capabilities";
            case INFO:
                return success ?
                    "Mid-call information delivered" :
                    "Failed to deliver information";
            case PRACK:
                return success ?
                    "Reliable provisional response acknowledged" :
                    "Failed to acknowledge provisional response";
            case UPDATE:
                return success ?
                    "Session parameters updated" :
                    "Failed to update session";
            case SUBSCRIBE:
                return success ?
                    "Subscribed to event notifications" :
                    "Failed to subscribe to events";
            case NOTIFY:
                return success ?
                    "Event notification delivered" :
                    "Failed to deliver notification";
            case OTHER:
                return success ?
                    "Unrecognized message - hover to see raw label" :
                    "Unrecognized message failed";
            default:
                return success ?
                    "Message exchanged successfully" :
                    "Message failed or timed out";
        }
    }
    
    /**
     * Get timing context based on elapsed time
     */
    private String getTimingContext(long elapsed) {
        if (elapsed < 50) {
            return " (very fast - cached or local response)";
        } else if (elapsed < 200) {
            return " (normal network latency)";
        } else if (elapsed < 1000) {
            return " (acceptable - within tolerance)";
        } else if (elapsed < 5000) {
            return " (slower than expected - may indicate network issues)";
        } else {
            return " (very slow - investigate network or server performance)";
        }
    }
    
    /**
     * Determine which phase of the call this message belongs to
     */
    private String getCallPhase(SipMessage.MessageType type) {
        switch (type) {
            case INVITE:
            case TRYING:
            case RINGING:
                return "Call Establishment";
            case OK:
            case ACK:
                return "Connection Confirmation";
            case BYE:
            case CANCEL:
                return "Call Teardown";
            case REGISTER:
                return "Network Registration";
            default:
                return "Unknown Phase";
        }
    }
    
    /**
     * Handle mouse movement for tooltips in UML layout
     */
    private void handleMouseMoved(MouseEvent event) {
        double mouseX = event.getX();
        double mouseY = event.getY();
        
        // Find which message the mouse is over
        double startY = MARGIN + TOP_MARGIN;
        int messageIndex = (int) ((mouseY - startY) / MESSAGE_HEIGHT);
        
        List<SipMessage> messages = callFlow.getMessages();
        if (messageIndex >= 0 && messageIndex < messages.size()) {
            SipMessage message = messages.get(messageIndex);
            
            // Generate message-specific tooltip with contextual information
            String tooltipText = getMessageTooltipText(message, messageIndex);
            
            messageTooltip.setText(tooltipText);
            Tooltip.install(this, messageTooltip);
        } else {
            Tooltip.uninstall(this, messageTooltip);
        }
    }
}
