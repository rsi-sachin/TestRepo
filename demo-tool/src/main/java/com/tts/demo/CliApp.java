package com.tts.demo;

import com.tts.demo.model.Demo;
import com.tts.demo.model.DemoConfig;
import com.tts.demo.model.RunResult;
import com.tts.demo.service.ConfigManager;
import com.tts.demo.service.DemoCatalog;
import com.tts.demo.service.DemoRunner;
import org.apache.commons.cli.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

/**
 * Command-line interface for running TTS demos programmatically.
 * 
 * Provides automated test execution capabilities for CI/CD integration
 * and scripted workflows without GUI dependency.
 * 
 * Exit codes:
 * - 0: Demo executed successfully
 * - 1: Demo failed (JMeter exit code non-zero)
 * - 2: CLI error (invalid arguments, demo not found, exception)
 */
public class CliApp {
    
    private static final Logger logger = LoggerFactory.getLogger(CliApp.class);
    private static final String APP_NAME = "tts-demo-tool";
    private static final int EXIT_SUCCESS = 0;
    private static final int EXIT_DEMO_FAILED = 1;
    private static final int EXIT_CLI_ERROR = 2;
    
    // Static block to prevent JavaFX auto-initialization
    static {
        // Set headless mode if JavaFX is not explicitly needed
        // This prevents JavaFX Platform from auto-starting
        System.setProperty("java.awt.headless", "true");
        System.setProperty("prism.order", "sw"); // Software rendering only
        System.setProperty("prism.verbose", "false");
    }
    
    public static void main(String[] args) {
        try {
            // Parse command-line arguments
            Options options = buildOptions();
            CommandLineParser parser = new DefaultParser();
            CommandLine cmd = parser.parse(options, args);
            
            // Handle help
            if (cmd.hasOption("help") || args.length == 0) {
                printHelp(options);
                cleanupAndExit(EXIT_SUCCESS);
            }
            
            // Initialize services
            DemoCatalog catalog = new DemoCatalog();
            ConfigManager configManager = new ConfigManager("runs");
            DemoRunner runner = new DemoRunner(configManager);
            
            // Setup shutdown hook for graceful termination (capture runner in closure)
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                logger.info("Shutdown signal received, stopping demo execution");
                runner.stopCurrentDemo();
                shutdownJavaFxIfRunning();
            }));
            
            // Handle list command
            if (cmd.hasOption("list")) {
                listDemos(catalog);
                cleanupAndExit(EXIT_SUCCESS);
            }
            
            // Handle demo execution
            if (cmd.hasOption("demo")) {
                String demoId = cmd.getOptionValue("demo");
                boolean verbose = cmd.hasOption("verbose");
                
                // Configure logging based on verbosity
                if (!verbose) {
                    // Suppress DEBUG logs for cleaner output
                    ch.qos.logback.classic.Logger root = 
                        (ch.qos.logback.classic.Logger) LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME);
                    root.setLevel(ch.qos.logback.classic.Level.INFO);
                }
                
                int exitCode = executeDemoFromCli(demoId, cmd, catalog, runner, configManager, verbose);
                cleanupAndExit(exitCode);
            }
            
            // No valid command provided
            System.err.println("Error: No valid command provided. Use --help for usage information.");
            cleanupAndExit(EXIT_CLI_ERROR);
            
        } catch (ParseException e) {
            System.err.println("Error parsing arguments: " + e.getMessage());
            System.err.println("Use --help for usage information.");
            cleanupAndExit(EXIT_CLI_ERROR);
        } catch (Exception e) {
            logger.error("Unexpected error in CLI", e);
            System.err.println("Error: " + e.getMessage());
            cleanupAndExit(EXIT_CLI_ERROR);
        }
    }
    
    /**
     * Shutdown JavaFX Platform if it was inadvertently initialized.
     * Uses reflection to avoid compile-time dependency on JavaFX.
     */
    private static void shutdownJavaFxIfRunning() {
        try {
            Class<?> platformClass = Class.forName("javafx.application.Platform");
            
            // Check if Platform is running
            java.lang.reflect.Method isImplicitExitMethod = platformClass.getMethod("isImplicitExit");
            java.lang.reflect.Method exitMethod = platformClass.getMethod("exit");
            
            // If JavaFX Platform exists and is accessible, shut it down
            logger.debug("JavaFX Platform detected, shutting down...");
            exitMethod.invoke(null);
            
            // Give it a moment to clean up
            Thread.sleep(100);
            
        } catch (ClassNotFoundException e) {
            // JavaFX not on classpath or not initialized - this is fine
            logger.debug("JavaFX Platform not found (expected for CLI)");
        } catch (Exception e) {
            // JavaFX might not be running or already shut down - this is fine
            logger.debug("JavaFX Platform shutdown skipped: {}", e.getMessage());
        }
    }
    
    /**
     * Cleanup and exit with the specified code.
     * Ensures JavaFX Platform is shut down if it was started.
     */
    private static void cleanupAndExit(int exitCode) {
        shutdownJavaFxIfRunning();
        System.exit(exitCode);
    }
    
    /**
     * Builds CLI options.
     */
    private static Options buildOptions() {
        Options options = new Options();
        
        options.addOption(Option.builder("d")
                .longOpt("demo")
                .desc("Demo ID to execute (e.g., sip-001)")
                .hasArg()
                .argName("ID")
                .build());
        
        options.addOption(Option.builder("p")
                .longOpt("param")
                .desc("Override demo parameter (format: key=value, repeatable)")
                .hasArgs()
                .argName("KEY=VALUE")
                .build());
        
        options.addOption(Option.builder("l")
                .longOpt("list")
                .desc("List all available demos")
                .build());
        
        options.addOption(Option.builder("v")
                .longOpt("verbose")
                .desc("Enable verbose output (includes DEBUG logs)")
                .build());
        
        options.addOption(Option.builder("h")
                .longOpt("help")
                .desc("Show usage information")
                .build());
        
        return options;
    }
    
    /**
     * Prints help message.
     */
    private static void printHelp(Options options) {
        HelpFormatter formatter = new HelpFormatter();
        formatter.setWidth(100);
        
        System.out.println("TTS Demo Tool - Command Line Interface");
        System.out.println("=======================================");
        System.out.println();
        
        formatter.printHelp(APP_NAME, options, true);
        
        System.out.println();
        System.out.println("Examples:");
        System.out.println("  " + APP_NAME + " --list");
        System.out.println("      List all available demos");
        System.out.println();
        System.out.println("  " + APP_NAME + " --demo sip-001");
        System.out.println("      Run VoLTE Call Setup & Teardown demo");
        System.out.println();
        System.out.println("  " + APP_NAME + " --demo sip-001 --param threads=2 --param loops=5");
        System.out.println("      Run demo with custom parameters");
        System.out.println();
        System.out.println("  " + APP_NAME + " --demo sip-001 --verbose");
        System.out.println("      Run demo with verbose logging");
        System.out.println();
        System.out.println("Exit Codes:");
        System.out.println("  0 - Demo executed successfully");
        System.out.println("  1 - Demo failed (JMeter reported failure)");
        System.out.println("  2 - CLI error (invalid arguments, demo not found, etc.)");
        System.out.println();
        System.out.println("For GUI mode, use: mvn javafx:run");
    }
    
    /**
     * Lists all available demos in table format.
     */
    private static void listDemos(DemoCatalog catalog) {
        List<Demo> demos = catalog.getAllDemos();
        
        System.out.println();
        System.out.println("Available Demos");
        System.out.println("===============");
        System.out.println();
        
        // Print table header
        String headerFormat = "%-15s %-50s %-12s %-12s%n";
        String rowFormat = "%-15s %-50s %-12s %-12s%n";
        
        System.out.printf(headerFormat, "ID", "Title", "Protocol", "Complexity");
        System.out.println("─".repeat(89));
        
        // Print demos
        for (Demo demo : demos) {
            System.out.printf(rowFormat, 
                demo.getId(),
                truncate(demo.getTitle(), 50),
                demo.getProtocol(),
                demo.getComplexity()
            );
        }
        
        System.out.println();
        System.out.println("Total: " + demos.size() + " demos");
        System.out.println();
        System.out.println("Run a demo with: " + APP_NAME + " --demo <ID>");
    }
    
    /**
     * Executes a demo from CLI arguments.
     */
    private static int executeDemoFromCli(String demoId, CommandLine cmd, 
                                         DemoCatalog catalog, DemoRunner runner,
                                         ConfigManager configManager, boolean verbose) {
        try {
            // Load demo
            Demo demo = catalog.getDemoById(demoId);
            if (demo == null) {
                System.err.println("Error: Demo not found: " + demoId);
                System.err.println("Use --list to see available demos.");
                return EXIT_CLI_ERROR;
            }
            
            // Print demo info
            System.out.println();
            System.out.println("═".repeat(80));
            System.out.println("  TTS Demo Execution");
            System.out.println("═".repeat(80));
            System.out.println();
            System.out.println("Demo:        " + demo.getTitle());
            System.out.println("ID:          " + demo.getId());
            System.out.println("Protocol:    " + demo.getProtocol());
            System.out.println("Complexity:  " + demo.getComplexity());
            System.out.println();
            System.out.println("Description: " + demo.getDescription());
            System.out.println();
            System.out.println("Expected Outcome:");
            System.out.println("  " + demo.getExpectedOutcome());
            System.out.println();
            System.out.println("─".repeat(80));
            
            // Create config with CLI parameters
            DemoConfig config = new DemoConfig(demoId);
            
            // Apply custom parameters from command line
            if (cmd.hasOption("param")) {
                String[] params = cmd.getOptionValues("param");
                System.out.println("Custom Parameters:");
                for (String param : params) {
                    String[] parts = param.split("=", 2);
                    if (parts.length == 2) {
                        String key = parts[0].trim();
                        String value = parts[1].trim();
                        config.setParameter(key, value);
                        System.out.println("  " + key + " = " + value);
                    } else {
                        System.err.println("Warning: Invalid parameter format (ignored): " + param);
                    }
                }
                System.out.println("─".repeat(80));
            }
            
            System.out.println();
            System.out.println("Starting execution...");
            System.out.println();
            
            // Execute demo with output streaming to console
            RunResult result = runner.runDemo(demo, config, line -> {
                if (verbose || !line.contains("DEBUG")) {
                    System.out.println(line);
                }
            });
            
            // Print result summary
            System.out.println();
            System.out.println("═".repeat(80));
            System.out.println("  Execution Result");
            System.out.println("═".repeat(80));
            System.out.println();
            System.out.println("Status:      " + result.getStatus());
            System.out.println("Duration:    " + result.getDurationSeconds() + " seconds");
            System.out.println("Exit Code:   " + result.getExitCode());
            System.out.println("Run ID:      " + result.getRunId());
            
            if (result.getOutputSnapshot() != null && !result.getOutputSnapshot().isEmpty()) {
                System.out.println();
                System.out.println("Error Message:");
                System.out.println("  " + result.getOutputSnapshot());
            }
            
            System.out.println();
            System.out.println("Run history saved to: runs/run_" + 
                result.getStartTime().format(java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")) + 
                "_" + demoId + ".json");
            System.out.println("═".repeat(80));
            System.out.println();
            
            // Return appropriate exit code
            if (result.getStatus() == RunResult.RunStatus.SUCCESS) {
                System.out.println("✓ Demo completed successfully");
                return EXIT_SUCCESS;
            } else {
                System.err.println("✗ Demo failed");
                return EXIT_DEMO_FAILED;
            }
            
        } catch (Exception e) {
            logger.error("Error executing demo: " + demoId, e);
            System.err.println();
            System.err.println("Error executing demo: " + e.getMessage());
            return EXIT_CLI_ERROR;
        }
    }
    
    /**
     * Truncates string to specified length with ellipsis.
     */
    private static String truncate(String str, int maxLength) {
        if (str.length() <= maxLength) {
            return str;
        }
        return str.substring(0, maxLength - 3) + "...";
    }
}
