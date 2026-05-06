package com.tts.demo.controller;

import com.tts.demo.model.RunResult;
import com.tts.demo.service.ConfigManager;
import javafx.beans.property.SimpleStringProperty;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;

/**
 * Controller for the Run History window.
 * Displays historical demo execution results and allows management.
 */
public class RunHistoryController {
    
    private static final Logger logger = LoggerFactory.getLogger(RunHistoryController.class);
    private static final DateTimeFormatter DATE_FORMATTER = 
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    
    @FXML private TableView<RunResult> historyTable;
    @FXML private TableColumn<RunResult, String> demoTitleColumn;
    @FXML private TableColumn<RunResult, String> startTimeColumn;
    @FXML private TableColumn<RunResult, String> durationColumn;
    @FXML private TableColumn<RunResult, String> statusColumn;
    @FXML private TableColumn<RunResult, String> exitCodeColumn;
    
    @FXML private Label statsLabel;
    @FXML private VBox detailsPane;
    @FXML private Label runIdLabel;
    @FXML private Label demoIdLabel;
    @FXML private Label logFileLabel;
    @FXML private TextArea outputSnapshotArea;
    
    private ConfigManager configManager;
    private ObservableList<RunResult> runResults;

    public void setConfigManager(ConfigManager configManager) {
        this.configManager = configManager;
        initialize();
    }

    private void initialize() {
        logger.info("Initializing RunHistoryController");
        
        // Setup table columns
        demoTitleColumn.setCellValueFactory(cellData -> 
                new SimpleStringProperty(cellData.getValue().getDemoTitle()));
        
        startTimeColumn.setCellValueFactory(cellData -> 
                new SimpleStringProperty(cellData.getValue().getStartTime().format(DATE_FORMATTER)));
        
        durationColumn.setCellValueFactory(cellData -> 
                new SimpleStringProperty(cellData.getValue().getDurationSeconds() + "s"));
        
        statusColumn.setCellValueFactory(cellData -> 
                new SimpleStringProperty(cellData.getValue().getStatus().getDisplayName()));
        
        exitCodeColumn.setCellValueFactory(cellData -> 
                new SimpleStringProperty(String.valueOf(cellData.getValue().getExitCode())));
        
        // Apply status styling
        statusColumn.setCellFactory(column -> new TableCell<RunResult, String>() {
            @Override
            protected void updateItem(String item, boolean empty) {
                super.updateItem(item, empty);
                if (empty || item == null) {
                    setText(null);
                    setGraphic(null);
                    setStyle("");
                } else {
                    setText(item);
                    RunResult result = getTableView().getItems().get(getIndex());
                    if (result.getStatus() == RunResult.RunStatus.SUCCESS) {
                        setStyle("-fx-text-fill: #27ae60; -fx-font-weight: bold;");
                    } else if (result.getStatus() == RunResult.RunStatus.FAILED) {
                        setStyle("-fx-text-fill: #e74c3c; -fx-font-weight: bold;");
                    } else {
                        setStyle("-fx-text-fill: #f39c12; -fx-font-weight: bold;");
                    }
                }
            }
        });
        
        // Selection listener
        historyTable.getSelectionModel().selectedItemProperty().addListener(
                (observable, oldValue, newValue) -> showRunDetails(newValue));
        
        // Load data
        loadHistory();
    }

    private void loadHistory() {
        List<RunResult> history = configManager.loadRunHistory();
        runResults = FXCollections.observableArrayList(history);
        historyTable.setItems(runResults);
        
        updateStatistics();
        
        logger.info("Loaded {} run results", history.size());
    }

    private void updateStatistics() {
        Map<String, Object> stats = configManager.getRunStatistics();
        
        int total = (Integer) stats.get("totalRuns");
        long success = (Long) stats.get("successfulRuns");
        long failed = (Long) stats.get("failedRuns");
        
        statsLabel.setText(String.format("Total: %d | Success: %d | Failed: %d", 
                                         total, success, failed));
    }

    private void showRunDetails(RunResult result) {
        if (result == null) {
            detailsPane.setVisible(false);
            detailsPane.setManaged(false);
            return;
        }
        
        detailsPane.setVisible(true);
        detailsPane.setManaged(true);
        
        runIdLabel.setText(result.getRunId());
        demoIdLabel.setText(result.getDemoId());
        logFileLabel.setText(result.getLogFilePath() != null ? result.getLogFilePath() : "N/A");
        outputSnapshotArea.setText(result.getOutputSnapshot() != null ? 
                                   result.getOutputSnapshot() : "No output snapshot available.");
    }

    @FXML
    private void handleRefresh() {
        loadHistory();
        logger.info("History refreshed");
    }

    @FXML
    private void handleClearAll() {
        Alert confirm = new Alert(Alert.AlertType.CONFIRMATION);
        confirm.setTitle("Clear All History");
        confirm.setHeaderText("Delete all run history?");
        confirm.setContentText("This action cannot be undone. All " + runResults.size() + 
                              " run records will be permanently deleted.");
        
        confirm.showAndWait().ifPresent(response -> {
            if (response == ButtonType.OK) {
                int cleared = configManager.clearRunHistory();
                loadHistory();
                detailsPane.setVisible(false);
                detailsPane.setManaged(false);
                
                Alert info = new Alert(Alert.AlertType.INFORMATION);
                info.setTitle("History Cleared");
                info.setHeaderText(null);
                info.setContentText("Cleared " + cleared + " run records.");
                info.showAndWait();
                
                logger.info("Cleared all history: {} records", cleared);
            }
        });
    }

    @FXML
    private void handleDeleteRun() {
        RunResult selected = historyTable.getSelectionModel().getSelectedItem();
        if (selected == null) {
            return;
        }
        
        Alert confirm = new Alert(Alert.AlertType.CONFIRMATION);
        confirm.setTitle("Delete Run");
        confirm.setHeaderText("Delete this run record?");
        confirm.setContentText("Run: " + selected.getDemoTitle() + "\n" +
                              "Started: " + selected.getStartTime().format(DATE_FORMATTER));
        
        confirm.showAndWait().ifPresent(response -> {
            if (response == ButtonType.OK) {
                boolean deleted = configManager.deleteRunResult(selected.getRunId());
                if (deleted) {
                    loadHistory();
                    detailsPane.setVisible(false);
                    detailsPane.setManaged(false);
                    logger.info("Deleted run: {}", selected.getRunId());
                } else {
                    Alert error = new Alert(Alert.AlertType.ERROR);
                    error.setTitle("Error");
                    error.setHeaderText(null);
                    error.setContentText("Failed to delete run record.");
                    error.showAndWait();
                }
            }
        });
    }

    @FXML
    private void handleClose() {
        Stage stage = (Stage) historyTable.getScene().getWindow();
        stage.close();
    }
}
