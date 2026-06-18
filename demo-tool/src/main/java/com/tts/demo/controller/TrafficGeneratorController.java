package com.tts.demo.controller;

import com.tts.demo.model.*;
import com.tts.demo.service.ConfigManager;
import com.tts.demo.service.DemoRunner;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.NumberAxis;
import javafx.scene.chart.XYChart;
import javafx.scene.control.*;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.VBox;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.text.DecimalFormat;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Controller for the Traffic Generator tab.
 * Manages traffic profile configuration, execution, and real-time statistics display.
 * 
 * Phase 2 Implementation - May 13, 2026
 */
public class TrafficGeneratorController {
    
    private static final Logger logger = LoggerFactory.getLogger(TrafficGeneratorController.class);
    private static final DecimalFormat DECIMAL_FORMAT = new DecimalFormat("#,##0");
    private static final DecimalFormat PERCENT_FORMAT = new DecimalFormat("0.0");
    private static final DateTimeFormatter TIME_FORMAT = DateTimeFormatter.ofPattern("HH:mm:ss");
    
    // Volume Controls
    @FXML private Slider concurrentCallsSlider;
    @FXML private Label concurrentCallsLabel;
    @FXML private TextField totalCallsField;
    @FXML private Spinner<Integer> rampUpSpinner;
    @FXML private Spinner<Integer> durationSpinner;
    
    // Failure Injection Controls
    @FXML private CheckBox enableFailureInjectionCheckBox;
    @FXML private VBox failureInjectionPanel;
    @FXML private Slider failureRateSlider;
    @FXML private Label failureRateLabel;
    @FXML private ComboBox<ActorType> failureNodeComboBox;
    @FXML private ComboBox<ConformanceScenario> scenarioComboBox;
    @FXML private Label scenarioDescriptionLabel;
    
    // Call Timing Controls
    @FXML private Spinner<Integer> callHoldTimeSpinner;
    @FXML private Spinner<Integer> interCallDelaySpinner;
    
    // Control Buttons
    @FXML private TextField profileNameField;
    @FXML private Button startButton;
    @FXML private Button stopButton;
    @FXML private Button exportButton;
    @FXML private Button resetButton;
    @FXML private ProgressIndicator progressIndicator;
    
    // Statistics Display
    @FXML private Label statusLabel;
    @FXML private Label totalAttemptsLabel;
    @FXML private Label successfulCallsLabel;
    @FXML private Label failedCallsLabel;
    @FXML private Label successRateLabel;
    @FXML private Label avgResponseTimeLabel;
    @FXML private Label callsPerSecondLabel;
    @FXML private Label elapsedTimeLabel;
    
    @FXML private ProgressBar progressBar;
    @FXML private Label progressLabel;
    
    // Failure Breakdown
    @FXML private GridPane failureBreakdownGrid;
    
    // Throughput Chart
    @FXML private LineChart<Number, Number> throughputChart;
    @FXML private NumberAxis chartXAxis;
    @FXML private NumberAxis chartYAxis;
    
    // Services
    private DemoRunner demoRunner;
    private ConfigManager configManager;
    
    // State
    private Demo selectedDemo;
    private TrafficStats currentStats;
    private Map<ActorType, XYChart.Series<Number, Number>> nodeSeriesMap;  // Per-node chart series
    private volatile LocalDateTime startTime;
    private final AtomicBoolean isRunning = new AtomicBoolean(false);
    
    /**
     * Initialize the controller
     */
    @FXML
    public void initialize() {
        logger.info("Initializing TrafficGeneratorController");
        
        // Initialize volume controls
        initializeVolumeControls();
        
        // Initialize failure injection controls
        initializeFailureInjectionControls();
        
        // Initialize call timing controls
        initializeCallTimingControls();
        
        // Initialize buttons
        initializeButtons();
        
        // Initialize statistics display
        initializeStatisticsDisplay();
        
        // Initialize chart
        initializeChart();
        
        logger.info("TrafficGeneratorController initialized");
    }
    
    /**
     * Set the services (called by MainController)
     */
    public void setServices(DemoRunner demoRunner, ConfigManager configManager) {
        this.demoRunner = demoRunner;
        this.configManager = configManager;
        logger.debug("Services configured for TrafficGeneratorController");
    }
    
    /**
     * Set the selected demo (called by MainController)
     */
    public void setSelectedDemo(Demo demo) {
        this.selectedDemo = demo;
        logger.debug("Selected demo set: {}", demo != null ? demo.getId() : "null");
        updateControlsState();
    }
    
    /**
     * Initialize volume control sliders and spinners
     */
    private void initializeVolumeControls() {
        // Concurrent Calls Slider (1-500)
        concurrentCallsSlider.setMin(1);
        concurrentCallsSlider.setMax(500);
        concurrentCallsSlider.setValue(50);
        concurrentCallsSlider.setMajorTickUnit(50);
        concurrentCallsSlider.setShowTickLabels(true);
        concurrentCallsSlider.setShowTickMarks(true);
        concurrentCallsSlider.valueProperty().addListener((obs, oldVal, newVal) -> {
            concurrentCallsLabel.setText(String.valueOf(newVal.intValue()));
        });
        concurrentCallsLabel.setText("50");
        
        // Total Calls Field
        totalCallsField.setText("10000");
        totalCallsField.textProperty().addListener((obs, oldVal, newVal) -> {
            if (!newVal.matches("\\d*")) {
                totalCallsField.setText(oldVal);
            }
        });
        
        // Ramp-Up Spinner (0-300 seconds)
        SpinnerValueFactory<Integer> rampUpFactory = 
            new SpinnerValueFactory.IntegerSpinnerValueFactory(0, 300, 30, 5);
        rampUpSpinner.setValueFactory(rampUpFactory);
        rampUpSpinner.setEditable(true);
        
        // Duration Spinner (0-3600 seconds, 0 = until total calls reached)
        SpinnerValueFactory<Integer> durationFactory = 
            new SpinnerValueFactory.IntegerSpinnerValueFactory(0, 3600, 0, 60);
        durationSpinner.setValueFactory(durationFactory);
        durationSpinner.setEditable(true);
    }
    
    /**
     * Initialize failure injection controls
     */
    private void initializeFailureInjectionControls() {
        // Failure Injection Enable/Disable
        failureInjectionPanel.setDisable(true);
        enableFailureInjectionCheckBox.setSelected(false);
        enableFailureInjectionCheckBox.selectedProperty().addListener((obs, oldVal, newVal) -> {
            failureInjectionPanel.setDisable(!newVal);
        });
        
        // Failure Rate Slider (0-100%)
        failureRateSlider.setMin(0);
        failureRateSlider.setMax(100);
        failureRateSlider.setValue(15);
        failureRateSlider.setMajorTickUnit(10);
        failureRateSlider.setShowTickLabels(true);
        failureRateSlider.setShowTickMarks(true);
        failureRateSlider.valueProperty().addListener((obs, oldVal, newVal) -> {
            failureRateLabel.setText(PERCENT_FORMAT.format(newVal.doubleValue()) + "%");
        });
        failureRateLabel.setText("15.0%");
        
        // Failure Node ComboBox
        failureNodeComboBox.getItems().addAll(ActorType.values());
        failureNodeComboBox.getItems().remove(ActorType.UNKNOWN);
        failureNodeComboBox.setValue(ActorType.HSS);
        
        // Conformance Scenario ComboBox
        scenarioComboBox.getItems().addAll(ConformanceScenario.values());
        scenarioComboBox.setValue(ConformanceScenario.WRONG_CREDENTIALS);
        scenarioComboBox.valueProperty().addListener((obs, oldVal, newVal) -> {
            if (newVal != null) {
                scenarioDescriptionLabel.setText(newVal.getDescription());
                // Auto-select the affected node
                failureNodeComboBox.setValue(newVal.getAffectedNode());
            }
        });
        scenarioDescriptionLabel.setText(ConformanceScenario.WRONG_CREDENTIALS.getDescription());
    }
    
    /**
     * Initialize call timing controls
     */
    private void initializeCallTimingControls() {
        // Call Hold Time Spinner (1000-30000 ms)
        SpinnerValueFactory<Integer> holdTimeFactory = 
            new SpinnerValueFactory.IntegerSpinnerValueFactory(1000, 30000, 5000, 1000);
        callHoldTimeSpinner.setValueFactory(holdTimeFactory);
        callHoldTimeSpinner.setEditable(true);
        
        // Inter-Call Delay Spinner (0-5000 ms)
        SpinnerValueFactory<Integer> delayFactory = 
            new SpinnerValueFactory.IntegerSpinnerValueFactory(0, 5000, 100, 50);
        interCallDelaySpinner.setValueFactory(delayFactory);
        interCallDelaySpinner.setEditable(true);
    }
    
    /**
     * Initialize control buttons
     */
    private void initializeButtons() {
        startButton.setDisable(true);
        stopButton.setDisable(true);
        exportButton.setDisable(true);
        progressIndicator.setVisible(false);
        
        profileNameField.setText("Traffic Test " + TIME_FORMAT.format(LocalDateTime.now()));
    }
    
    /**
     * Initialize statistics display
     */
    private void initializeStatisticsDisplay() {
        resetStatisticsDisplay();
    }
    
    /**
     * Initialize throughput chart for per-node visualization
     */
    private void initializeChart() {
        chartXAxis.setLabel("Time (seconds)");
        chartYAxis.setLabel("Messages per Second");
        chartXAxis.setAutoRanging(true);
        chartYAxis.setAutoRanging(true);
        
        // Initialize node series map
        nodeSeriesMap = new HashMap<>();
        
        // Chart will be populated dynamically as nodes become active
        throughputChart.setCreateSymbols(false);
        throughputChart.setAnimated(false);
        throughputChart.setLegendVisible(true);
    }
    
    /**
     * Update controls state based on selected demo and running state
     */
    private void updateControlsState() {
        boolean hasDemo = selectedDemo != null;
        boolean running = isRunning.get();
        
        Platform.runLater(() -> {
            startButton.setDisable(!hasDemo || running);
            stopButton.setDisable(!running);
            exportButton.setDisable(currentStats == null || running);
            resetButton.setDisable(running);
            
            // Disable all input controls when running
            concurrentCallsSlider.setDisable(running);
            totalCallsField.setDisable(running);
            rampUpSpinner.setDisable(running);
            durationSpinner.setDisable(running);
            enableFailureInjectionCheckBox.setDisable(running);
            failureRateSlider.setDisable(running);
            failureNodeComboBox.setDisable(running);
            scenarioComboBox.setDisable(running);
            callHoldTimeSpinner.setDisable(running);
            interCallDelaySpinner.setDisable(running);
            profileNameField.setDisable(running);
        });
    }
    
    /**
     * Handle Start button click
     */
    @FXML
    private void handleStart() {
        if (selectedDemo == null) {
            showAlert("No Demo Selected", "Please select a demo from the catalog first.");
            return;
        }
        
        try {
            // Build traffic profile
            TrafficProfile profile = buildTrafficProfile();
            
            // Validate profile
            if (!profile.isValid()) {
                showAlert("Invalid Configuration", "Please check all traffic generation parameters.");
                return;
            }
            
            // Reset statistics
            resetStatisticsDisplay();
            clearChart();
            
            // Initialize stats
            String sessionId = "session-" + System.currentTimeMillis();
            currentStats = new TrafficStats(sessionId, profile);
            startTime = LocalDateTime.now();
            
            // Update UI state
            isRunning.set(true);
            updateControlsState();
            progressIndicator.setVisible(true);
            statusLabel.setText("RUNNING");
            statusLabel.setStyle("-fx-text-fill: #27ae60; -fx-font-weight: bold;");
            
            logger.info("Starting traffic generation: {}", profile.getProfileName());
            
            // Execute traffic generation in background thread
            new Thread(() -> {
                try {
                    demoRunner.executeTrafficGeneration(selectedDemo, profile, this::updateStatistics);
                    
                    // Update UI on completion
                    Platform.runLater(() -> {
                        isRunning.set(false);
                        updateControlsState();
                        progressIndicator.setVisible(false);
                        statusLabel.setText("COMPLETED");
                        statusLabel.setStyle("-fx-text-fill: #27ae60; -fx-font-weight: bold;");
                        logger.info("Traffic generation completed successfully");
                    });
                } catch (Exception e) {
                    logger.error("Traffic generation execution error", e);
                    Platform.runLater(() -> {
                        isRunning.set(false);
                        updateControlsState();
                        progressIndicator.setVisible(false);
                        statusLabel.setText("FAILED");
                        statusLabel.setStyle("-fx-text-fill: #e74c3c; -fx-font-weight: bold;");
                        showAlert("Error", "Traffic generation failed: " + e.getMessage());
                    });
                }
            }, "Traffic-Generation-Thread").start();
            
        } catch (Exception e) {
            logger.error("Error starting traffic generation", e);
            showAlert("Error", "Failed to start traffic generation: " + e.getMessage());
            isRunning.set(false);
            updateControlsState();
            progressIndicator.setVisible(false);
        }
    }
    
    /**
     * Handle Stop button click
     */
    @FXML
    private void handleStop() {
        logger.info("Stopping traffic generation");
        
        // Stop the traffic generation
        if (demoRunner != null) {
            demoRunner.stopTrafficGeneration();
        }
        
        isRunning.set(false);
        updateControlsState();
        progressIndicator.setVisible(false);
        statusLabel.setText("STOPPED");
        statusLabel.setStyle("-fx-text-fill: #e74c3c; -fx-font-weight: bold;");
    }
    
    /**
     * Handle Export button click
     */
    @FXML
    private void handleExport() {
        if (currentStats == null) {
            showAlert("No Data", "No traffic generation data available to export.");
            return;
        }
        
        // TODO Phase 5: Implement TrafficDataExporter
        showInfo("Export", "Data export will be implemented in Phase 5.\n\n" +
            currentStats.getSummaryReport());
    }
    
    /**
     * Handle Reset button click
     */
    @FXML
    private void handleReset() {
        resetStatisticsDisplay();
        clearChart();
        currentStats = null;
        statusLabel.setText("READY");
        statusLabel.setStyle("-fx-text-fill: #7f8c8d;");
        progressBar.setProgress(0);
        progressLabel.setText("0%");
        logger.debug("Traffic generator reset");
    }
    
    /**
     * Build TrafficProfile from UI controls
     */
    private TrafficProfile buildTrafficProfile() {
        TrafficProfile profile = new TrafficProfile();
        
        profile.setProfileName(profileNameField.getText());
        profile.setConcurrentCalls((int) concurrentCallsSlider.getValue());
        
        try {
            profile.setTotalCalls(Integer.parseInt(totalCallsField.getText()));
        } catch (NumberFormatException e) {
            profile.setTotalCalls(10000);
        }
        
        profile.setRampUpSeconds(rampUpSpinner.getValue());
        profile.setDurationSeconds(durationSpinner.getValue());
        profile.setCallHoldTimeMs(callHoldTimeSpinner.getValue());
        profile.setInterCallDelayMs(interCallDelaySpinner.getValue());
        
        if (enableFailureInjectionCheckBox.isSelected()) {
            profile.setFailureRate(failureRateSlider.getValue());
            profile.setFailureNode(failureNodeComboBox.getValue());
            profile.setFailureScenario(scenarioComboBox.getValue().getScenarioId());
            // Parse response code to determine FailureType
            String expectedResponse = scenarioComboBox.getValue().getExpectedResponse();
            profile.setFailureType(parseFailureType(expectedResponse));
        } else {
            profile.setFailureRate(0.0);
        }
        
        return profile;
    }
    
    /**
     * Update statistics display (called periodically during execution)
     */
    public void updateStatistics(TrafficStats stats) {
        if (stats == null) {
            return;
        }
        
        this.currentStats = stats;
        
        Platform.runLater(() -> {
            // Update counters
            totalAttemptsLabel.setText(DECIMAL_FORMAT.format(stats.getTotalAttempts()));
            successfulCallsLabel.setText(DECIMAL_FORMAT.format(stats.getSuccessfulCalls()));
            failedCallsLabel.setText(DECIMAL_FORMAT.format(stats.getFailedCalls()));
            
            // Update rates
            successRateLabel.setText(PERCENT_FORMAT.format(stats.getSuccessRate()) + "%");
            
            // Update performance metrics
            avgResponseTimeLabel.setText(DECIMAL_FORMAT.format(stats.getAverageResponseTime()) + " ms");
            callsPerSecondLabel.setText(PERCENT_FORMAT.format(stats.getCallsPerSecond()));
            
            // Update elapsed time
            if (startTime != null) {
                long seconds = java.time.Duration.between(startTime, LocalDateTime.now()).getSeconds();
                elapsedTimeLabel.setText(formatDuration(seconds));
            }
            
            // Update progress bar
            TrafficProfile profile = stats.getProfile();
            if (profile != null && profile.getTotalCalls() > 0) {
                double progress = (double) stats.getTotalAttempts() / profile.getTotalCalls();
                progressBar.setProgress(progress);
                progressLabel.setText(DECIMAL_FORMAT.format(progress * 100) + "%");
            }
            
            // Update failure breakdown
            updateFailureBreakdown(stats);
            
            // Update chart
            updateChart(stats);
        });
    }
    
    /**
     * Update failure breakdown grid
     */
    private void updateFailureBreakdown(TrafficStats stats) {
        failureBreakdownGrid.getChildren().clear();
        
        int row = 0;
        for (var entry : stats.getFailuresByType().entrySet()) {
            Label typeLabel = new Label(entry.getKey() + ":");
            Label countLabel = new Label(DECIMAL_FORMAT.format(entry.getValue()));
            countLabel.setStyle("-fx-font-weight: bold;");
            
            failureBreakdownGrid.add(typeLabel, 0, row);
            failureBreakdownGrid.add(countLabel, 1, row);
            row++;
        }
    }
    
    /**
     * Update chart with per-node messages per second
     */
    private void updateChart(TrafficStats stats) {
        if (startTime == null) {
            return;
        }
        
        long elapsedSeconds = java.time.Duration.between(startTime, LocalDateTime.now()).getSeconds();
        LocalDateTime currentTimestamp = LocalDateTime.now().withNano(0);
        
        // Get all active nodes
        Set<ActorType> activeNodes = stats.getActiveNodes();
        
        // Create series for new nodes
        for (ActorType node : activeNodes) {
            if (!nodeSeriesMap.containsKey(node)) {
                XYChart.Series<Number, Number> series = new XYChart.Series<>();
                series.setName(node.getDisplayName());
                nodeSeriesMap.put(node, series);
                throughputChart.getData().add(series);
                logger.debug("Created chart series for node: {}", node.getDisplayName());
            }
        }
        
        // Update each node's series with current messages/second
        for (ActorType node : activeNodes) {
            XYChart.Series<Number, Number> series = nodeSeriesMap.get(node);
            if (series != null) {
                int messagesPerSec = stats.getMessagesPerSecond(node, currentTimestamp);
                
                // Only add non-zero data points
                if (messagesPerSec > 0) {
                    series.getData().add(new XYChart.Data<>(elapsedSeconds, messagesPerSec));
                    
                    // Limit data points to last 60 seconds
                    if (series.getData().size() > 60) {
                        series.getData().remove(0);
                    }
                }
            }
        }
    }
    
    /**
     * Reset statistics display
     */
    private void resetStatisticsDisplay() {
        totalAttemptsLabel.setText("0");
        successfulCallsLabel.setText("0");
        failedCallsLabel.setText("0");
        successRateLabel.setText("0.0%");
        avgResponseTimeLabel.setText("0 ms");
        callsPerSecondLabel.setText("0.0");
        elapsedTimeLabel.setText("00:00:00");
        failureBreakdownGrid.getChildren().clear();
        progressBar.setProgress(0);
        progressLabel.setText("0%");
    }
    
    /**
     * Clear chart data
     */
    private void clearChart() {
        // Clear all node series
        if (nodeSeriesMap != null) {
            for (XYChart.Series<Number, Number> series : nodeSeriesMap.values()) {
                series.getData().clear();
            }
            nodeSeriesMap.clear();
        }
        throughputChart.getData().clear();
    }
    
    /**
     * Format duration in HH:MM:SS
     */
    private String formatDuration(long seconds) {
        long hours = seconds / 3600;
        long minutes = (seconds % 3600) / 60;
        long secs = seconds % 60;
        return String.format("%02d:%02d:%02d", hours, minutes, secs);
    }
    
    /**
     * Show alert dialog
     */
    private void showAlert(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.WARNING);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }
    
    /**
     * Show info dialog
     */
    private void showInfo(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }
    
    /**
     * Parse response code string to determine FailureType
     */
    private FailureType parseFailureType(String responseCode) {
        if (responseCode == null || responseCode.isEmpty()) {
            return FailureType.UNKNOWN;
        }
        
        // Extract status code (e.g., "400 Bad Request" -> "400")
        String code = responseCode.split(" ")[0];
        
        if (code.startsWith("4")) {
            return FailureType.REJECTION_4XX;
        } else if (code.startsWith("5")) {
            return FailureType.REJECTION_5XX;
        } else if (code.equals("408")) {
            return FailureType.TIMEOUT;
        } else if (code.equals("401") || code.equals("403")) {
            return FailureType.AUTHENTICATION_FAILURE;
        } else if (code.equals("488") || code.equals("480")) {
            return FailureType.RESOURCE_UNAVAILABLE;
        } else {
            return FailureType.UNKNOWN;
        }
    }
}
