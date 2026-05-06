package com.tts.demo.component;

import com.tts.demo.model.CallFlow;
import com.tts.demo.model.CallFlowUpdateListener;
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

import java.util.List;

/**
 * Custom JavaFX Canvas control for rendering SIP call flow sequence diagrams.
 * Displays client-server message exchanges with timing and status information.
 * Supports real-time updates via CallFlowUpdateListener (Phase 2.2).
 */
public class CallFlowDiagram extends Canvas implements CallFlowUpdateListener {
    
    // Layout constants for UML sequence diagram
    private static final double MARGIN = 40;
    private static final double ACTOR_WIDTH = 80;      // Width of actor boxes
    private static final double ACTOR_HEIGHT = 40;     // Height of actor boxes
    private static final double LIFELINE_SPACING = 200; // Horizontal space between lifelines
    private static final double MESSAGE_HEIGHT = 50;    // Vertical space per message
    private static final double TOP_MARGIN = 80;        // Space for actors at top
    private static final double LEGEND_HEIGHT = 80;
    private static final double ARROW_HEAD_SIZE = 8;
    private static final double LIFELINE_DASH = 5;      // Dash pattern for lifelines
    private static final double DIAGRAM_WIDTH = 400;    // Fixed width for UML diagram
    
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
    private final List<SipMessage> messages;
    private Tooltip messageTooltip;
    
    /**
     * Create a CallFlowDiagram for visualizing the given call flow
     * 
     * @param callFlow The call flow to visualize
     */
    public CallFlowDiagram(CallFlow callFlow) {
        this.callFlow = callFlow;
        this.messages = callFlow.getMessages();
        
        // Calculate required canvas size based on UML layout
        double requiredWidth = DIAGRAM_WIDTH;
        double requiredHeight = MARGIN * 2 + TOP_MARGIN + (messages.size() * MESSAGE_HEIGHT) + LEGEND_HEIGHT;
        
        setWidth(requiredWidth);
        setHeight(Math.max(600, requiredHeight));
        
        // Setup tooltip for hover interactions
        messageTooltip = new Tooltip();
        
        // Add mouse hover handler
        setOnMouseMoved(this::handleMouseMoved);
        
        // Render the diagram
        render();
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
        double requiredWidth = DIAGRAM_WIDTH;
        double requiredHeight = MARGIN * 2 + TOP_MARGIN + (messages.size() * MESSAGE_HEIGHT) + LEGEND_HEIGHT;
        
        setWidth(requiredWidth);
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
        
        // Check if throttle period has passed
        if (now - lastRefreshTime >= THROTTLE_MS) {
            // Immediate refresh
            lastRefreshTime = now;
            refreshPending = false;
            Platform.runLater(this::refresh);
        } else {
            // Schedule a delayed refresh if not already pending
            if (!refreshPending) {
                refreshPending = true;
                long delay = THROTTLE_MS - (now - lastRefreshTime);
                
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
            }
        }
    }
    
    /**
     * Render the complete call flow diagram in UML sequence diagram style.
     * Changed to public for incremental rendering support (Phase 2.1).
     */
    public void render() {
        GraphicsContext gc = getGraphicsContext2D();
        
        // Clear canvas
        gc.setFill(COLOR_BACKGROUND);
        gc.fillRect(0, 0, getWidth(), getHeight());
        
        // Draw UML components in order
        drawActors(gc);
        drawLifelines(gc);
        drawMessages(gc);
        drawLegend(gc);
    }
    
    /**
     * Draw the actor boxes at the top (Client and Server)
     */
    private void drawActors(GraphicsContext gc) {
        double clientX = MARGIN;
        double serverX = MARGIN + LIFELINE_SPACING;
        double actorY = MARGIN;
        
        // Draw actor boxes
        gc.setFill(Color.rgb(52, 73, 94)); // Dark blue-gray header
        gc.fillRect(clientX, actorY, ACTOR_WIDTH, ACTOR_HEIGHT);
        gc.fillRect(serverX, actorY, ACTOR_WIDTH, ACTOR_HEIGHT);
        
        // Draw actor borders
        gc.setStroke(COLOR_BORDER);
        gc.setLineWidth(2);
        gc.strokeRect(clientX, actorY, ACTOR_WIDTH, ACTOR_HEIGHT);
        gc.strokeRect(serverX, actorY, ACTOR_WIDTH, ACTOR_HEIGHT);
        
        // Draw actor labels
        gc.setFill(Color.WHITE);
        gc.setFont(Font.font("Segoe UI", FontWeight.BOLD, 14));
        gc.setTextAlign(TextAlignment.CENTER);
        gc.setTextBaseline(VPos.CENTER);
        
        gc.fillText("Client", clientX + ACTOR_WIDTH / 2, actorY + ACTOR_HEIGHT / 2);
        gc.fillText("Server", serverX + ACTOR_WIDTH / 2, actorY + ACTOR_HEIGHT / 2);
    }
    
    /**
     * Draw the vertical lifelines extending down from actors
     */
    private void drawLifelines(GraphicsContext gc) {
        double clientX = MARGIN + ACTOR_WIDTH / 2;
        double serverX = MARGIN + LIFELINE_SPACING + ACTOR_WIDTH / 2;
        double startY = MARGIN + ACTOR_HEIGHT;
        double endY = MARGIN + TOP_MARGIN + (messages.size() * MESSAGE_HEIGHT);
        
        // Draw dashed lifelines
        gc.setStroke(COLOR_BORDER);
        gc.setLineWidth(1);
        gc.setLineDashes(LIFELINE_DASH, LIFELINE_DASH);
        
        gc.strokeLine(clientX, startY, clientX, endY);
        gc.strokeLine(serverX, startY, serverX, endY);
        
        // Reset line dashes for other drawing
        gc.setLineDashes(0);
    }
    
    /**
     * Draw all SIP messages as horizontal arrows between lifelines
     */
    private void drawMessages(GraphicsContext gc) {
        double clientX = MARGIN + ACTOR_WIDTH / 2;
        double serverX = MARGIN + LIFELINE_SPACING + ACTOR_WIDTH / 2;
        double startY = MARGIN + TOP_MARGIN;
        
        for (int i = 0; i < messages.size(); i++) {
            SipMessage message = messages.get(i);
            double y = startY + (i * MESSAGE_HEIGHT);
            
            drawMessage(gc, message, clientX, serverX, y);
        }
    }
    
    /**
     * Draw a single message arrow in UML style
     */
    private void drawMessage(GraphicsContext gc, SipMessage message, double clientX, double serverX, double y) {
        // Determine arrow direction and color
        boolean isClientToServer = message.getDirection() == SipMessage.Direction.CLIENT_TO_SERVER;
        double startX = isClientToServer ? clientX : serverX;
        double endX = isClientToServer ? serverX : clientX;
        
        Color arrowColor = message.isSuccess() ? COLOR_SUCCESS : COLOR_FAILURE;
        
        // Draw arrow line
        gc.setStroke(arrowColor);
        gc.setLineWidth(2);
        gc.strokeLine(startX, y, endX, y);
        
        // Draw arrowhead
        drawArrowHead(gc, endX, y, isClientToServer, arrowColor);
        
        // Draw message label above arrow
        String label = message.getMessageType().getDisplayName();
        gc.setFill(COLOR_TEXT);
        gc.setFont(Font.font("Segoe UI", FontWeight.NORMAL, 11));
        gc.setTextAlign(isClientToServer ? TextAlignment.LEFT : TextAlignment.RIGHT);
        gc.setTextBaseline(VPos.BOTTOM);
        
        double labelX = isClientToServer ? startX + 5 : startX - 5;
        gc.fillText(label, labelX, y - 5);
        
        // Draw elapsed time below arrow
        gc.setFill(COLOR_INFO);
        gc.setFont(Font.font("Segoe UI", FontWeight.NORMAL, 9));
        gc.setTextBaseline(VPos.TOP);
        gc.fillText(message.getElapsed() + "ms", labelX, y + 3);
        
        // Draw status indicator at end of arrow
        String statusIcon = message.isSuccess() ? "✓" : "✗";
        gc.setFill(arrowColor);
        gc.setFont(Font.font("Segoe UI", FontWeight.BOLD, 12));
        gc.setTextAlign(TextAlignment.CENTER);
        double statusX = isClientToServer ? endX + 12 : endX - 12;
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
     * Draw the legend explaining colors and symbols
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
        gc.setFont(Font.font("Segoe UI", FontWeight.BOLD, 12));
        gc.setTextAlign(TextAlignment.LEFT);
        gc.setTextBaseline(VPos.TOP);
        gc.fillText("Legend:", legendX + 10, legendY + 10);
        
        // Draw legend items
        double itemY = legendY + 30;
        double itemSpacing = 150;
        gc.setFont(Font.font("Segoe UI", FontWeight.NORMAL, 11));
        
        // Success indicator
        drawLegendItem(gc, legendX + 10, itemY, COLOR_SUCCESS, "✓ Success");
        
        // Failure indicator
        drawLegendItem(gc, legendX + 10 + itemSpacing, itemY, COLOR_FAILURE, "✗ Failed");
        
        // Direction indicators
        gc.setFill(COLOR_TEXT);
        gc.fillText("→ Client to Server", legendX + 10, itemY + 20);
        gc.fillText("← Server to Client", legendX + 10 + itemSpacing, itemY + 20);
        
        // Draw call flow summary
        String summary = String.format("Call Flow: %d messages | %d successful (%.1f%%) | Duration: %.1fs | Status: %s",
                callFlow.getTotalMessages(),
                callFlow.getSuccessfulMessages(),
                callFlow.getSuccessRate(),
                callFlow.getTotalDuration() / 1000.0,
                callFlow.isCallCompleted() ? "✓ Completed" : "✗ Incomplete");
        
        gc.setFill(COLOR_TEXT);
        gc.setFont(Font.font("Segoe UI", FontWeight.BOLD, 11));
        gc.setTextAlign(TextAlignment.CENTER);
        gc.fillText(summary, getWidth() / 2, legendY + LEGEND_HEIGHT - 15);
    }
    
    /**
     * Draw a single legend item
     */
    private void drawLegendItem(GraphicsContext gc, double x, double y, Color color, String text) {
        // Draw color indicator
        gc.setFill(color);
        gc.fillOval(x, y, 12, 12);
        
        // Draw text
        gc.setFill(COLOR_TEXT);
        gc.setTextAlign(TextAlignment.LEFT);
        gc.setTextBaseline(VPos.CENTER);
        gc.fillText(text, x + 20, y + 6);
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
            .append(" of ").append(messages.size()).append("\n");
        tooltip.append("Phase: ").append(getCallPhase(message.getMessageType())).append("\n\n");
        
        // Technical Details section
        tooltip.append("Technical Details:\n");
        tooltip.append("Response Code: ").append(message.getResponseCode()).append("\n");
        tooltip.append("Thread: ").append(message.getThreadName()).append("\n");
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
