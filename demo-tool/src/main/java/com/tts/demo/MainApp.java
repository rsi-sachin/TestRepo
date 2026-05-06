package com.tts.demo;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Main entry point for the TTS Demo Tool JavaFX application.
 * 
 * Phase 1: JavaFX desktop application
 * Phase 2: Spring Boot + Vanilla JS web application (reuse service layer)
 * 
 * Note: Uses self-contained reference tests that include both client and server components,
 * satisfying REQ-004 (Isolated IMS environment testing with no external systems needed).
 */
public class MainApp extends Application {
    
    private static final Logger logger = LoggerFactory.getLogger(MainApp.class);
    private static final String APP_TITLE = "TTS Demo Tool";
    private static final int WINDOW_WIDTH = 1400;
    private static final int WINDOW_HEIGHT = 900;

    @Override
    public void start(Stage primaryStage) {
        try {
            logger.info("Starting TTS Demo Tool application");
            
            // Load FXML
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/main.fxml"));
            Parent root = loader.load();
            
            // Create scene
            Scene scene = new Scene(root, WINDOW_WIDTH, WINDOW_HEIGHT);
            
            // Setup stage
            primaryStage.setTitle(APP_TITLE);
            primaryStage.setScene(scene);
            primaryStage.setMinWidth(1000);
            primaryStage.setMinHeight(700);
            
            // Show window
            primaryStage.show();
            
            logger.info("TTS Demo Tool application started successfully");
            
        } catch (Exception e) {
            logger.error("Failed to start application", e);
            showErrorAndExit("Failed to start application: " + e.getMessage());
        }
    }

    @Override
    public void stop() {
        logger.info("TTS Demo Tool application stopping");
    }

    private void showErrorAndExit(String message) {
        javafx.scene.control.Alert alert = new javafx.scene.control.Alert(
                javafx.scene.control.Alert.AlertType.ERROR);
        alert.setTitle("Startup Error");
        alert.setHeaderText("Failed to start TTS Demo Tool");
        alert.setContentText(message);
        alert.showAndWait();
        System.exit(1);
    }

    public static void main(String[] args) {
        logger.info("Launching TTS Demo Tool");
        launch(args);
    }
}
