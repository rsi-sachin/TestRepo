package com.tts.demo.service;

import com.tts.demo.model.Demo;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests to verify that all JMX file paths in demos.json reference actual files
 * in the C:\TTS installation directory.
 * 
 * PURPOSE: Catch configuration errors early before demos fail at runtime.
 */
@DisplayName("Demo Catalog - JMX File Validation Tests")
class DemoCatalogFileValidationTest {

    private DemoCatalog catalog;
    private List<String> missingFiles;
    private List<String> validFiles;

    @BeforeEach
    void setUp() {
        catalog = new DemoCatalog();
        missingFiles = new ArrayList<>();
        validFiles = new ArrayList<>();
    }

    @Test
    @DisplayName("TEST-001: All demo JMX files should exist on filesystem")
    void allDemoJmxFilesShouldExist() {
        List<Demo> allDemos = catalog.getAllDemos();
        
        for (Demo demo : allDemos) {
            String jmxPath = demo.getJmxPath();
            File jmxFile = new File(jmxPath);
            
            if (jmxFile.exists()) {
                validFiles.add(String.format("%s -> %s", demo.getId(), jmxPath));
            } else {
                missingFiles.add(String.format("%s -> %s", demo.getId(), jmxPath));
            }
        }
        
        // Print results
        System.out.println("\n=== JMX File Validation Results ===");
        System.out.println("✓ Valid files: " + validFiles.size());
        validFiles.forEach(f -> System.out.println("  ✓ " + f));
        
        System.out.println("\n✗ Missing files: " + missingFiles.size());
        missingFiles.forEach(f -> System.out.println("  ✗ " + f));
        
        // Assert: All files must exist
        assertTrue(missingFiles.isEmpty(), 
                "Found " + missingFiles.size() + " demos with missing JMX files: " + missingFiles);
    }

    @Test
    @DisplayName("TEST-002: All JMX paths should use C:\\TTS base directory")
    void allJmxPathsShouldUseTTSDirectory() {
        List<Demo> allDemos = catalog.getAllDemos();
        List<String> wrongBasePath = new ArrayList<>();
        
        for (Demo demo : allDemos) {
            String jmxPath = demo.getJmxPath();
            if (!jmxPath.startsWith("C:\\TTS\\")) {
                wrongBasePath.add(String.format("%s -> %s", demo.getId(), jmxPath));
            }
        }
        
        assertTrue(wrongBasePath.isEmpty(), 
                "Found demos not using C:\\TTS base path: " + wrongBasePath);
    }

    @Test
    @DisplayName("TEST-003: JMX files should be readable")
    void jmxFilesShouldBeReadable() {
        List<Demo> allDemos = catalog.getAllDemos();
        List<String> unreadableFiles = new ArrayList<>();
        
        for (Demo demo : allDemos) {
            Path jmxPath = Paths.get(demo.getJmxPath());
            if (Files.exists(jmxPath) && !Files.isReadable(jmxPath)) {
                unreadableFiles.add(String.format("%s -> %s", demo.getId(), jmxPath));
            }
        }
        
        assertTrue(unreadableFiles.isEmpty(), 
                "Found JMX files that are not readable: " + unreadableFiles);
    }

    @Test
    @DisplayName("TEST-004: JMX files should have .jmx extension")
    void jmxFilesShouldHaveCorrectExtension() {
        List<Demo> allDemos = catalog.getAllDemos();
        List<String> wrongExtension = new ArrayList<>();
        
        for (Demo demo : allDemos) {
            String jmxPath = demo.getJmxPath();
            if (!jmxPath.toLowerCase().endsWith(".jmx")) {
                wrongExtension.add(String.format("%s -> %s", demo.getId(), jmxPath));
            }
        }
        
        assertTrue(wrongExtension.isEmpty(), 
                "Found demos with non-.jmx file extensions: " + wrongExtension);
    }

    @Test
    @DisplayName("TEST-005: SIP demos should reference C:\\TTS\\docs\\sip\\reference_tests")
    void sipDemosShouldReferenceCorrectDirectory() {
        List<Demo> sipDemos = catalog.getDemosByProtocol(Demo.Protocol.SIP_IMS);
        List<String> wrongDirectory = new ArrayList<>();
        
        for (Demo demo : sipDemos) {
            String jmxPath = demo.getJmxPath();
            if (!jmxPath.contains("\\docs\\sip\\reference_tests\\")) {
                wrongDirectory.add(String.format("%s -> %s", demo.getId(), jmxPath));
            }
        }
        
        assertTrue(wrongDirectory.isEmpty(), 
                "Found SIP demos not using expected directory: " + wrongDirectory);
    }

    @Test
    @DisplayName("TEST-006: Diameter demos should use either templates or reference_tests")
    void diameterDemosShouldUseExpectedDirectories() {
        List<Demo> diameterDemos = catalog.getDemosByProtocol(Demo.Protocol.DIAMETER);
        List<String> unexpectedDirectory = new ArrayList<>();
        
        for (Demo demo : diameterDemos) {
            String jmxPath = demo.getJmxPath();
            boolean usesTemplates = jmxPath.contains("\\bin\\templates\\tts\\");
            boolean usesReferenceTests = jmxPath.contains("\\docs\\diameter\\reference_tests\\");
            
            if (!usesTemplates && !usesReferenceTests) {
                unexpectedDirectory.add(String.format("%s -> %s", demo.getId(), jmxPath));
            }
        }
        
        assertTrue(unexpectedDirectory.isEmpty(), 
                "Found Diameter demos not using expected directories: " + unexpectedDirectory);
    }

    @Test
    @DisplayName("TEST-007: RADIUS demos should use either templates or reference_tests")
    void radiusDemosShouldUseExpectedDirectories() {
        List<Demo> radiusDemos = catalog.getDemosByProtocol(Demo.Protocol.RADIUS);
        List<String> unexpectedDirectory = new ArrayList<>();
        
        for (Demo demo : radiusDemos) {
            String jmxPath = demo.getJmxPath();
            boolean usesTemplates = jmxPath.contains("\\bin\\templates\\tts\\");
            boolean usesReferenceTests = jmxPath.contains("\\docs\\radius_client\\reference_tests\\");
            
            if (!usesTemplates && !usesReferenceTests) {
                unexpectedDirectory.add(String.format("%s -> %s", demo.getId(), jmxPath));
            }
        }
        
        assertTrue(unexpectedDirectory.isEmpty(), 
                "Found RADIUS demos not using expected directories: " + unexpectedDirectory);
    }

    @Test
    @DisplayName("TEST-008: No duplicate JMX paths across demos")
    void noDuplicateJmxPaths() {
        List<Demo> allDemos = catalog.getAllDemos();
        List<String> seenPaths = new ArrayList<>();
        List<String> duplicates = new ArrayList<>();
        
        for (Demo demo : allDemos) {
            String jmxPath = demo.getJmxPath();
            if (seenPaths.contains(jmxPath)) {
                duplicates.add(String.format("%s -> %s", demo.getId(), jmxPath));
            } else {
                seenPaths.add(jmxPath);
            }
        }
        
        assertTrue(duplicates.isEmpty(), 
                "Found demos sharing the same JMX file: " + duplicates);
    }

    @Test
    @DisplayName("TEST-009: JMX paths should use backslash separators (Windows)")
    void jmxPathsShouldUseWindowsSeparators() {
        List<Demo> allDemos = catalog.getAllDemos();
        List<String> wrongSeparator = new ArrayList<>();
        
        for (Demo demo : allDemos) {
            String jmxPath = demo.getJmxPath();
            if (jmxPath.contains("/")) {
                wrongSeparator.add(String.format("%s -> %s", demo.getId(), jmxPath));
            }
        }
        
        assertTrue(wrongSeparator.isEmpty(), 
                "Found demos using forward slashes in paths: " + wrongSeparator);
    }

    @Test
    @DisplayName("TEST-010: Catalog should load minimum number of demos")
    void catalogShouldLoadMinimumDemos() {
        List<Demo> allDemos = catalog.getAllDemos();
        assertTrue(allDemos.size() >= 10, 
                "Expected at least 10 demos, found: " + allDemos.size());
    }
}
