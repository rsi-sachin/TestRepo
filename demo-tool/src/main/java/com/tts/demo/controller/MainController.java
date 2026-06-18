package com.tts.demo.controller;

import com.tts.demo.component.CallFlowDiagram;
import com.tts.demo.component.NetworkArchitecturePanel;
import com.tts.demo.model.ActorType;
import com.tts.demo.model.CallFlow;
import com.tts.demo.model.Demo;
import com.tts.demo.model.DemoConfig;
import com.tts.demo.model.RcaResult;
import com.tts.demo.model.RunResult;
import com.tts.demo.model.SipMessage;
import com.tts.demo.service.ConfigManager;
import com.tts.demo.service.DemoCatalog;
import com.tts.demo.service.DemoRunner;
import com.tts.demo.service.JtlParser;
import com.tts.demo.service.RcaAnalyzer;
import javafx.application.Platform;
import javafx.embed.swing.SwingFXUtils;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Node;
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
    @FXML private Tab architectureTab;
    @FXML private Tab trafficGeneratorTab;
    @FXML private Button executionTabStopButton;
    
    // Call Flow Visualization components (Phase 4+5)
    @FXML private CheckBox showTerminalCheckBox;
    @FXML private Button exportDiagramButton;
    @FXML private Label callFlowStatusLabel;
    @FXML private SplitPane visualizationSplitPane;
    @FXML private StackPane diagramContainer;
    @FXML private TitledPane terminalPane;
    
    // Architecture Tab components (Phase 3)
    @FXML private VBox architectureContainer;
    
    @FXML private Label ttsStatusLabel;
    @FXML private Label historyCountLabel;
    
    private DemoCatalog catalog;
    private ConfigManager configManager;
    private DemoRunner demoRunner;
    private JtlParser jtlParser;
    private RcaAnalyzer rcaAnalyzer;
    
    private Demo selectedDemo;
    private DemoConfig currentConfig;
    private Map<String, TextField> parameterFields;
    private CallFlowDiagram currentDiagram;
    private NetworkArchitecturePanel architecturePanel;  // Phase 3
    private TrafficGeneratorController trafficGeneratorController;  // Phase 2
    
    // Real-time call flow visualization fields (Phase 1.3)
    private final List<SipMessage> liveMessages = Collections.synchronizedList(new ArrayList<>());
    private volatile CallFlow liveCallFlow = null;
    
    // Real-time architecture panel updates (Phase 3.1)
    private final Set<ActorType> liveActiveActors = Collections.synchronizedSet(new LinkedHashSet<>());
    private volatile long lastArchitectureUpdateTime = 0;
    private volatile boolean architectureUpdatePending = false;

    @FXML
    public void initialize() {
        logger.info("Initializing MainController");
        
        // Initialize services
        catalog = new DemoCatalog();
        configManager = new ConfigManager();
        demoRunner = new DemoRunner(configManager);
        jtlParser = new JtlParser();
        rcaAnalyzer = new RcaAnalyzer();
        
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
        
        // Initialize architecture panel (Phase 3)
        initializeArchitecturePanel();
        
        // Initialize traffic generator controller (Phase 2)
        initializeTrafficGeneratorController();
        
        logger.info("MainController initialized with {} demos", catalog.getDemoCount());
    }
    
    /**
     * Initialize the 3GPP architecture reference panel (Phase 3)
     */
    private void initializeArchitecturePanel() {
        if (architectureContainer != null) {
            architecturePanel = new NetworkArchitecturePanel();
            architectureContainer.getChildren().clear();
            architectureContainer.getChildren().add(architecturePanel);
            logger.debug("Architecture panel initialized");
        }
    }
    
    /**
     * Initialize the Traffic Generator controller (Phase 2)
     */
    private void initializeTrafficGeneratorController() {
        if (trafficGeneratorTab != null) {
            try {
                // Load the FXML for traffic generator
                FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/traffic-generator.fxml"));
                javafx.scene.Parent content = loader.load();
                
                // Get the controller
                trafficGeneratorController = loader.getController();
                
                // Set the content
                trafficGeneratorTab.setContent(content);
                
                // Initialize services
                if (trafficGeneratorController != null) {
                    trafficGeneratorController.setServices(demoRunner, configManager);
                    logger.debug("Traffic generator controller initialized");
                } else {
                    logger.warn("Traffic generator controller is null after loading FXML");
                }
            } catch (Exception e) {
                logger.error("Failed to initialize traffic generator controller", e);
            }
        }
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
        badges.setAlignment(javafx.geometry.Pos.CENTER_LEFT);
        
        Label protocolLabel = new Label(demo.getProtocol().getDisplayName());
        protocolLabel.getStyleClass().addAll("protocol-badge", getProtocolStyleClass(demo.getProtocol()));
        protocolLabel.setWrapText(false);
        protocolLabel.setMaxHeight(Double.MAX_VALUE);
        
        Label complexityLabel = new Label(demo.getComplexity().getDisplayName());
        complexityLabel.getStyleClass().addAll("complexity-badge", getComplexityStyleClass(demo.getComplexity()));
        complexityLabel.setWrapText(false);
        complexityLabel.setMaxHeight(Double.MAX_VALUE);
        
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
        
        // Notify traffic generator controller (Phase 2)
        if (trafficGeneratorController != null) {
            trafficGeneratorController.setSelectedDemo(demo);
        }
        
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
        
        // Clear real-time actor tracking (Phase 3.1)
        synchronized (liveActiveActors) {
            liveActiveActors.clear();
        }
        lastArchitectureUpdateTime = 0;
        architectureUpdatePending = false;
        logger.info("[REALTIME] Cleared architecture panel actor tracking");
        
        // Reset split pane structure (remove any previous RCA panels)
        resetVisualizationPane();
        
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
            
            // Initialize architecture panel with empty actors (Phase 3)
            updateArchitecturePanelForDemo();
            
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
                    
                    // RCA: Check for failures in call flow even when test "succeeds" (Phase RCA)
                    // Many JMeter tests return exit code 0 even with error responses or error scenarios
                    if (selectedDemo.getProtocol() == Demo.Protocol.SIP_IMS && liveCallFlow != null && liveCallFlow.getTotalMessages() > 0) {
                        logger.info("Checking for failures in call flow (test status: SUCCESS, messages: {})", liveCallFlow.getTotalMessages());
                        
                        // Check if there are error responses OR error-related labels in the call flow
                        boolean hasErrors = liveCallFlow.getMessages().stream()
                            .anyMatch(msg -> {
                                String code = msg.getResponseCode();
                                String label = msg.getLabel();
                                
                                // Check for error response codes
                                boolean hasErrorCode = code != null && (code.startsWith("4") || code.startsWith("5") || code.startsWith("6"));
                                
                                // Check for error-related labels (for Error Scenario tests)
                                boolean hasErrorLabel = label != null && (
                                    label.toUpperCase().contains("ERROR") ||
                                    label.contains("error scenario") ||
                                    label.contains("REJECT") ||
                                    label.contains("FAIL")
                                );
                                
                                return hasErrorCode || hasErrorLabel;
                            });
                        
                        // Also check if this is explicitly an RCA demo or error scenario demo
                        boolean isRcaDemo = selectedDemo.getId().contains("rca") || 
                                          selectedDemo.getTitle().toLowerCase().contains("failure") ||
                                          selectedDemo.getTitle().toLowerCase().contains("error");
                        
                        if (hasErrors || isRcaDemo) {
                            logger.info("Found error indicators in call flow (errors={}, rcaDemo={}), triggering RCA analysis", hasErrors, isRcaDemo);
                            try {
                                RcaResult rcaResult = rcaAnalyzer.analyze(result, liveCallFlow);
                                logger.info("RCA result: hasFailure={}, summary={}", rcaResult.hasFailure(), rcaResult.getSummary());
                                
                                // Display RCA results
                                if (rcaResult.hasFailure()) {
                                    displayRcaResults(rcaResult);
                                    
                                    // Highlight failed message in diagram
                                    if (currentDiagram != null && rcaResult.getFailureMessageIndex() >= 0) {
                                        currentDiagram.setFailureHighlight(
                                            rcaResult.getFailureMessageIndex(),
                                            rcaResult.getRootCause()
                                        );
                                        logger.info("Highlighted failure at message index {}", rcaResult.getFailureMessageIndex());
                                    }
                                }
                            } catch (Exception e) {
                                logger.error("RCA analysis failed", e);
                            }
                        }
                    }
                } else {
                    statusLabel.setText("Failed");
                    statusLabel.getStyleClass().clear();
                    statusLabel.getStyleClass().add("status-failed");
                    
                    // RCA: Analyze failure for SIP demos
                    logger.info("Test failed. Protocol: {}, CallFlow: {}, Messages: {}", 
                        selectedDemo.getProtocol(), 
                        liveCallFlow != null ? "present" : "null",
                        liveCallFlow != null ? liveCallFlow.getTotalMessages() : 0);
                    
                    if (selectedDemo.getProtocol() == Demo.Protocol.SIP_IMS && liveCallFlow != null && liveCallFlow.getTotalMessages() > 0) {
                        logger.info("Triggering RCA analysis for failed test");
                        try {
                            RcaResult rcaResult = rcaAnalyzer.analyze(result, liveCallFlow);
                            logger.info("RCA result: hasFailure={}, summary={}", rcaResult.hasFailure(), rcaResult.getSummary());
                            
                            // Display RCA results
                            displayRcaResults(rcaResult);
                            
                            // Highlight failed message in diagram
                            if (currentDiagram != null && rcaResult.getFailureMessageIndex() >= 0) {
                                currentDiagram.setFailureHighlight(
                                    rcaResult.getFailureMessageIndex(),
                                    rcaResult.getRootCause()
                                );
                                logger.info("Highlighted failure at message index {}", rcaResult.getFailureMessageIndex());
                            }
                            
                            logger.info("RCA analysis complete: {}", rcaResult.getSummary());
                        } catch (Exception e) {
                            logger.error("RCA analysis failed", e);
                        }
                    } else {
                        logger.warn("RCA not triggered - conditions not met");
                    }
                    
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
        
        // Real-time actor extraction for architecture panel (Phase 3.1)
        if (selectedDemo != null && selectedDemo.getProtocol() == Demo.Protocol.SIP_IMS) {
            boolean actorAdded = false;
            List<ActorType> newActors = new ArrayList<>();
            
            if (message.getSourceActor() != null && message.getSourceActor() != ActorType.UNKNOWN) {
                synchronized (liveActiveActors) {
                    if (liveActiveActors.add(message.getSourceActor())) {
                        actorAdded = true;
                        newActors.add(message.getSourceActor());
                    }
                }
            }
            
            if (message.getTargetActor() != null && message.getTargetActor() != ActorType.UNKNOWN) {
                synchronized (liveActiveActors) {
                    if (liveActiveActors.add(message.getTargetActor())) {
                        actorAdded = true;
                        newActors.add(message.getTargetActor());
                    }
                }
            }
            
            // Only trigger update if new actor detected
            if (actorAdded) {
                logger.info("[REALTIME] New actors detected: {} (total: {})", 
                    newActors.stream().map(ActorType::getDisplayName).collect(Collectors.joining(", ")),
                    liveActiveActors.size());
                scheduleArchitectureUpdate();
            }
        }
        
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
        
        // Update architecture panel with active actors (Phase 3)
        updateArchitecturePanelWithCallFlow(callFlow);
        
        logger.info("Call flow diagram added to UI");
    }
    
    /**
     * Update architecture panel with active actors from call flow (Phase 3)
     */
    private void updateArchitecturePanelWithCallFlow(CallFlow callFlow) {
        if (architecturePanel != null && callFlow != null) {
            // Extract unique actors from call flow messages
            Set<ActorType> uniqueActors = new LinkedHashSet<>();
            for (SipMessage message : callFlow.getMessages()) {
                if (message.getSourceActor() != null && message.getSourceActor() != ActorType.UNKNOWN) {
                    uniqueActors.add(message.getSourceActor());
                }
                if (message.getTargetActor() != null && message.getTargetActor() != ActorType.UNKNOWN) {
                    uniqueActors.add(message.getTargetActor());
                }
            }
            
            architecturePanel.setActiveActors(new ArrayList<>(uniqueActors));
            logger.debug("Updated architecture panel with {} active actors", uniqueActors.size());
        }
    }
    
    /**
     * Update architecture panel for the selected demo (Phase 3)
     */
    private void updateArchitecturePanelForDemo() {
        if (architecturePanel != null) {
            // Start with empty actors, will be updated as messages arrive
            architecturePanel.setActiveActors(new ArrayList<>());
            logger.debug("Initialized architecture panel for demo");
        }
    }
    
    /**
     * Schedule a throttled architecture panel update (Phase 3.1).
     * Updates at most once per 500ms to prevent UI flickering.
     */
    private void scheduleArchitectureUpdate() {
        long now = System.currentTimeMillis();
        
        // Throttle to max 1 update per 500ms (slower than diagram for less visual noise)
        if (now - lastArchitectureUpdateTime >= 500) {
            lastArchitectureUpdateTime = now;
            architectureUpdatePending = false;
            logger.info("[REALTIME] Updating architecture panel immediately");
            updateArchitecturePanelRealTime();
        } else if (!architectureUpdatePending) {
            architectureUpdatePending = true;
            long delay = 500 - (now - lastArchitectureUpdateTime);
            logger.info("[REALTIME] Scheduling architecture update in {}ms", delay);
            
            new Thread(() -> {
                try {
                    Thread.sleep(delay);
                    lastArchitectureUpdateTime = System.currentTimeMillis();
                    architectureUpdatePending = false;
                    updateArchitecturePanelRealTime();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }).start();
        }
    }
    
    /**
     * Update architecture panel in real-time with currently detected actors (Phase 3.1).
     * Must be called on JavaFX Application Thread or via Platform.runLater().
     */
    private void updateArchitecturePanelRealTime() {
        Platform.runLater(() -> {
            if (architecturePanel != null && !liveActiveActors.isEmpty()) {
                synchronized (liveActiveActors) {
                    List<ActorType> actorList = new ArrayList<>(liveActiveActors);
                    architecturePanel.setActiveActors(actorList);
                    logger.info("[REALTIME] Architecture panel updated with {} actors: {}", 
                        actorList.size(),
                        actorList.stream().map(ActorType::getDisplayName).collect(Collectors.joining(", ")));
                }
            }
        });
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
        boolean valid = demoRunner.validateJMeterInstallation();
        
        // Update status bar
        if (valid) {
            ttsStatusLabel.setText("TTS: Ready");
            ttsStatusLabel.setStyle("-fx-text-fill: #27ae60; -fx-font-weight: bold;");
        } else {
            ttsStatusLabel.setText("TTS: Not Found");
            ttsStatusLabel.setStyle("-fx-text-fill: #e74c3c; -fx-font-weight: bold;");
        }
        
        // Show detailed validation result dialog
        Alert alert = new Alert(valid ? Alert.AlertType.INFORMATION : Alert.AlertType.WARNING);
        alert.setTitle("TTS Validation");
        alert.setHeaderText(valid ? "✓ TTS Installation Valid" : "✗ TTS Installation Not Found");
        
        if (valid) {
            alert.setContentText(
                "JMeter found at: C:\\TTS\\bin\\jmeter.bat\n\n" +
                "Status: Ready to run demos\n" +
                "All demo templates should be accessible\n\n" +
                "You can now execute SIP/IMS, Diameter, and RADIUS demos."
            );
        } else {
            alert.setContentText(
                "JMeter not found at: C:\\TTS\\bin\\jmeter.bat\n\n" +
                "Please install TTS before running demos.\n\n" +
                "Expected installation directory: C:\\TTS\\\n" +
                "Required file: C:\\TTS\\bin\\jmeter.bat\n\n" +
                "Demos will fail to execute until TTS is properly installed."
            );
        }
        
        alert.showAndWait();
        logger.info("TTS validation result shown to user: {}", valid ? "Valid" : "Not Found");
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
    
    /**
     * Reset visualization pane to original structure (remove any RCA panels)
     */
    private void resetVisualizationPane() {
        if (!Platform.isFxApplicationThread()) {
            Platform.runLater(this::resetVisualizationPane);
            return;
        }
        
        try {
            if (visualizationSplitPane == null || visualizationSplitPane.getItems().size() < 2) {
                logger.debug("Split pane not initialized or has fewer than 2 items");
                return;
            }
            
            // Get the right pane (index 1)
            Node rightItem = visualizationSplitPane.getItems().get(1);
            
            // If it's not the terminalPane directly, it might be wrapped in a VBox
            if (!(rightItem instanceof TitledPane)) {
                // Right item was replaced with container, restore original
                logger.info("Restoring original terminal pane structure");
                visualizationSplitPane.getItems().set(1, terminalPane);
            } else {
                logger.debug("Terminal pane already in correct position");
            }
        } catch (Exception e) {
            logger.error("Error resetting visualization pane", e);
        }
    }
    
    /**
     * Display Root Cause Analysis results below the terminal output (right pane)
     * IMPROVED: More robust split pane manipulation with proper error handling
     */
    private void displayRcaResults(RcaResult rca) {
        if (rca == null || !rca.hasFailure()) {
            logger.warn("Cannot display RCA: no failure detected or analysis incomplete (rca={}, hasFailure={})", 
                rca != null, rca != null ? rca.hasFailure() : "N/A");
            return;
        }
        
        logger.info("Creating RCA panel UI - Summary: {}", rca.getSummary());
        
        // Create RCA panel
        VBox rcaPanel = new VBox(15);
        rcaPanel.setPadding(new Insets(20));
        rcaPanel.setStyle("-fx-background-color: #fff3cd; -fx-border-color: #ffc107; -fx-border-width: 2px; -fx-border-radius: 5px; -fx-background-radius: 5px;");
        
        // Header
        Label headerLabel = new Label("⚠ Root Cause Analysis");
        headerLabel.setStyle("-fx-font-size: 18px; -fx-font-weight: bold; -fx-text-fill: #856404;");
        
        // Failure Summary
        Label summaryLabel = new Label(rca.getSummary());
        summaryLabel.setStyle("-fx-font-size: 14px; -fx-font-weight: bold; -fx-text-fill: #333;");
        summaryLabel.setWrapText(true);
        
        // Root Cause
        VBox rootCauseBox = new VBox(5);
        Label rootCauseTitle = new Label("Root Cause:");
        rootCauseTitle.setStyle("-fx-font-weight: bold; -fx-font-size: 13px;");
        TextArea rootCauseText = new TextArea(rca.getRootCause());
        rootCauseText.setWrapText(true);
        rootCauseText.setEditable(false);
        rootCauseText.setPrefRowCount(3);
        rootCauseText.setStyle("-fx-background-color: white; -fx-border-color: #ddd; -fx-border-width: 1px;");
        rootCauseBox.getChildren().addAll(rootCauseTitle, rootCauseText);
        
        // Affected Node
        if (rca.getAffectedNode() != null) {
            HBox nodeBox = new HBox(10);
            nodeBox.setAlignment(Pos.CENTER_LEFT);
            Label nodeLabel = new Label("Affected Node:");
            nodeLabel.setStyle("-fx-font-weight: bold;");
            Label nodeValue = new Label(rca.getAffectedNode());
            nodeValue.setStyle("-fx-font-size: 14px; -fx-text-fill: #d32f2f; -fx-font-weight: bold;");
            nodeBox.getChildren().addAll(nodeLabel, nodeValue);
            rcaPanel.getChildren().add(nodeBox);
        }
        
        // NEW: Failure Mechanism (HOW it failed)
        if (rca.getFailureMechanism() != null) {
            VBox mechanismBox = new VBox(5);
            mechanismBox.setStyle("-fx-background-color: #e8f5e9; -fx-padding: 10px; -fx-border-color: #4caf50; -fx-border-width: 1px; -fx-border-radius: 3px; -fx-background-radius: 3px;");
            
            Label mechanismTitle = new Label("📋 Failure Mechanism:");
            mechanismTitle.setStyle("-fx-font-weight: bold; -fx-font-size: 13px;");
            
            Label mechanismValue = new Label(rca.getFailureMechanism().getDisplayName());
            mechanismValue.setStyle("-fx-font-size: 13px; -fx-font-weight: bold; -fx-text-fill: #2e7d32;");
            
            Label mechanismExplanation = new Label(rca.getFailureMechanism().getExplanation());
            mechanismExplanation.setWrapText(true);
            mechanismExplanation.setStyle("-fx-font-size: 11px; -fx-text-fill: #555; -fx-font-style: italic;");
            
            mechanismBox.getChildren().addAll(mechanismTitle, mechanismValue, mechanismExplanation);
            rcaPanel.getChildren().add(mechanismBox);
        }
        
        // Evidence Section
        if (rca.getEvidence() != null && !rca.getEvidence().isEmpty()) {
            VBox evidenceBox = new VBox(5);
            Label evidenceTitle = new Label("Evidence:");
            evidenceTitle.setStyle("-fx-font-weight: bold; -fx-font-size: 13px;");
            VBox evidenceList = new VBox(3);
            for (String evidence : rca.getEvidence()) {
                Label bulletLabel = new Label("• " + evidence);
                bulletLabel.setWrapText(true);
                bulletLabel.setStyle("-fx-font-size: 12px;");
                evidenceList.getChildren().add(bulletLabel);
            }
            evidenceBox.getChildren().addAll(evidenceTitle, evidenceList);
            rcaPanel.getChildren().add(evidenceBox);
        }
        
        // Recommendations Section
        if (rca.getRecommendations() != null && !rca.getRecommendations().isEmpty()) {
            VBox recBox = new VBox(5);
            Label recTitle = new Label("Recommended Actions:");
            recTitle.setStyle("-fx-font-weight: bold; -fx-font-size: 13px;");
            VBox recList = new VBox(3);
            int num = 1;
            for (String recommendation : rca.getRecommendations()) {
                Label recLabel = new Label(num + ". " + recommendation);
                recLabel.setWrapText(true);
                recLabel.setStyle("-fx-font-size: 12px;");
                recList.getChildren().add(recLabel);
                num++;
            }
            recBox.getChildren().addAll(recTitle, recList);
            rcaPanel.getChildren().add(recBox);
        }
        
        // Add all components to RCA panel
        rcaPanel.getChildren().addAll(0, List.of(headerLabel, summaryLabel, rootCauseBox));
        
        // Wrap in TitledPane for collapsibility
        TitledPane rcaTitledPane = new TitledPane();
        rcaTitledPane.setText("🔍 Root Cause Analysis");
        rcaTitledPane.setContent(rcaPanel);
        rcaTitledPane.setExpanded(true);
        rcaTitledPane.setCollapsible(true);
        rcaTitledPane.setMaxHeight(Double.MAX_VALUE);
        
        // Add RCA panel to right pane below terminal - IMPROVED APPROACH
        if (!Platform.isFxApplicationThread()) {
            Platform.runLater(() -> addRcaPanelToUI(rcaTitledPane));
        } else {
            addRcaPanelToUI(rcaTitledPane);
        }
    }
    
    /**
     * Add RCA panel to UI - separated method for better error handling and debugging
     */
    private void addRcaPanelToUI(TitledPane rcaTitledPane) {
        try {
            logger.info("Adding RCA panel to UI (split pane items: {}, terminalPane parent: {})", 
                visualizationSplitPane.getItems().size(),
                terminalPane.getParent() != null ? terminalPane.getParent().getClass().getSimpleName() : "null");
            
            // Verify split pane structure
            if (visualizationSplitPane == null) {
                logger.error("visualizationSplitPane is null!");
                return;
            }
            
            if (visualizationSplitPane.getItems().size() < 2) {
                logger.error("Split pane has only {} items, expected at least 2", 
                    visualizationSplitPane.getItems().size());
                return;
            }
            
            Node currentRightItem = visualizationSplitPane.getItems().get(1);
            logger.info("Current right pane type: {}", currentRightItem.getClass().getSimpleName());
            
            // Create container for terminal + RCA
            VBox rightPaneContainer = new VBox(10);
            rightPaneContainer.setPadding(new Insets(0));
            rightPaneContainer.setMaxHeight(Double.MAX_VALUE);
            
            // Remove terminal from current parent if it's already in a container
            if (terminalPane.getParent() != null && terminalPane.getParent() != visualizationSplitPane) {
                ((Pane) terminalPane.getParent()).getChildren().remove(terminalPane);
                logger.debug("Removed terminalPane from previous parent");
            }
            
            // Set growth properties for proper resizing
            VBox.setVgrow(terminalPane, Priority.ALWAYS);
            VBox.setVgrow(rcaTitledPane, Priority.ALWAYS);
            
            // Add terminal and RCA to container
            rightPaneContainer.getChildren().addAll(terminalPane, rcaTitledPane);
            
            // Replace the right item in split pane
            visualizationSplitPane.getItems().set(1, rightPaneContainer);
            
            logger.info("✓ RCA panel successfully added to UI (container children: {})", 
                rightPaneContainer.getChildren().size());
            
            // Force layout update
            visualizationSplitPane.layout();
            rightPaneContainer.layout();
            
        } catch (Exception e) {
            logger.error("Failed to add RCA panel to UI", e);
            logger.error("  Split pane items: {}", visualizationSplitPane != null ? 
                visualizationSplitPane.getItems().size() : "NULL");
            logger.error("  Terminal pane: {}", terminalPane != null ? 
                terminalPane.getClass().getSimpleName() : "NULL");
        }
    }

    private void showAlert(String title, String content, Alert.AlertType type) {
        Alert alert = new Alert(type);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(content);
        alert.showAndWait();
    }
}
