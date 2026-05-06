package com.tts.demo.service;

import com.tts.demo.model.Demo;
import com.tts.demo.model.DemoConfig;
import com.tts.demo.model.RunResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.net.DatagramSocket;
import java.net.SocketException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

/**
 * Executes demo scenarios by invoking JMeter in non-GUI mode.
 * Streams live output and captures run results.
 */
public class DemoRunner {
    
    private static final Logger logger = LoggerFactory.getLogger(DemoRunner.class);
    private static final String JMETER_CMD = "C:\\TTS\\bin\\jmeter.bat";
    private static final String JMETER_HOME = "C:\\TTS";
    private static final String JMETER_BIN_DIR = "C:\\TTS\\bin";
    private static final String LOGS_DIR = "logs";
    private static final DateTimeFormatter LOG_DATE_FORMAT = 
            DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");
    
    // SIP/IMS port configuration for VoLTE tests
    private static final int SIP_SERVER_PORT = 5060;
    private static final int SIP_CLIENT_PORT = 5065;
    
    private final ConfigManager configManager;
    private Process currentProcess;
    private File tempJmxFile; // Track temporary JMX file for cleanup

    public DemoRunner(ConfigManager configManager) {
        this.configManager = configManager;
        ensureLogsDirectoryExists();
    }

    /**
     * Creates the logs directory if it doesn't exist.
     */
    private void ensureLogsDirectoryExists() {
        try {
            Path logsPath = Paths.get(LOGS_DIR);
            if (!Files.exists(logsPath)) {
                Files.createDirectories(logsPath);
            }
        } catch (IOException e) {
            logger.error("Failed to create logs directory", e);
        }
    }

    /**
     * Executes a demo scenario asynchronously.
     * Streams output to the provided consumer in real-time.
     * 
     * @param demo The demo to execute
     * @param config Configuration parameters for the demo
     * @param outputConsumer Consumer that receives live output lines
     * @return RunResult with execution metadata
     */
    public RunResult runDemo(Demo demo, DemoConfig config, Consumer<String> outputConsumer) {
        String runId = UUID.randomUUID().toString();
        RunResult result = new RunResult(runId, demo.getId(), demo.getTitle());
        
        // Validate JMX file exists before attempting execution
        File jmxFile = new File(demo.getJmxPath());
        if (!jmxFile.exists()) {
            String errorMsg = "JMX file not found: " + demo.getJmxPath();
            result.fail(errorMsg);
            logger.error("Pre-flight check failed for demo '{}': {}", demo.getTitle(), errorMsg);
            configManager.saveRunResult(result);
            return result;
        }
        
        // Validate UDP ports for SIP/IMS demos
        if (demo.getProtocol() == Demo.Protocol.SIP_IMS) {
            logger.debug("Validating UDP port availability for SIP/IMS demo...");
            String portError = validatePortAvailability(SIP_SERVER_PORT, SIP_CLIENT_PORT);
            if (portError != null) {
                result.fail(portError);
                logger.error("Port validation failed for demo '{}': {}", demo.getTitle(), portError);
                configManager.saveRunResult(result);
                return result;
            }
            logger.debug("Port validation successful - ports {} and {} are available", 
                        SIP_SERVER_PORT, SIP_CLIENT_PORT);
        }
        
        // Merge default parameters with configuration
        config.mergeDefaults(demo.getDefaultParams());
        
        String logFilePath = generateLogFilePath(demo.getId());
        result.setLogFilePath(logFilePath);
        
        try {
            // CRITICAL: Copy JMX to C:\TTS\bin directory (required for TTS license access)
            String jmxPathForExecution = copyJmxToTtsBin(jmxFile, runId);
            logger.info("JMX file copied to TTS bin directory for license access: {}", jmxPathForExecution);
            
            // Build JMeter command with copied JMX path
            List<String> command = buildJMeterCommand(jmxPathForExecution, logFilePath, config);
            
            logger.info("Starting demo execution: {} (runId: {})", demo.getTitle(), runId);
            logger.debug("Command: {}", String.join(" ", command));
            
            // Start process with working directory set to C:\TTS\bin for license access
            ProcessBuilder pb = new ProcessBuilder(command);
            pb.directory(new File(JMETER_BIN_DIR)); // CRITICAL: Set working directory for license access
            pb.redirectErrorStream(true);
            pb.environment().put("JMETER_HOME", JMETER_HOME);
            currentProcess = pb.start();
            
            // Stream output with enhanced progress logging
            new Thread(() -> streamOutput(currentProcess, outputConsumer, demo)).start();
            
            // Log expected timing for SIP/IMS demos
            if (demo.getProtocol() == Demo.Protocol.SIP_IMS && outputConsumer != null) {
                outputConsumer.accept("[INFO] Expected startup time: ~15 seconds (thread synchronization buffer)");
                outputConsumer.accept("[INFO] Watching for Server and Client thread activity...");
            }
            
            // Wait for completion
            boolean finished = currentProcess.waitFor(10, TimeUnit.MINUTES);
            
            if (finished) {
                int exitCode = currentProcess.exitValue();
                result.complete(exitCode);
                logger.info("Demo execution completed: {} (exit code: {})", demo.getTitle(), exitCode);
            } else {
                currentProcess.destroyForcibly();
                result.fail("Execution timeout after 10 minutes");
                logger.error("Demo execution timeout: {}", demo.getTitle());
            }
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            result.fail("Execution interrupted");
            logger.error("Demo execution interrupted: {}", demo.getTitle(), e);
        } catch (Exception e) {
            result.fail("Execution error: " + e.getMessage());
            logger.error("Demo execution failed: {}", demo.getTitle(), e);
        } finally {
            currentProcess = null;
            cleanupTempJmxFile(); // Clean up temporary JMX file
            configManager.saveRunResult(result);
        }
        
        return result;
    }

    /**
     * Stops the currently running demo.
     */
    public void stopCurrentDemo() {
        if (currentProcess != null && currentProcess.isAlive()) {
            logger.info("Stopping current demo execution");
            currentProcess.destroyForcibly();
        }
    }

    /**
     * Checks if a demo is currently running.
     */
    public boolean isRunning() {
        return currentProcess != null && currentProcess.isAlive();
    }

    /**
     * Builds the JMeter command with all parameters.
     */
    private List<String> buildJMeterCommand(String jmxPath, String logPath, DemoConfig config) {
        List<String> command = new ArrayList<>();
        command.add(JMETER_CMD);
        command.add("-n");
        command.add("-t");
        command.add(jmxPath);
        command.add("-l");
        command.add(logPath);
        
        // Add parameters
        String[] params = config.toJMeterArgs();
        for (String param : params) {
            command.add(param);
        }
        
        return command;
    }

    /**
     * Generates a unique log file path for the run.
     */
    private String generateLogFilePath(String demoId) {
        String timestamp = LocalDateTime.now().format(LOG_DATE_FORMAT);
        Path logsPath = Paths.get(LOGS_DIR).toAbsolutePath();
        return String.format("%s\\log_%s_%s.jtl", logsPath.toString(), timestamp, demoId);
    }

    /**
     * Streams process output to the consumer line by line with enhanced progress indicators.
     * Detects and highlights key execution events for better user feedback.
     * 
     * @param process The JMeter process
     * @param outputConsumer Consumer that receives output lines
     * @param demo The demo being executed (for protocol-specific enhancements)
     */
    private void streamOutput(Process process, Consumer<String> outputConsumer, Demo demo) {
        boolean testStarted = false;
        boolean summaryShown = false;
        
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                // Enhance key log patterns for better visibility
                String enhancedLine = line;
                
                // Detect test start
                if (line.contains("Starting standalone test")) {
                    if (outputConsumer != null) {
                        outputConsumer.accept("[PROGRESS] JMeter test execution started");
                    }
                    testStarted = true;
                }
                
                // Detect thread group activity
                if (line.contains("Thread started") && demo.getProtocol() == Demo.Protocol.SIP_IMS) {
                    if (outputConsumer != null) {
                        if (line.contains("Server")) {
                            outputConsumer.accept("[PROGRESS] Server thread initialized");
                        } else if (line.contains("Client")) {
                            outputConsumer.accept("[PROGRESS] Client thread initialized");
                        }
                    }
                }
                
                // Enhance summary output
                if (line.contains("summary =") && !summaryShown) {
                    if (outputConsumer != null) {
                        outputConsumer.accept("[PROGRESS] Execution in progress...");
                        outputConsumer.accept(enhancedLine);
                    }
                    summaryShown = true;
                    logger.info("JMeter summary: {}", line.trim());
                    continue; // Skip normal processing for summary line
                }
                
                // Detect test completion
                if (line.contains("Tidying up")) {
                    if (outputConsumer != null) {
                        outputConsumer.accept("[PROGRESS] Test completed, cleaning up...");
                    }
                }
                
                if (line.contains("end of run")) {
                    if (outputConsumer != null) {
                        outputConsumer.accept("[PROGRESS] JMeter execution finished");
                    }
                }
                
                // Send line to consumer (unless already sent above)
                if (outputConsumer != null && !line.contains("summary =")) {
                    outputConsumer.accept(enhancedLine);
                }
                
                // Log all output at debug level
                logger.debug("JMeter output: {}", line);
            }
        } catch (IOException e) {
            logger.error("Error reading process output", e);
        }
    }

    /**
     * Validates that JMeter is accessible.
     */
    public boolean validateJMeterInstallation() {
        File jmeterCmd = new File(JMETER_CMD);
        boolean exists = jmeterCmd.exists();
        
        if (!exists) {
            logger.error("JMeter command not found: {}", JMETER_CMD);
        } else {
            logger.info("JMeter installation validated: {}", JMETER_CMD);
        }
        
        return exists;
    }

    /**
     * Gets the JMeter command path.
     */
    public String getJMeterCommand() {
        return JMETER_CMD;
    }
    
    /**
     * Copies the JMX file to C:\TTS\bin directory.
     * This is required for TTS license file access which is only available from that directory.
     * 
     * @param sourceJmxFile The source JMX file to copy
     * @param runId Unique run identifier for creating a unique filename
     * @return Path to the copied JMX file
     * @throws IOException if copy fails
     */
    private String copyJmxToTtsBin(File sourceJmxFile, String runId) throws IOException {
        String fileName = String.format("demo_temp_%s.jmx", runId.substring(0, 8));
        Path targetPath = Paths.get(JMETER_BIN_DIR, fileName);
        
        Files.copy(sourceJmxFile.toPath(), targetPath, StandardCopyOption.REPLACE_EXISTING);
        tempJmxFile = targetPath.toFile();
        
        logger.debug("Copied JMX file from {} to {}", sourceJmxFile.getAbsolutePath(), targetPath);
        return targetPath.toString();
    }
    
    /**
     * Cleans up the temporary JMX file created in C:\TTS\bin directory.
     */
    private void cleanupTempJmxFile() {
        if (tempJmxFile != null && tempJmxFile.exists()) {
            try {
                if (tempJmxFile.delete()) {
                    logger.debug("Cleaned up temporary JMX file: {}", tempJmxFile.getAbsolutePath());
                } else {
                    logger.warn("Failed to delete temporary JMX file: {}", tempJmxFile.getAbsolutePath());
                }
            } catch (Exception e) {
                logger.error("Error cleaning up temporary JMX file", e);
            } finally {
                tempJmxFile = null;
            }
        }
    }
    
    /**
     * Validates that the specified UDP ports are available for binding.
     * This is critical for SIP/IMS tests which require specific ports to be free.
     * 
     * @param ports UDP port numbers to validate
     * @return null if all ports are available, error message otherwise
     */
    private String validatePortAvailability(int... ports) {
        for (int port : ports) {
            DatagramSocket socket = null;
            try {
                // Try to bind to the UDP port
                socket = new DatagramSocket(port);
                socket.setReuseAddress(true);
                logger.debug("UDP port {} is available", port);
            } catch (SocketException e) {
                String errorMsg = String.format("UDP port %d is already in use or unavailable: %s", 
                                               port, e.getMessage());
                logger.warn(errorMsg);
                return errorMsg;
            } finally {
                if (socket != null && !socket.isClosed()) {
                    socket.close();
                }
            }
        }
        return null; // All ports available
    }
}
