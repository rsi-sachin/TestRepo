package com.tts.demo.service;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import com.tts.demo.model.Demo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.lang.reflect.Type;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Manages the catalog of demo scenarios.
 * Loads demos from JSON file and provides filtering/search capabilities.
 */
public class DemoCatalog {
    
    private static final Logger logger = LoggerFactory.getLogger(DemoCatalog.class);
    private static final String DEMOS_JSON_PATH = "/data/demos.json";
    
    private final List<Demo> demos;
    private final Map<String, Demo> demoIndex;
    private final Gson gson;

    public DemoCatalog() {
        this.gson = new GsonBuilder().setPrettyPrinting().create();
        this.demos = new ArrayList<>();
        this.demoIndex = new HashMap<>();
        loadDemos();
    }

    /**
     * Loads demo scenarios from the JSON catalog file.
     */
    private void loadDemos() {
        try (InputStream is = getClass().getResourceAsStream(DEMOS_JSON_PATH)) {
            if (is == null) {
                logger.error("Demos catalog not found: {}", DEMOS_JSON_PATH);
                return;
            }

            try (Reader reader = new InputStreamReader(is)) {
                Type catalogType = new TypeToken<Map<String, List<Demo>>>(){}.getType();
                Map<String, List<Demo>> catalog = gson.fromJson(reader, catalogType);
                
                if (catalog != null && catalog.containsKey("demos")) {
                    List<Demo> loadedDemos = catalog.get("demos");
                    demos.addAll(loadedDemos);
                    
                    // Build index for fast lookup
                    for (Demo demo : loadedDemos) {
                        demoIndex.put(demo.getId(), demo);
                    }
                    
                    logger.info("Loaded {} demos from catalog", demos.size());
                    
                    // Validate that JMX files exist
                    validateDemoFiles();
                } else {
                    logger.warn("No demos found in catalog");
                }
            }
        } catch (IOException e) {
            logger.error("Failed to load demos catalog", e);
        }
    }

    /**
     * Validates that JMX files referenced by demos actually exist.
     * Logs warnings for missing files but does not prevent catalog loading.
     */
    private void validateDemoFiles() {
        int missingCount = 0;
        for (Demo demo : demos) {
            java.io.File jmxFile = new java.io.File(demo.getJmxPath());
            if (!jmxFile.exists()) {
                logger.warn("Demo '{}' (id: {}) references missing JMX file: {}", 
                           demo.getTitle(), demo.getId(), demo.getJmxPath());
                missingCount++;
            }
        }
        
        if (missingCount > 0) {
            logger.warn("Found {} demo(s) with missing JMX files. These demos will fail at runtime.", 
                       missingCount);
        } else {
            logger.info("All demo JMX files validated successfully");
        }
    }

    /**
     * Returns all available demos.
     */
    public List<Demo> getAllDemos() {
        return new ArrayList<>(demos);
    }

    /**
     * Finds a demo by its ID.
     * @return Demo if found, null otherwise
     */
    public Demo getDemoById(String id) {
        return demoIndex.get(id);
    }

    /**
     * Filters demos by protocol.
     */
    public List<Demo> getDemosByProtocol(Demo.Protocol protocol) {
        return demos.stream()
                .filter(d -> d.getProtocol() == protocol)
                .collect(Collectors.toList());
    }

    /**
     * Filters demos by complexity level.
     */
    public List<Demo> getDemosByComplexity(Demo.Complexity complexity) {
        return demos.stream()
                .filter(d -> d.getComplexity() == complexity)
                .collect(Collectors.toList());
    }

    /**
     * Searches demos by text in title or description.
     * Case-insensitive search.
     */
    public List<Demo> searchDemos(String searchText) {
        if (searchText == null || searchText.trim().isEmpty()) {
            return getAllDemos();
        }
        
        String lowerSearch = searchText.toLowerCase();
        return demos.stream()
                .filter(d -> d.getTitle().toLowerCase().contains(lowerSearch) ||
                            d.getDescription().toLowerCase().contains(lowerSearch))
                .collect(Collectors.toList());
    }

    /**
     * Returns all available protocols in the catalog.
     */
    public Set<Demo.Protocol> getAvailableProtocols() {
        return demos.stream()
                .map(Demo::getProtocol)
                .collect(Collectors.toSet());
    }

    /**
     * Returns all available complexity levels in the catalog.
     */
    public Set<Demo.Complexity> getAvailableComplexityLevels() {
        return demos.stream()
                .map(Demo::getComplexity)
                .collect(Collectors.toSet());
    }

    /**
     * Returns the total count of demos in the catalog.
     */
    public int getDemoCount() {
        return demos.size();
    }

    /**
     * Checks if the catalog is empty.
     */
    public boolean isEmpty() {
        return demos.isEmpty();
    }
}
