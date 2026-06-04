package com.tts.demo.service;

import com.tts.demo.model.CallFlow;
import com.tts.demo.model.SipMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

/**
 * Parses JMeter JTL (CSV) files to extract SIP call flow messages.
 * Converts raw test results into structured CallFlow objects for visualization.
 */
public class JtlParser {
    
    private static final Logger logger = LoggerFactory.getLogger(JtlParser.class);
    
    /**
     * Parse a JTL file and extract SIP call flow
     * 
     * @param filePath Path to the JTL file (absolute or relative)
     * @return CallFlow object containing all parsed SIP messages
     * @throws IOException if file cannot be read
     */
    public CallFlow parseJtlFile(String filePath) throws IOException {
        Path path = Paths.get(filePath);
        
        if (!Files.exists(path)) {
            logger.error("JTL file not found: {}", filePath);
            throw new IOException("JTL file not found: " + filePath);
        }
        
        logger.info("Parsing JTL file: {}", filePath);
        List<SipMessage> messages = new ArrayList<>();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(path.toFile()))) {
            String line;
            boolean isFirstLine = true;
            int lineNumber = 0;
            
            while ((line = reader.readLine()) != null) {
                lineNumber++;
                
                // Skip header line
                if (isFirstLine) {
                    isFirstLine = false;
                    continue;
                }
                
                // Skip empty lines
                if (line.trim().isEmpty()) {
                    continue;
                }
                
                try {
                    SipMessage message = parseLine(line);
                    if (message != null) {
                        messages.add(message);
                    }
                } catch (Exception e) {
                    logger.warn("Failed to parse line {}: {} - Error: {}", lineNumber, line, e.getMessage());
                }
            }
        }
        
        logger.info("Parsed {} SIP messages from JTL file", messages.size());
        return new CallFlow(messages);
    }
    
    /**
     * Parse a single CSV line from JTL file
     * 
     * JTL CSV format:
     * timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,...
     * 
     * @param line CSV line from JTL file
     * @return SipMessage object or null if line should be skipped
     */
    private SipMessage parseLine(String line) {
        String[] fields = parseCsvLine(line);
        
        if (fields.length < 8) {
            logger.warn("Line has insufficient fields: {}", line);
            return null;
        }
        
        try {
            long timestamp = Long.parseLong(fields[0].trim());
            long elapsed = Long.parseLong(fields[1].trim());
            String label = fields[2].trim();
            String responseCode = fields[3].trim();
            String threadName = fields[5].trim();
            boolean success = Boolean.parseBoolean(fields[7].trim());
            
            // Filter out non-SIP messages (timers, call ID generation, etc.)
            if (isNonSipMessage(label)) {
                return null;
            }
            
            // Determine message type and direction
            SipMessage.MessageType messageType = SipMessage.MessageType.fromLabel(label);
            SipMessage.Direction direction = SipMessage.Direction.fromThreadAndLabel(threadName, label);
            
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
            
        } catch (NumberFormatException e) {
            logger.warn("Failed to parse numeric field in line: {}", line);
            return null;
        }
    }
    
    /**
     * Parse CSV line handling quoted fields with commas
     * 
     * @param line CSV line
     * @return Array of field values
     */
    private String[] parseCsvLine(String line) {
        List<String> fields = new ArrayList<>();
        StringBuilder currentField = new StringBuilder();
        boolean inQuotes = false;
        
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            
            if (c == '"') {
                inQuotes = !inQuotes;
            } else if (c == ',' && !inQuotes) {
                fields.add(currentField.toString());
                currentField = new StringBuilder();
            } else {
                currentField.append(c);
            }
        }
        
        // Add last field
        fields.add(currentField.toString());
        
        return fields.toArray(new String[0]);
    }
    
    /**
     * Check if label indicates a non-SIP message that should be filtered out
     * 
     * @param label JTL label field
     * @return true if message should be skipped
     */
    private boolean isNonSipMessage(String label) {
        if (label == null || label.isEmpty()) {
            return true;
        }
        
        String lower = label.toLowerCase();
        
        // Filter out timers and utility messages
        return lower.contains("wait for") ||
               lower.contains("timer") ||
               lower.contains("generate") ||
               lower.contains("callid") ||
               lower.contains("delay");
    }
}
