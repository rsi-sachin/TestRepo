package com.tts.demo.controller;

import com.tts.demo.model.Demo;
import com.tts.demo.model.DemoConfig;
import com.tts.demo.model.RunResult;
import com.tts.demo.service.ConfigManager;
import com.tts.demo.service.DemoCatalog;
import com.tts.demo.service.DemoRunner;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.Modality;
import javafx.stage.Stage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
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
    
    @FXML private Label ttsStatusLabel;
    @FXML private Label historyCountLabel;
    
    private DemoCatalog catalog;
    private ConfigManager configManager;
    private DemoRunner demoRunner;
    
    private Demo selectedDemo;
    private DemoConfig currentConfig;
    private Map<String, TextField> parameterFields;

    @FXML
    public void initialize() {
        logger.info("Initializing MainController");
        
        // Initialize services
        catalog = new DemoCatalog();
        configManager = new ConfigManager();
        demoRunner = new DemoRunner(configManager);
        
        parameterFields = new HashMap<>();
        
        // Initialize filters
        initializeFilters();
        
        // Load initial demo list
        refreshDemoList();
        
        // Validate TTS installation
        validateTTSInstallation();
        
        // Update history count
        updateHistoryCount();
        
        logger.info("MainController initialized with {} demos", catalog.getDemoCount());
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
        progressIndicator.setVisible(true);
        statusLabel.setText("Running...");
        statusLabel.getStyleClass().clear();
        statusLabel.getStyleClass().add("status-running");
        outputTextArea.clear();
        
        logger.info("Starting demo run: {}", selectedDemo.getTitle());
        
        // Run demo in background thread
        new Thread(() -> {
            RunResult result = demoRunner.runDemo(selectedDemo, currentConfig, this::appendOutput);
            
            Platform.runLater(() -> {
                runButton.setDisable(false);
                stopButton.setDisable(true);
                progressIndicator.setVisible(false);
                
                if (result.getStatus() == RunResult.RunStatus.SUCCESS) {
                    statusLabel.setText("Completed Successfully");
                    statusLabel.getStyleClass().clear();
                    statusLabel.getStyleClass().add("status-success");
                    showAlert("Demo Completed", "Demo executed successfully in " + 
                             result.getDurationSeconds() + " seconds.", Alert.AlertType.INFORMATION);
                } else {
                    statusLabel.setText("Failed");
                    statusLabel.getStyleClass().clear();
                    statusLabel.getStyleClass().add("status-failed");
                    showAlert("Demo Failed", "Demo execution failed. Check output for details.", 
                             Alert.AlertType.ERROR);
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
        progressIndicator.setVisible(false);
        logger.info("Demo execution stopped by user");
    }

    private void appendOutput(String line) {
        Platform.runLater(() -> {
            outputTextArea.appendText(line + "\n");
        });
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
