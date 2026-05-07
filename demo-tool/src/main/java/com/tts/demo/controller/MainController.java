package com.tts.demo.controller;

import com.tts.demo.component.CallFlowDiagram;
import com.tts.demo.model.CallFlow;
import com.tts.demo.model.Demo;
import com.tts.demo.model.DemoConfig;
import com.tts.demo.model.RunResult;
import com.tts.demo.model.SipMessage;
import com.tts.demo.service.ConfigManager;
import com.tts.demo.service.DemoCatalog;
import com.tts.demo.service.DemoRunner;
import com.tts.demo.service.JtlParser;
import javafx.application.Platform;
import javafx.embed.swing.SwingFXUtils;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.SnapshotParameters;
import javafx.scene.control.*;
import javafx.scene.image.WritableImage;
import javafx.scene.layout.*;
import javafx.stage.Modality;
import javafx.stage.Stage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.imageio.ImageIO;
import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Main controller for the TTS Demo Tool application.
 * Manages the demo catalog view, demo execution, and live output streaming.
 */
public class MainController {
    
    private static final Logger logger = LoggerFactory.getLogger(MainController.class);
    
    @FXML private TextField searchField;
    @FXML private ComboBox<String> protocolFilter;
    @FXML private ComboBox<String> complexityFilter;
    @FXML private Label demoCountLabel;
    @FXML private VBox demoListContainer;
    
    @FXML private VBox demoDetailsPane;
    @FXML private VBox placeholderPane;
    @FXML private Label demoTitleLabel;
    @FXML private Label protocolBadge;
    @FXML private Label complexityBadge;
    @FXML private Label demoDescriptionLabel;
    @FXML private Label demoOutcomeLabel;
    @FXML private GridPane parametersGrid;
    @FXML private Button runButton;
    @FXML private Button stopButton;
    @FXML private ProgressIndicator progressIndicator;
    @FXML private Label statusLabel;
    @FXML private TextArea outputTextArea;
    
    // Tabbed Interface components
    @FXML private TabPane demoTabPane;
    @FXML private Tab configTab;
    @FXML private Tab executionTab;
    @FXML private Button executionTabStopButton;
    
    // Call Flow Visualization components (Phase 4+5)
    @FXML private CheckBox showTerminalCheckBox;
    @FXML private Button exportDiagramButton;
    @FXML private Label callFlowStatusLabel;
    @FXML private SplitPane visualizationSplitPane;
    @FXML private StackPane diagramContainer;
    @FXML private TitledPane terminalPane;
    
    @FXML private Label ttsStatusLabel;
    @FXML private Label historyCountLabel;
    
    private DemoCatalog catalog;
    private ConfigManager configManager;
    private DemoRunner demoRunner;
    private JtlParser jtlParser;
    
    private Demo selectedDemo;
    private DemoConfig currentConfig;
    private Map<String, TextField> parameterFields;
    private CallFlowDiagram currentDiagram;
    
    // Real-time call flow visualization fields (Phase 1.3)
    private final List<SipMessage> liveMessages = Collections.synchronizedList(new ArrayList<>());
    private volatile CallFlow liveCallFlow = null;

    @FXML
    public void initialize() {
        logger.info("Initializing MainController");
        
        // Initialize services
        catalog = new DemoCatalog();
        configManager = new ConfigManager();
        demoRunner = new DemoRunner(configManager);
        jtlParser = new JtlParser();
        
        parameterFields = new HashMap<>();
        
        // Initialize filters
        initializeFilters();
        
        // Load initial demo list
        refreshDemoList();
        
        // Validate TTS installation
        validateTTSInstallation();
        
        // Update history count
        updateHistoryCount();
        
        // Initialize tab state
        if (demoTabPane != null && configTab != null) {
            demoTabPane.getSelectionModel().select(configTab);
            logger.debug("Initialized tab selection to Configuration tab");
        }
        
        logger.info("MainController initialized with {} demos", catalog.getDemoCount());
    }
    
    /**
     * Switch to the Execution tab
     */
    private void switchToExecutionTab() {
        if (demoTabPane != null && executionTab != null) {
            demoTabPane.getSelectionModel().select(executionTab);
            logger.debug("Switched to Execution tab");
        }
    }
    
    /**
     * Switch to the Configuration tab
     */
    private void switchToConfigTab() {
        if (demoTabPane != null && configTab != null) {
            demoTabPane.getSelectionModel().select(configTab);
            logger.debug("Switched to Configuration tab");
        }
    }
    
    /**
     * Enable or disable the Configuration tab
     * 
     * @param disabled true to disable the tab, false to enable
     */
    private void setConfigTabDisabled(boolean disabled) {
        if (configTab != null) {
            configTab.setDisable(disabled);
            logger.debug("Configuration tab disabled: {}", disabled);
        }
    }

    private void initializeFilters() {
        // Protocol filter
        protocolFilter.getItems().add("All Protocols");
        for (Demo.Protocol protocol : Demo.Protocol.values()) {
            protocolFilter.getItems().add(protocol.getDisplayName());
        }
        protocolFilter.setValue("All Protocols");
        
        // Complexity filter
        complexityFilter.getItems().add("All Levels");
        for (Demo.Complexity complexity : Demo.Complexity.values()) {
            complexityFilter.getItems().add(complexity.getDisplayName());
        }
        complexityFilter.setValue("All Levels");
    }

    @FXML
    private void handleSearch() {
        refreshDemoList();
    }

    @FXML
    private void handleFilterChange() {
        refreshDemoList();
    }

    @FXML
    private void handleClearFilters() {
        searchField.clear();
        protocolFilter.setValue("All Protocols");
        complexityFilter.setValue("All Levels");
        refreshDemoList();
    }

    private void refreshDemoList() {
        List<Demo> demos = getFilteredDemos();
        
        demoListContainer.getChildren().clear();
        
        for (Demo demo : demos) {
            VBox demoCard = createDemoCard(demo);
            demoListContainer.getChildren().add(demoCard);
        }
        
        demoCountLabel.setText(demos.size() + " demo" + (demos.size() != 1 ? "s" : ""));
    }

    private List<Demo> getFilteredDemos() {
        List<Demo> demos = catalog.getAllDemos();
        
        // Apply search filter
        String searchText = searchField.getText();
        if (searchText != null && !searchText.trim().isEmpty()) {
            demos = catalog.searchDemos(searchText);
        }
        
        // Apply protocol filter
        String protocol = protocolFilter.getValue();
        if (protocol != null && !protocol.equals("All Protocols")) {
            Demo.Protocol selectedProtocol = findProtocolByDisplayName(protocol);
            if (selectedProtocol != null) {
                demos = demos.stream()
                        .filter(d -> d.getProtocol() == selectedProtocol)
                        .collect(Collectors.toList());
            }
        }
        
        // Apply complexity filter
        String complexity = complexityFilter.getValue();
        if (complexity != null && !complexity.equals("All Levels")) {
            Demo.Complexity selectedComplexity = findComplexityByDisplayName(complexity);
            if (selectedComplexity != null) {
                demos = demos.stream()
                        .filter(d -> d.getComplexity() == selectedComplexity)
                        .collect(Collectors.toList());
            }
        }
        
        return demos;
    }

    private VBox createDemoCard(Demo demo) {
        VBox card = new VBox(8);
        card.getStyleClass().add("demo-card");
        card.setPadding(new Insets(15));
        card.setCursor(javafx.scene.Cursor.HAND);
        
        // Title
        Label title = new Label(demo.getTitle());
        title.getStyleClass().add("demo-title");
        title.setWrapText(true);
        
        // Badges
        HBox badges = new HBox(8);
        
        Label protocolLabel = new Label(demo.getProtocol().getDisplayName());
        protocolLabel.getStyleClass().addAll("protocol-badge", getProtocolStyleClass(demo.getProtocol()));
        
        Label complexityLabel = new Label(demo.getComplexity().getDisplayName());
        complexityLabel.getStyleClass().addAll("complexity-badge", getComplexityStyleClass(demo.getComplexity()));
        
        badges.getChildren().addAll(protocolLabel, complexityLabel);
        
        // Description (truncated)
        Label description = new Label(truncateText(demo.getDescription(), 120));
        description.getStyleClass().add("demo-description");
        description.setWrapText(true);
        
        card.getChildren().addAll(title, badges, description);
        
        // Click handler
        card.setOnMouseClicked(event -> selectDemo(demo));
        
        return card;
    }

    private void selectDemo(Demo demo) {
        selectedDemo = demo;
        currentConfig = new DemoConfig(demo.getId());
        
        // Show details pane, hide placeholder
        placeholderPane.setVisible(false);
        placeholderPane.setManaged(false);
        demoDetailsPane.setVisible(true);
        demoDetailsPane.setManaged(true);
        
        // Update UI
        demoTitleLabel.setText(demo.getTitle());
        
        protocolBadge.setText(demo.getProtocol().getDisplayName());
        protocolBadge.getStyleClass().clear();
        protocolBadge.getStyleClass().addAll("protocol-badge", getProtocolStyleClass(demo.getProtocol()));
        
        complexityBadge.setText(demo.getComplexity().getDisplayName());
        complexityBadge.getStyleClass().clear();
        complexityBadge.getStyleClass().addAll("complexity-badge", getComplexityStyleClass(demo.getComplexity()));
        
        demoDescriptionLabel.setText(demo.getDescription());
        demoOutcomeLabel.setText(demo.getExpectedOutcome());
        
        // Build parameters grid
        buildParametersGrid(demo);
        
        // Clear output
        outputTextArea.clear();
        statusLabel.setText("");
        
        // Switch to Configuration tab and enable it
        switchToConfigTab();
        setConfigTabDisabled(false);
        
        logger.info("Selected demo: {}", demo.getTitle());
    }

    private void buildParametersGrid(Demo demo) {
        parametersGrid.getChildren().clear();
        parameterFields.clear();
        
        int row = 0;
        for (Map.Entry<String, String> entry : demo.getDefaultParams().entrySet()) {
            Label label = new Label(entry.getKey() + ":");
            label.setStyle("-fx-font-weight: bold;");
            
            TextField textField = new TextField(entry.getValue());
            textField.setPrefWidth(300);
            
            parametersGrid.add(label, 0, row);
            parametersGrid.add(textField, 1, row);
            
            parameterFields.put(entry.getKey(), textField);
            row++;
        }
    }

    @FXML
    private void handleRunDemo() {
        if (selectedDemo == null) {
            showAlert("No Demo Selected", "Please select a demo to run.", Alert.AlertType.WARNING);
            return;
        }
        
        // Collect parameters
        for (Map.Entry<String, TextField> entry : parameterFields.entrySet()) {
            currentConfig.setParameter(entry.getKey(), entry.getValue().getText());
        }
        
        // Update UI state
        runButton.setDisable(true);
        stopButton.setDisable(false);
        if (executionTabStopButton != null) {
            executionTabStopButton.setDisable(false);
        }
        progressIndicator.setVisible(true);
        statusLabel.setText("Running...");
        statusLabel.getStyleClass().clear();
        statusLabel.getStyleClass().add("status-running");
        outputTextArea.clear();
        
        // Initialize live call flow for real-time visualization (Phase 1.3)
        liveMessages.clear();
        liveCallFlow = new CallFlow();
        logger.debug("Initialized live call flow for real-time visualization");
        
        // Create live diagram for SIP/IMS protocols (Phase 2.3)
        if (selectedDemo.getProtocol() == Demo.Protocol.SIP_IMS) {
            currentDiagram = new CallFlowDiagram(liveCallFlow);
            liveCallFlow.addListener(currentDiagram); // Register diagram as listener
            
            // Add diagram to UI immediately (will update in real-time)
            diagramContainer.getChildren().clear();
            diagramContainer.getChildren().add(currentDiagram);
            
            // Enable export button
            if (exportDiagramButton != null) {
                exportDiagramButton.setDisable(false);
            }
            
            callFlowStatusLabel.setText("Call Flow: Initializing...");
            logger.info("Created live call flow diagram, registered as listener");
        }
        
        // Switch to Execution tab and disable Configuration tab
        switchToExecutionTab();
        setConfigTabDisabled(true);
        
        logger.info("Starting demo run: {}", selectedDemo.getTitle());
        
        // Run demo in background thread with real-time message capture
        new Thread(() -> {
            RunResult result = demoRunner.runDemo(selectedDemo, currentConfig, this::appendOutput, this::handleLiveSipMessage);
            
            Platform.runLater(() -> {
                runButton.setDisable(false);
                stopButton.setDisable(true);
                if (executionTabStopButton != null) {
                    executionTabStopButton.setDisable(true);
                }
                progressIndicator.setVisible(false);
                
                if (result.getStatus() == RunResult.RunStatus.SUCCESS) {
                    statusLabel.setText("Completed Successfully");
                    statusLabel.getStyleClass().clear();
                    statusLabel.getStyleClass().add("status-success");
                    
                    // For SIP/IMS demos, keep the live diagram and validate against JTL
                    if (selectedDemo.getProtocol() == Demo.Protocol.SIP_IMS) {
                        // Use the live call flow that was built dynamically during execution
                        if (liveCallFlow != null && liveCallFlow.getTotalMessages() > 0) {
                            // Keep the existing live diagram (already displayed and updating)
                            updateCallFlowStatus(liveCallFlow);
                            exportDiagramButton.setDisable(false);
                            logger.info("Live call flow diagram retained: {} messages captured in real-time", 
                                liveCallFlow.getTotalMessages());
                            
                            // Validate against JTL for accuracy (optional verification)
                            try {
                                String jtlPath = result.getLogFilePath();
                                if (jtlPath != null && new File(jtlPath).exists()) {
                                    CallFlow jtlFlow = jtlParser.parseJtlFile(jtlPath);
                                    if (jtlFlow.getTotalMessages() != liveCallFlow.getTotalMessages()) {
                                        logger.warn("Live capture message count ({}) differs from JTL count ({}). " +
                                            "This may indicate missed messages in real-time parsing.",
                                            liveCallFlow.getTotalMessages(), jtlFlow.getTotalMessages());
                                    } else {
                                        logger.debug("Live capture validated: {} messages match JTL count", 
                                            liveCallFlow.getTotalMessages());
                                    }
                                }
                            } catch (IOException e) {
                                logger.warn("Could not validate live capture against JTL: {}", e.getMessage());
                            }
                        } else {
                            // Fallback: parse JTL if live capture failed or is empty
                            logger.warn("Live call flow is empty, falling back to JTL parsing");
                            try {
                                String jtlPath = result.getLogFilePath();
                                if (jtlPath != null && new File(jtlPath).exists()) {
                                    CallFlow callFlow = jtlParser.parseJtlFile(jtlPath);
                                    
                                    // Check if call flow has messages
                                    if (callFlow.getTotalMessages() == 0) {
                                        showEmptyCallFlowMessage();
                                        logger.warn("No SIP messages found in JTL file: {}", jtlPath);
                                    } else {
                                        createCallFlowDiagram(callFlow);
                                        updateCallFlowStatus(callFlow);
                                        exportDiagramButton.setDisable(false);
                                        logger.info("Call flow diagram created from JTL fallback: {} messages", 
                                            callFlow.getTotalMessages());
                                    }
                                } else {
                                    logger.warn("JTL file not found: {}", jtlPath);
                                    showJtlNotFoundMessage();
                                }
                            } catch (IOException e) {
                                logger.error("Failed to parse JTL file", e);
                                callFlowStatusLabel.setText("Call Flow: Parse error");
                                showParseErrorMessage(e.getMessage());
                            }
                        }
                    } else {
                        // For non-SIP protocols, show message
                        showNonSipMessage();
                    }
                    
                    showAlert("Demo Completed", "Demo executed successfully in " + 
                             result.getDurationSeconds() + " seconds.", Alert.AlertType.INFORMATION);
                    
                    // Re-enable Configuration tab
                    setConfigTabDisabled(false);
                } else {
                    statusLabel.setText("Failed");
                    statusLabel.getStyleClass().clear();
                    statusLabel.getStyleClass().add("status-failed");
                    
                    // Show error message in diagram area for SIP demos
                    if (selectedDemo.getProtocol() == Demo.Protocol.SIP_IMS) {
                        showFailedTestMessage();
                    }
                    
                    showAlert("Demo Failed", "Demo execution failed. Check output for details.", 
                             Alert.AlertType.ERROR);
                    
                    // Re-enable Configuration tab
                    setConfigTabDisabled(false);
                }
                
                updateHistoryCount();
                logger.info("Demo run completed: {} - {}", selectedDemo.getTitle(), result.getStatus());
            });
        }).start();
    }

    @FXML
    private void handleStopDemo() {
        demoRunner.stopCurrentDemo();
        statusLabel.setText("Stopped");
        statusLabel.getStyleClass().clear();
        statusLabel.getStyleClass().add("status-failed");
        runButton.setDisable(false);
        stopButton.setDisable(true);
        if (executionTabStopButton != null) {
            executionTabStopButton.setDisable(true);
        }
        progressIndicator.setVisible(false);
        
        // Re-enable Configuration tab
        setConfigTabDisabled(false);
        
        logger.info("Demo execution stopped by user");
    }

    private void appendOutput(String line) {
        Platform.runLater(() -> {
            outputTextArea.appendText(line + "\n");
        });
    }
    
    /**
     * Handle real-time SIP message capture for live call flow visualization (Phase 1.3).
     * This callback is invoked from the background thread streaming JMeter output.
     * Messages are added to the live call flow for real-time diagram updates.
     * 
     * @param message Parsed SIP message from JMeter output
     */
    private void handleLiveSipMessage(SipMessage message) {
        if (message == null || liveCallFlow == null) {
            return;
        }
        
        // Thread-safe: add message to synchronized list
        liveMessages.add(message);
        
        // Thread-safe: add message to live call flow (calls analyze() internally)
        synchronized (liveCallFlow) {
            liveCallFlow.addMessage(message);
        }
        
        logger.debug("Live SIP message captured: {} {} (total: {})", 
                message.getDirection().getDisplayName(), 
                message.getMessageType().getDisplayName(),
                liveMessages.size());
        
        // Update call flow status label (Phase 2.3)
        Platform.runLater(() -> {
            if (callFlowStatusLabel != null) {
                callFlowStatusLabel.setText(String.format("Call Flow: %d messages", liveMessages.size()));
            }
        });
    }
    
    /**
     * Create and display call flow diagram from parsed data
     */
    private void createCallFlowDiagram(CallFlow callFlow) {
        currentDiagram = new CallFlowDiagram(callFlow);
        diagramContainer.getChildren().clear();
        diagramContainer.getChildren().add(currentDiagram);
        logger.info("Call flow diagram added to UI");
    }
    
    /**
     * Update call flow status label with statistics
     */
    private void updateCallFlowStatus(CallFlow callFlow) {
        String status = String.format("Call Flow: %d messages (%d successful, %.1f%%)",
                callFlow.getTotalMessages(),
                callFlow.getSuccessfulMessages(),
                callFlow.getSuccessRate());
        
        callFlowStatusLabel.setText(status);
        
        // Change label style based on success rate
        callFlowStatusLabel.getStyleClass().clear();
        if (callFlow.getSuccessRate() >= 100.0) {
            callFlowStatusLabel.getStyleClass().add("status-success");
        } else if (callFlow.getSuccessRate() >= 90.0) {
            callFlowStatusLabel.getStyleClass().add("status-warning");
        } else {
            callFlowStatusLabel.getStyleClass().add("status-failed");
        }
    }
    
    /**
     * Show message for non-SIP protocols
     */
    private void showNonSipMessage() {
        diagramContainer.getChildren().clear();
        Label message = new Label("Call flow visualization is only available for SIP/IMS demos.\n" +
                                 "For other protocols, use the terminal output below.");
        message.setStyle("-fx-text-fill: #95a5a6; -fx-font-size: 14px; -fx-text-alignment: center;");
        message.setWrapText(true);
        message.setMaxWidth(600);
        diagramContainer.getChildren().add(message);
        callFlowStatusLabel.setText("Call Flow: Not available for this protocol");
        exportDiagramButton.setDisable(true);
    }
    
    /**
     * Show message when no SIP messages found
     */
    private void showEmptyCallFlowMessage() {
        diagramContainer.getChildren().clear();
        Label message = new Label("No SIP messages were exchanged during this test.\n" +
                                 "This may indicate a configuration issue or test failure.\n" +
                                 "Check the terminal output for details.");
        message.setStyle("-fx-text-fill: #e67e22; -fx-font-size: 14px; -fx-text-alignment: center;");
        message.setWrapText(true);
        message.setMaxWidth(600);
        diagramContainer.getChildren().add(message);
        callFlowStatusLabel.setText("Call Flow: No messages");
        callFlowStatusLabel.getStyleClass().clear();
        callFlowStatusLabel.getStyleClass().add("status-warning");
        exportDiagramButton.setDisable(true);
    }
    
    /**
     * Show message when JTL file not found
     */
    private void showJtlNotFoundMessage() {
        diagramContainer.getChildren().clear();
        Label message = new Label("Test results file (JTL) not found.\n" +
                                 "The call flow cannot be visualized.");
        message.setStyle("-fx-text-fill: #e74c3c; -fx-font-size: 14px; -fx-text-alignment: center;");
        message.setWrapText(true);
        message.setMaxWidth(600);
        diagramContainer.getChildren().add(message);
        callFlowStatusLabel.setText("Call Flow: Results not found");
        callFlowStatusLabel.getStyleClass().clear();
        callFlowStatusLabel.getStyleClass().add("status-failed");
        exportDiagramButton.setDisable(true);
    }
    
    /**
     * Show message when JTL parse fails
     */
    private void showParseErrorMessage(String errorDetail) {
        diagramContainer.getChildren().clear();
        VBox errorBox = new VBox(10);
        errorBox.setAlignment(Pos.CENTER);
        errorBox.setMaxWidth(600);
        
        Label title = new Label("Failed to parse test results");
        title.setStyle("-fx-text-fill: #e74c3c; -fx-font-size: 16px; -fx-font-weight: bold;");
        
        Label detail = new Label(errorDetail);
        detail.setStyle("-fx-text-fill: #95a5a6; -fx-font-size: 12px;");
        detail.setWrapText(true);
        
        errorBox.getChildren().addAll(title, detail);
        diagramContainer.getChildren().add(errorBox);
        exportDiagramButton.setDisable(true);
    }
    
    /**
     * Show message when test fails
     */
    private void showFailedTestMessage() {
        diagramContainer.getChildren().clear();
        Label message = new Label("Test execution failed.\n" +
                                 "No call flow diagram available.\n" +
                                 "Check the terminal output for error details.");
        message.setStyle("-fx-text-fill: #e74c3c; -fx-font-size: 14px; -fx-text-alignment: center;");
        message.setWrapText(true);
        message.setMaxWidth(600);
        diagramContainer.getChildren().add(message);
        callFlowStatusLabel.setText("Call Flow: Test failed");
        callFlowStatusLabel.getStyleClass().clear();
        callFlowStatusLabel.getStyleClass().add("status-failed");
        exportDiagramButton.setDisable(true);
    }
    
    /**
     * Handle toggle terminal checkbox
     */
    @FXML
    private void handleToggleTerminal() {
        boolean show = showTerminalCheckBox.isSelected();
        terminalPane.setExpanded(show);
        
        if (!show) {
            // Hide terminal completely - show only diagram
            visualizationSplitPane.setDividerPositions(1.0);
        } else {
            // Show both - 70/30 split
            visualizationSplitPane.setDividerPositions(0.7);
        }
        
        logger.debug("Terminal visibility toggled: {}", show);
    }
    
    /**
     * Handle export diagram button
     */
    @FXML
    private void handleExportDiagram() {
        if (currentDiagram == null) {
            showAlert("Export Failed", "No diagram to export", Alert.AlertType.WARNING);
            return;
        }
        
        try {
            // Create exports directory if it doesn't exist
            File exportsDir = new File("exports");
            if (!exportsDir.exists()) {
                exportsDir.mkdirs();
            }
            
            // Generate filename with timestamp
            String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
            String filename = String.format("%s_callflow_%s.png", 
                    selectedDemo.getId(), timestamp);
            File outputFile = new File(exportsDir, filename);
            
            // Take snapshot of diagram
            WritableImage image = currentDiagram.snapshot(new SnapshotParameters(), null);
            
            // Write to file
            ImageIO.write(SwingFXUtils.fromFXImage(image, null), "png", outputFile);
            
            showAlert("Export Successful", 
                     "Diagram exported to: " + outputFile.getPath(), 
                     Alert.AlertType.INFORMATION);
            
            logger.info("Diagram exported to: {}", outputFile.getPath());
            
        } catch (IOException e) {
            logger.error("Failed to export diagram", e);
            showAlert("Export Failed", 
                     "Failed to export diagram: " + e.getMessage(), 
                     Alert.AlertType.ERROR);
        }
    }

    @FXML
    private void handleRefreshCatalog() {
        catalog = new DemoCatalog();
        refreshDemoList();
        logger.info("Catalog refreshed");
    }

    @FXML
    private void handleShowRunHistory() {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/run-history.fxml"));
            Parent root = loader.load();
            
            RunHistoryController controller = loader.getController();
            controller.setConfigManager(configManager);
            
            Stage stage = new Stage();
            stage.setTitle("Run History");
            stage.setScene(new Scene(root));
            stage.initModality(Modality.APPLICATION_MODAL);
            stage.show();
            
            stage.setOnHidden(e -> updateHistoryCount());
        } catch (IOException e) {
            logger.error("Failed to open run history window", e);
            showAlert("Error", "Failed to open run history window.", Alert.AlertType.ERROR);
        }
    }

    @FXML
    private void handleClearHistory() {
        Alert confirm = new Alert(Alert.AlertType.CONFIRMATION);
        confirm.setTitle("Clear History");
        confirm.setHeaderText("Clear all run history?");
        confirm.setContentText("This action cannot be undone.");
        
        confirm.showAndWait().ifPresent(response -> {
            if (response == ButtonType.OK) {
                int cleared = configManager.clearRunHistory();
                updateHistoryCount();
                showAlert("History Cleared", "Cleared " + cleared + " run records.", 
                         Alert.AlertType.INFORMATION);
                logger.info("Cleared {} run records", cleared);
            }
        });
    }

    @FXML
    private void handleValidateTTS() {
        validateTTSInstallation();
    }

    private void validateTTSInstallation() {
        boolean valid = demoRunner.validateJMeterInstallation();
        if (valid) {
            ttsStatusLabel.setText("TTS: Ready");
            ttsStatusLabel.setStyle("-fx-text-fill: #27ae60; -fx-font-weight: bold;");
        } else {
            ttsStatusLabel.setText("TTS: Not Found");
            ttsStatusLabel.setStyle("-fx-text-fill: #e74c3c; -fx-font-weight: bold;");
        }
    }

    private void updateHistoryCount() {
        int count = configManager.loadRunHistory().size();
        historyCountLabel.setText("History: " + count + " run" + (count != 1 ? "s" : ""));
    }

    @FXML
    private void handleAbout() {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("About TTS Demo Tool");
        alert.setHeaderText("TTS Demo Tool v1.0.0");
        alert.setContentText("Computaris TTS Demo Tool\n\n" +
                           "A JavaFX desktop application for demonstrating TTS capabilities.\n\n" +
                           "Supports SIP/IMS, Diameter, and RADIUS protocols.");
        alert.showAndWait();
    }

    @FXML
    private void handleExit() {
        Platform.exit();
    }

    // Helper methods
    
    private String getProtocolStyleClass(Demo.Protocol protocol) {
        switch (protocol) {
            case SIP_IMS: return "protocol-sip";
            case DIAMETER: return "protocol-diameter";
            case RADIUS: return "protocol-radius";
            default: return "";
        }
    }

    private String getComplexityStyleClass(Demo.Complexity complexity) {
        switch (complexity) {
            case BASIC: return "complexity-basic";
            case INTERMEDIATE: return "complexity-intermediate";
            case ADVANCED: return "complexity-advanced";
            default: return "";
        }
    }

    private Demo.Protocol findProtocolByDisplayName(String displayName) {
        for (Demo.Protocol protocol : Demo.Protocol.values()) {
            if (protocol.getDisplayName().equals(displayName)) {
                return protocol;
            }
        }
        return null;
    }

    private Demo.Complexity findComplexityByDisplayName(String displayName) {
        for (Demo.Complexity complexity : Demo.Complexity.values()) {
            if (complexity.getDisplayName().equals(displayName)) {
                return complexity;
            }
        }
        return null;
    }

    private String truncateText(String text, int maxLength) {
        if (text.length() <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength) + "...";
    }

    private void showAlert(String title, String content, Alert.AlertType type) {
        Alert alert = new Alert(type);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(content);
        alert.showAndWait();
    }
}
