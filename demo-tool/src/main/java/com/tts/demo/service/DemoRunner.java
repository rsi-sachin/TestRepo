package com.tts.demo.service;

import com.tts.demo.model.Demo;
import com.tts.demo.model.DemoConfig;
import com.tts.demo.model.RunResult;
import com.tts.demo.model.SipMessage;
import com.tts.demo.model.TrafficProfile;
import com.tts.demo.model.TrafficStats;
import com.tts.demo.model.ActorType;
import com.tts.demo.model.FailureType;
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
    private Process trafficProcess; // Separate process for traffic generation
    private volatile boolean stopTrafficGeneration = false; // Flag to stop traffic generation
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
        // Call the dual-consumer version with a no-op message consumer for backward compatibility
        return runDemo(demo, config, outputConsumer, null);
    }
    
    /**
     * Executes a demo scenario asynchronously with real-time SIP message capture.
     * Streams output to the provided consumer and captures SIP messages for live visualization.
     * 
     * @param demo The demo to execute
     * @param config Configuration parameters for the demo
     * @param outputConsumer Consumer that receives live output lines (for terminal display)
     * @param messageConsumer Consumer that receives parsed SipMessage objects (for live diagram), can be null
     * @return RunResult with execution metadata
     */
    public RunResult runDemo(Demo demo, DemoConfig config, Consumer<String> outputConsumer, Consumer<SipMessage> messageConsumer) {
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
            new Thread(() -> streamOutput(currentProcess, outputConsumer, messageConsumer, demo)).start();
            
            // For SIP/IMS demos, tail the JTL file in real-time for live message capture
            Thread jtlTailerThread = null;
            if (demo.getProtocol() == Demo.Protocol.SIP_IMS && messageConsumer != null) {
                final String jtlPath = result.getLogFilePath();
                jtlTailerThread = new Thread(() -> tailJtlFile(jtlPath, messageConsumer, currentProcess));
                jtlTailerThread.setDaemon(true);
                jtlTailerThread.setName("JTL-Tailer-" + demo.getId());
                jtlTailerThread.start();
                logger.info("Started JTL file tailer for real-time message capture: {}", jtlPath);
            }
            
            // Log expected timing for SIP/IMS demos
            if (demo.getProtocol() == Demo.Protocol.SIP_IMS && outputConsumer != null) {
                outputConsumer.accept("[INFO] Expected startup time: ~15 seconds (thread synchronization buffer)");
                outputConsumer.accept("[INFO] Watching for real-time call flow updates...");
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
        
        // Enable auto-flush for JTL file to support real-time tailing
        // This forces JMeter to write each sampler result immediately instead of buffering
        command.add("-Jjmeter.save.saveservice.autoflush=true");
        
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
     * Tails a JTL file in real-time, parsing and sending SIP messages as they're written.
     * This enables true real-time call flow visualization during test execution.
     * Package-private for testing.
     * 
     * @param jtlFilePath Path to the JTL file being written by JMeter
     * @param messageConsumer Consumer that receives parsed SipMessage objects
     * @param process The JMeter process (to check if still running)
     */
    void tailJtlFile(String jtlFilePath, Consumer<SipMessage> messageConsumer, Process process) {
        File jtlFile = new File(jtlFilePath);
        long lastPosition = 0;
        boolean headerSkipped = false;
        int messagesProcessed = 0;
        
        logger.info("[JTL-TAILER] Starting to tail JTL file: {}", jtlFilePath);
        
        // Wait for file to be created (JMeter might not create it immediately)
        // Increased timeout to 15 seconds to account for slower disk I/O or JMeter startup delays
        int waitAttempts = 0;
        while (!jtlFile.exists() && process.isAlive() && waitAttempts < 150) {
            try {
                Thread.sleep(100);
                waitAttempts++;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
        }
        
        if (!jtlFile.exists()) {
            logger.warn("[JTL-TAILER] JTL file not created after 15 seconds: {}", jtlFilePath);
            return;
        }
        
        logger.info("[JTL-TAILER] JTL file detected, starting real-time parsing");
        
        // Tail the file until process completes
        while (process.isAlive() || jtlFile.length() > lastPosition) {
            try {
                if (jtlFile.length() > lastPosition) {
                    try (RandomAccessFile raf = new RandomAccessFile(jtlFile, "r")) {
                        raf.seek(lastPosition);
                        String line;
                        
                        while ((line = raf.readLine()) != null) {
                            // Skip CSV header
                            if (!headerSkipped) {
                                headerSkipped = true;
                                lastPosition = raf.getFilePointer();
                                continue;
                            }
                            
                            // Parse the CSV line into a SipMessage
                            SipMessage message = parseJtlLine(line);
                            if (message != null) {
                                messageConsumer.accept(message);
                                messagesProcessed++;
                                logger.info("[JTL-TAILER] Real-time message #{}: {} {} ({}ms)", 
                                    messagesProcessed,
                                    message.getDirection().getDisplayName(),
                                    message.getMessageType().getDisplayName(),
                                    message.getElapsed());
                            }
                            
                            lastPosition = raf.getFilePointer();
                        }
                    } catch (IOException e) {
                        logger.error("[JTL-TAILER] Error reading JTL file", e);
                    }
                }
                
                // Short sleep to avoid busy-waiting
                Thread.sleep(50);
                
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        logger.info("[JTL-TAILER] Stopped tailing JTL file. Total messages processed: {}", messagesProcessed);
    }
    
    /**
     * Determine if a JTL label should be skipped (not a real SIP message).
     * Filters out timer samplers, variable extractors, debug samplers, and other non-SIP elements.
     * Package-private for testing.
     * 
     * @param label The label from the JTL CSV line
     * @return true if the label should be skipped, false if it's a valid SIP message
     */
    boolean shouldSkipLabel(String label) {
        if (label == null || label.trim().isEmpty()) {
            return true;
        }
        
        String upper = label.toUpperCase();
        
        // Filter out common non-SIP samplers
        return upper.contains("WAIT FOR") ||
               upper.contains("GENERATE") ||
               upper.contains("TIMER") ||
               upper.contains("DEBUG") ||
               upper.contains("STARTING") ||
               upper.contains("CALLID") ||
               upper.contains("DELAY") ||              // "Short Delay", "Long Delay"
               label.startsWith("A") ||               // "ATo:", "AFrom:", "AVia:", "ACallID:"
               upper.contains("EXTRACT") ||
               (upper.contains("SAMPLER") && upper.contains("DEBUG")) ||
               label.startsWith("===") ||             // "=== Call was a normal scenario ==="
               upper.contains("SCENARIO") ||          // Test scenario assertions
               upper.contains("ASSERTION");           // Assertion samplers
    }
    
    /**
     * Parse a single JTL CSV line into a SipMessage object.
     * JTL format: timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,...
     * Package-private for testing.
     * 
     * @param line CSV line from JTL file
     * @return SipMessage object or null if line cannot be parsed or should be skipped
     */
    SipMessage parseJtlLine(String line) {
        if (line == null || line.trim().isEmpty()) {
            return null;
        }
        
        String[] fields = line.split(",");
        if (fields.length < 8) {
            return null;
        }
        
        try {
            long timestamp = Long.parseLong(fields[0].trim());
            long elapsed = Long.parseLong(fields[1].trim());
            String label = fields[2].trim();
            String responseCode = fields[3].trim();
            String threadName = fields[5].trim();
            boolean success = Boolean.parseBoolean(fields[7].trim());
            
            // Filter out non-SIP messages (timers, wait conditions, etc.)
            if (shouldSkipLabel(label)) {
                logger.debug("[JTL-TAILER] Skipping non-SIP label: {}", label);
                return null;
            }
            
            // Determine message type and direction
            SipMessage.MessageType messageType = SipMessage.MessageType.fromLabel(label);
            SipMessage.Direction direction = SipMessage.Direction.fromThreadAndLabel(threadName, label);
            
            // Log if message type is OTHER for debugging
            if (messageType == SipMessage.MessageType.OTHER) {
                logger.warn("[JTL-TAILER] Unrecognized SIP message label: '{}' - classified as OTHER", label);
            }
            
            return new SipMessage(
                messageType,
                direction,
                threadName,
                timestamp,
                elapsed,
                success,
                responseCode,
                label
            );
            
        } catch (Exception e) {
            logger.warn("[JTL-TAILER] Failed to parse JTL line: {} - Error: {}", line, e.getMessage());
            return null;
        }
    }
    
    /**
     * Streams process output to the consumer line by line with enhanced progress indicators.
     * Detects and highlights key execution events for better user feedback.
     * Note: Real-time message capture now happens via JTL tailing, not console parsing.
     * 
     * @param process The JMeter process
     * @param outputConsumer Consumer that receives output lines (for terminal display)
     * @param messageConsumer Consumer that receives parsed SipMessage objects (deprecated - use JTL tailing)
     * @param demo The demo being executed (for protocol-specific enhancements)
     */
    private void streamOutput(Process process, Consumer<String> outputConsumer, Consumer<SipMessage> messageConsumer, Demo demo) {
        boolean testStarted = false;
        boolean summaryShown = false;
        int sipMessageCount = 0;
        int successfulSipMessages = 0;
        
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
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
                
                // Detect and format SIP messages for SIP/IMS protocol
                if (demo.getProtocol() == Demo.Protocol.SIP_IMS) {
                    // Parse SIP message for real-time capture
                    SipMessage sipMessage = parseSipMessageFromOutput(line);
                    if (sipMessage != null) {
                        sipMessageCount++;
                        if (sipMessage.isSuccess()) {
                            successfulSipMessages++;
                        }
                        
                        // Send parsed message to live diagram consumer (if provided)
                        if (messageConsumer != null) {
                            messageConsumer.accept(sipMessage);
                        }
                        
                        // Format and send to terminal output consumer
                        String formattedSipMessage = detectAndFormatSipMessage(line);
                        if (outputConsumer != null && formattedSipMessage != null) {
                            outputConsumer.accept(formattedSipMessage);
                        }
                        
                        logger.debug("SIP Message detected: {}", formattedSipMessage);
                        continue; // Skip normal processing for SIP messages
                    }
                }
                
                // Enhance summary output
                if (line.contains("summary =") && !summaryShown) {
                    if (outputConsumer != null) {
                        outputConsumer.accept("[PROGRESS] Execution in progress...");
                        outputConsumer.accept("[INFO] " + line.trim());
                    }
                    summaryShown = true;
                    logger.info("JMeter summary: {}", line.trim());
                    continue;
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
                        
                        // Add call flow summary for SIP/IMS tests
                        if (demo.getProtocol() == Demo.Protocol.SIP_IMS && sipMessageCount > 0) {
                            outputConsumer.accept("");
                            outputConsumer.accept("════════════════════════════════════════════");
                            outputConsumer.accept("            Call Flow Summary               ");
                            outputConsumer.accept("════════════════════════════════════════════");
                            outputConsumer.accept(String.format("Total SIP Messages: %d", sipMessageCount));
                            outputConsumer.accept(String.format("Successful: %d (%.1f%%)", 
                                    successfulSipMessages, 
                                    (successfulSipMessages * 100.0) / sipMessageCount));
                            outputConsumer.accept(String.format("Failed: %d", sipMessageCount - successfulSipMessages));
                            outputConsumer.accept("════════════════════════════════════════════");
                            outputConsumer.accept("");
                        }
                    }
                }
                
                // Filter out noise - only show important lines
                if (shouldShowLine(line)) {
                    if (outputConsumer != null) {
                        outputConsumer.accept(line);
                    }
                }
                
                // Log all output at debug level
                logger.debug("JMeter output: {}", line);
            }
        } catch (IOException e) {
            logger.error("Error reading process output", e);
        }
    }
    
    /**
     * Detect and format SIP messages from JMeter output
     * 
     * @param line JMeter output line
     * @return Formatted SIP message or null if not a SIP message
     */
    private String detectAndFormatSipMessage(String line) {
        if (line == null || line.isEmpty()) {
            return null;
        }
        
        // Skip timer and utility messages
        if (line.contains("Wait for") || line.contains("Generate") || line.contains("Timer")) {
            return null;
        }
        
        // Detect Send/Listen patterns
        String direction = null;
        String messageType = null;
        String threadType = null;
        String elapsedTime = null;
        
        // Extract thread type (Client or Server)
        if (line.contains("Client")) {
            threadType = "Client";
        } else if (line.contains("Server")) {
            threadType = "Server";
        } else {
            return null; // Not a client/server message
        }
        
        // Detect Send messages (outgoing)
        if (line.contains("Send ")) {
            if (threadType.equals("Client")) {
                direction = "Client → Server";
            } else {
                direction = "Server → Client";
            }
            
            // Extract message type
            if (line.contains("INVITE")) messageType = "INVITE";
            else if (line.contains("TRYING")) messageType = "TRYING";
            else if (line.contains("RINGING")) messageType = "RINGING";
            else if (line.contains("OK")) messageType = "OK";
            else if (line.contains("ACK")) messageType = "ACK";
            else if (line.contains("BYE")) messageType = "BYE";
        }
        
        // Detect Listen messages (incoming - reverse direction)
        else if (line.contains("Listen for ")) {
            if (threadType.equals("Client")) {
                direction = "Server → Client"; // Client listening receives from server
            } else {
                direction = "Client → Server"; // Server listening receives from client
            }
            
            // Extract message type
            if (line.contains("INVITE")) messageType = "INVITE";
            else if (line.contains("TRYING")) messageType = "TRYING";
            else if (line.contains("RINGING")) messageType = "RINGING";
            else if (line.contains("OK")) messageType = "OK";
            else if (line.contains("ACK")) messageType = "ACK";
            else if (line.contains("BYE")) messageType = "BYE";
        }
        
        // If we found a SIP message, format it
        if (direction != null && messageType != null) {
            // Try to extract elapsed time if available (format: "elapsed: 97ms")
            if (line.contains("elapsed:")) {
                int elapsedIdx = line.indexOf("elapsed:");
                if (elapsedIdx != -1) {
                    String remaining = line.substring(elapsedIdx + 8).trim();
                    int spaceIdx = remaining.indexOf(' ');
                    if (spaceIdx != -1) {
                        elapsedTime = remaining.substring(0, spaceIdx);
                    }
                }
            }
            
            // Format the message
            String status = line.contains("successfully") ? "[OK]" : 
                           line.contains("failed") ? "[FAIL]" : "";
            
            if (elapsedTime != null) {
                return String.format("[SIP] %s %s (elapsed: %s) %s", 
                        direction, messageType, elapsedTime, status);
            } else {
                return String.format("[SIP] %s %s %s", direction, messageType, status);
            }
        }
        
        return null;
    }
    
    /**
     * Determine if a line should be shown in the output (filter noise)
     * 
     * @param line JMeter output line
     * @return true if line should be shown
     */
    private boolean shouldShowLine(String line) {
        if (line == null || line.isEmpty()) {
            return false;
        }
        
        // Always show lines with these markers
        if (line.contains("[PROGRESS]") || 
            line.contains("[INFO]") || 
            line.contains("[SIP]") ||
            line.contains("[ERROR]") ||
            line.contains("summary =")) {
            return true;
        }
        
        // Filter out common noise patterns
        if (line.contains("Waiting for possible Shutdown") ||
            line.contains("Notifying test listeners") ||
            line.contains("StandardJMeterEngine") ||
            line.contains("Listener") ||
            line.contains("DEBUG") ||
            line.trim().isEmpty()) {
            return false;
        }
        
        // Show errors and warnings
        if (line.contains("ERROR") || line.contains("WARN")) {
            return true;
        }
        
        return false; // Filter everything else
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
     * Parse SIP message from JMeter output line and create SipMessage object.
     * This method extracts message metadata for real-time call flow visualization.
     * 
     * @param line JMeter output line
     * @return SipMessage object or null if line is not a SIP message
     */
    public SipMessage parseSipMessageFromOutput(String line) {
        if (line == null || line.isEmpty()) {
            return null;
        }
        
        // Skip timer and utility messages
        if (line.contains("Wait for") || line.contains("Generate") || line.contains("Timer")) {
            return null;
        }
        
        // Extract thread type (Client or Server)
        String threadName = null;
        if (line.contains("Client")) {
            threadName = "Client";
        } else if (line.contains("Server")) {
            threadName = "Server";
        } else {
            return null; // Not a client/server message
        }
        
        // Determine message type and direction
        SipMessage.MessageType messageType = null;
        SipMessage.Direction direction = null;
        String label = null;
        
        // Detect Send messages (outgoing)
        if (line.contains("Send ")) {
            label = "Send";
            if (threadName.equals("Client")) {
                direction = SipMessage.Direction.CLIENT_TO_SERVER;
            } else {
                direction = SipMessage.Direction.SERVER_TO_CLIENT;
            }
            
            // Extract message type from line
            if (line.contains("INVITE")) {
                messageType = SipMessage.MessageType.INVITE;
                label = "Send INVITE";
            } else if (line.contains("TRYING")) {
                messageType = SipMessage.MessageType.TRYING;
                label = "Send TRYING";
            } else if (line.contains("RINGING")) {
                messageType = SipMessage.MessageType.RINGING;
                label = "Send RINGING";
            } else if (line.contains("OK")) {
                messageType = SipMessage.MessageType.OK;
                label = "Send OK";
            } else if (line.contains("ACK")) {
                messageType = SipMessage.MessageType.ACK;
                label = "Send ACK";
            } else if (line.contains("BYE")) {
                messageType = SipMessage.MessageType.BYE;
                label = "Send BYE";
            } else if (line.contains("REGISTER")) {
                messageType = SipMessage.MessageType.REGISTER;
                label = "Send REGISTER";
            } else if (line.contains("OPTIONS")) {
                messageType = SipMessage.MessageType.OPTIONS;
                label = "Send OPTIONS";
            } else if (line.contains("INFO")) {
                messageType = SipMessage.MessageType.INFO;
                label = "Send INFO";
            } else if (line.contains("PRACK")) {
                messageType = SipMessage.MessageType.PRACK;
                label = "Send PRACK";
            } else if (line.contains("UPDATE")) {
                messageType = SipMessage.MessageType.UPDATE;
                label = "Send UPDATE";
            }
        }
        
        // Detect Listen messages (incoming - reverse direction)
        else if (line.contains("Listen for ")) {
            label = "Listen for";
            if (threadName.equals("Client")) {
                direction = SipMessage.Direction.SERVER_TO_CLIENT; // Client listening receives from server
            } else {
                direction = SipMessage.Direction.CLIENT_TO_SERVER; // Server listening receives from client
            }
            
            // Extract message type from line
            if (line.contains("INVITE")) {
                messageType = SipMessage.MessageType.INVITE;
                label = "Listen for INVITE";
            } else if (line.contains("TRYING")) {
                messageType = SipMessage.MessageType.TRYING;
                label = "Listen for TRYING";
            } else if (line.contains("RINGING")) {
                messageType = SipMessage.MessageType.RINGING;
                label = "Listen for RINGING";
            } else if (line.contains("OK")) {
                messageType = SipMessage.MessageType.OK;
                label = "Listen for OK";
            } else if (line.contains("ACK")) {
                messageType = SipMessage.MessageType.ACK;
                label = "Listen for ACK";
            } else if (line.contains("BYE")) {
                messageType = SipMessage.MessageType.BYE;
                label = "Listen for BYE";
            } else if (line.contains("REGISTER")) {
                messageType = SipMessage.MessageType.REGISTER;
                label = "Listen for REGISTER";
            } else if (line.contains("OPTIONS")) {
                messageType = SipMessage.MessageType.OPTIONS;
                label = "Listen for OPTIONS";
            } else if (line.contains("INFO")) {
                messageType = SipMessage.MessageType.INFO;
                label = "Listen for INFO";
            } else if (line.contains("PRACK")) {
                messageType = SipMessage.MessageType.PRACK;
                label = "Listen for PRACK";
            } else if (line.contains("UPDATE")) {
                messageType = SipMessage.MessageType.UPDATE;
                label = "Listen for UPDATE";
            }
        }
        
        // If we found a valid SIP message, create SipMessage object
        if (direction != null && messageType != null && label != null) {
            // Try to extract elapsed time if available (format: "elapsed: 97ms")
            long elapsed = 0;
            if (line.contains("elapsed:")) {
                try {
                    int elapsedIdx = line.indexOf("elapsed:");
                    String remaining = line.substring(elapsedIdx + 8).trim();
                    int spaceIdx = remaining.indexOf(' ');
                    if (spaceIdx != -1) {
                        String elapsedStr = remaining.substring(0, spaceIdx).replace("ms", "").trim();
                        elapsed = Long.parseLong(elapsedStr);
                    }
                } catch (Exception e) {
                    logger.debug("Failed to parse elapsed time from line: {}", line);
                    elapsed = 0;
                }
            }
            
            // Determine success status
            boolean success = line.contains("successfully") || !line.contains("failed");
            
            // Use current timestamp (JMeter output doesn't include absolute timestamps)
            long timestamp = System.currentTimeMillis();
            
            // Create and return SipMessage
            return new SipMessage(
                messageType,
                direction,
                threadName,
                timestamp,
                elapsed,
                success,
                success ? "200" : "500", // Response code
                label
            );
        }
        
        return null;
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
    
    // ============ TRAFFIC GENERATION ENGINE (Phase 3) ============
    
    /**
     * Executes a demo as a traffic generation run with controlled failure injection.
     * Streams real-time statistics to the provided callback for live UI updates.
     * Handles high-volume calls (100K+) efficiently.
     * 
     * @param demo The demo to execute as traffic generation
     * @param profile Traffic generation profile with volume and failure parameters
     * @param statsCallback Consumer that receives TrafficStats updates (invoked every second)
     * @return RunResult with execution metadata
     */
    public RunResult executeTrafficGeneration(Demo demo, TrafficProfile profile, Consumer<TrafficStats> statsCallback) {
        String runId = UUID.randomUUID().toString();
        RunResult result = new RunResult(runId, demo.getId(), demo.getTitle());
        
        // Validate JMX file exists
        File jmxFile = new File(demo.getJmxPath());
        if (!jmxFile.exists()) {
            String errorMsg = "JMX file not found: " + demo.getJmxPath();
            result.fail(errorMsg);
            logger.error("Traffic generation pre-flight check failed: {}", errorMsg);
            return result;
        }
        
        // Generate log file path
        String logFilePath = generateLogFilePath("traffic_" + demo.getId());
        result.setLogFilePath(logFilePath);
        
        // Initialize traffic statistics
        TrafficStats stats = new TrafficStats(runId, profile);
        
        try {
            // Copy JMX to TTS bin directory
            String jmxPathForExecution = copyJmxToTtsBin(jmxFile, runId);
            logger.info("Starting traffic generation: {} (runId: {})", profile.getProfileName(), runId);
            logger.info("Profile: {} concurrent calls, {} total calls, {}% failure rate at {}",
                profile.getConcurrentCalls(), profile.getTotalCalls(), profile.getFailureRate(),
                profile.getFailureNode().getDisplayName());
            
            // Build JMeter command with traffic profile parameters
            List<String> command = buildTrafficGenerationCommand(jmxPathForExecution, logFilePath, profile);
            
            logger.debug("Command: {}", String.join(" ", command));
            
            // Start process
            ProcessBuilder pb = new ProcessBuilder(command);
            pb.directory(new File(JMETER_BIN_DIR));
            pb.redirectErrorStream(true);
            pb.environment().put("JMETER_HOME", JMETER_HOME);
            
            stopTrafficGeneration = false;
            trafficProcess = pb.start();
            
            // Stream output in background
            new Thread(() -> streamTrafficOutput(trafficProcess), "Traffic-Output-Stream").start();
            
            // Start JTL stats parser thread
            Thread statsThread = new Thread(() -> parseTrafficStats(logFilePath, stats, statsCallback, trafficProcess),
                "Traffic-Stats-Parser");
            statsThread.setDaemon(true);
            statsThread.start();
            
            // Wait for completion or stop signal
            boolean finished = false;
            while (!finished && !stopTrafficGeneration) {
                finished = trafficProcess.waitFor(1, TimeUnit.SECONDS);
            }
            
            if (stopTrafficGeneration) {
                trafficProcess.destroyForcibly();
                result.fail("Traffic generation stopped by user");
                logger.info("Traffic generation stopped by user");
            } else {
                int exitCode = trafficProcess.exitValue();
                result.complete(exitCode);
                logger.info("Traffic generation completed: {} (exit code: {})", profile.getProfileName(), exitCode);
            }
            
            // Mark stats as complete
            stats.markComplete();
            
            // Send final stats update
            if (statsCallback != null) {
                statsCallback.accept(stats);
            }
            
            logger.info("Traffic generation summary: {}", stats.toString());
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            result.fail("Execution interrupted");
            logger.error("Traffic generation interrupted", e);
        } catch (Exception e) {
            result.fail("Execution error: " + e.getMessage());
            logger.error("Traffic generation failed", e);
        } finally {
            trafficProcess = null;
            stopTrafficGeneration = false;
            cleanupTempJmxFile();
            configManager.saveRunResult(result);
        }
        
        return result;
    }
    
    /**
     * Stops the currently running traffic generation.
     */
    public void stopTrafficGeneration() {
        if (trafficProcess != null && trafficProcess.isAlive()) {
            logger.info("Stopping traffic generation");
            stopTrafficGeneration = true;
            trafficProcess.destroyForcibly();
        }
    }
    
    /**
     * Checks if traffic generation is currently running.
     */
    public boolean isTrafficGenerationRunning() {
        return trafficProcess != null && trafficProcess.isAlive();
    }
    
    /**
     * Builds JMeter command for traffic generation with TrafficProfile parameters.
     */
    private List<String> buildTrafficGenerationCommand(String jmxPath, String logPath, TrafficProfile profile) {
        List<String> command = new ArrayList<>();
        command.add(JMETER_CMD);
        command.add("-n");
        command.add("-t");
        command.add(jmxPath);
        command.add("-l");
        command.add(logPath);
        
        // Enable auto-flush for real-time stats
        command.add("-Jjmeter.save.saveservice.autoflush=true");
        
        // Add traffic profile parameters as JMeter properties
        for (var entry : profile.toJMeterProperties().entrySet()) {
            command.add("-J" + entry.getKey() + "=" + entry.getValue());
        }
        
        logger.debug("Traffic profile JMeter properties: {}", profile.toJMeterProperties());
        
        return command;
    }
    
    /**
     * Stream traffic generation output (simplified - no detailed parsing).
     */
    private void streamTrafficOutput(Process process) {
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                // Log important lines
                if (line.contains("summary =") || line.contains("ERROR") || line.contains("WARN")) {
                    logger.info("[TRAFFIC] {}", line);
                }
                logger.debug("[TRAFFIC-OUTPUT] {}", line);
            }
        } catch (IOException e) {
            logger.error("Error streaming traffic output", e);
        }
    }
    
    /**
     * Parse JTL file for traffic statistics in real-time.
     * Efficiently handles high-volume calls (100K+) by only extracting stats, not full SipMessage objects.
     * Invokes statsCallback every second with updated statistics.
     */
    private void parseTrafficStats(String jtlFilePath, TrafficStats stats, 
                                   Consumer<TrafficStats> statsCallback, Process process) {
        File jtlFile = new File(jtlFilePath);
        long lastPosition = 0;
        boolean headerSkipped = false;
        long lastCallbackTime = System.currentTimeMillis();
        
        logger.info("[TRAFFIC-STATS] Starting stats parser for: {}", jtlFilePath);
        
        // Wait for JTL file creation
        int waitAttempts = 0;
        while (!jtlFile.exists() && process.isAlive() && waitAttempts < 150) {
            try {
                Thread.sleep(100);
                waitAttempts++;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
        }
        
        if (!jtlFile.exists()) {
            logger.warn("[TRAFFIC-STATS] JTL file not created after 15 seconds");
            return;
        }
        
        logger.info("[TRAFFIC-STATS] JTL file detected, starting stats collection");
        
        // Parse JTL file continuously
        while (process.isAlive() || jtlFile.length() > lastPosition) {
            try {
                if (jtlFile.length() > lastPosition) {
                    try (RandomAccessFile raf = new RandomAccessFile(jtlFile, "r")) {
                        raf.seek(lastPosition);
                        String line;
                        
                        while ((line = raf.readLine()) != null) {
                            // Skip CSV header
                            if (!headerSkipped) {
                                headerSkipped = true;
                                lastPosition = raf.getFilePointer();
                                continue;
                            }
                            
                            // Parse and record stats
                            parseAndRecordStats(line, stats);
                            
                            lastPosition = raf.getFilePointer();
                        }
                    } catch (IOException e) {
                        logger.error("[TRAFFIC-STATS] Error reading JTL file", e);
                    }
                }
                
                // Invoke callback every second
                long now = System.currentTimeMillis();
                if (statsCallback != null && (now - lastCallbackTime) >= 1000) {
                    statsCallback.accept(stats);
                    lastCallbackTime = now;
                    logger.debug("[TRAFFIC-STATS] Stats update: {}", stats.toString());
                }
                
                // Short sleep to avoid busy-waiting
                Thread.sleep(100);
                
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        // Final stats update
        if (statsCallback != null) {
            stats.markComplete();
            statsCallback.accept(stats);
        }
        
        logger.info("[TRAFFIC-STATS] Stats parser completed. Final: {}", stats.toString());
    }
    
    /**
     * Parse a single JTL line and record statistics.
     * Lightweight parsing - only extracts essential data for stats.
     */
    private void parseAndRecordStats(String line, TrafficStats stats) {
        if (line == null || line.trim().isEmpty()) {
            return;
        }
        
        String[] fields = line.split(",");
        if (fields.length < 8) {
            return;
        }
        
        try {
            long elapsed = Long.parseLong(fields[1].trim());
            String label = fields[2].trim();
            String responseCode = fields[3].trim();
            boolean success = Boolean.parseBoolean(fields[7].trim());
            
            // Skip non-call samplers
            if (shouldSkipLabel(label)) {
                return;
            }
            
            // Extract node from label
            ActorType node = extractFailedNode(label);
            
            // Record attempt with node tracking
            stats.recordAttempt(node);
            
            if (success) {
                stats.recordSuccess(node, elapsed);
            } else {
                // Determine failure type from response code
                FailureType failureType = determineFailureType(responseCode);
                stats.recordFailure(failureType.getDisplayName(), node, responseCode, elapsed);
            }
            
        } catch (Exception e) {
            logger.debug("[TRAFFIC-STATS] Failed to parse line: {} - Error: {}", line, e.getMessage());
        }
    }
    
    /**
     * Determine failure type from response code.
     */
    private FailureType determineFailureType(String responseCode) {
        if (responseCode == null || responseCode.isEmpty()) {
            return FailureType.UNKNOWN;
        }
        
        String code = responseCode.trim();
        
        if (code.startsWith("4")) {
            if (code.equals("401") || code.equals("403")) {
                return FailureType.AUTHENTICATION_FAILURE;
            } else if (code.equals("408")) {
                return FailureType.TIMEOUT;
            } else if (code.equals("400")) {
                return FailureType.PROTOCOL_ERROR;
            } else {
                return FailureType.REJECTION_4XX;
            }
        } else if (code.startsWith("5")) {
            return FailureType.REJECTION_5XX;
        } else if (code.startsWith("6")) {
            return FailureType.REJECTION_5XX; // Treat 6xx as server errors
        } else {
            return FailureType.UNKNOWN;
        }
    }
    
    /**
     * Extract failed node from label (simplified extraction).
     */
    private ActorType extractFailedNode(String label) {
        if (label == null) {
            return ActorType.UNKNOWN;
        }
        
        // Try to extract from label patterns
        return ActorType.fromLabel(label);
    }
}
