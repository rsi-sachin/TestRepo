package com.tts.demo.model;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

/**
 * Configuration for demo execution.
 * Holds runtime parameters that can be customized before running a demo.
 */
public class DemoConfig {
    
    private String demoId;
    private Map<String, String> parameters;

    public DemoConfig() {
        this.parameters = new HashMap<>();
    }

    public DemoConfig(String demoId) {
        this.demoId = demoId;
        this.parameters = new HashMap<>();
    }

    public DemoConfig(String demoId, Map<String, String> parameters) {
        this.demoId = demoId;
        this.parameters = new HashMap<>(parameters);
    }

    /**
     * Sets a parameter value.
     */
    public void setParameter(String key, String value) {
        parameters.put(key, value);
    }

    /**
     * Gets a parameter value, returning null if not found.
     */
    public String getParameter(String key) {
        return parameters.get(key);
    }

    /**
     * Gets a parameter value with a default fallback.
     */
    public String getParameter(String key, String defaultValue) {
        return parameters.getOrDefault(key, defaultValue);
    }

    /**
     * Checks if a parameter exists.
     */
    public boolean hasParameter(String key) {
        return parameters.containsKey(key);
    }

    /**
     * Merges default parameters with configured parameters.
     * Configured parameters take precedence.
     */
    public void mergeDefaults(Map<String, String> defaults) {
        if (defaults != null) {
            defaults.forEach(parameters::putIfAbsent);
        }
    }

    /**
     * Builds JMeter command-line arguments from parameters.
     * Format: -Jkey=value
     */
    public String[] toJMeterArgs() {
        return parameters.entrySet().stream()
                .map(e -> "-J" + e.getKey() + "=" + e.getValue())
                .toArray(String[]::new);
    }

    // Getters and Setters
    public String getDemoId() {
        return demoId;
    }

    public void setDemoId(String demoId) {
        this.demoId = demoId;
    }

    public Map<String, String> getParameters() {
        return new HashMap<>(parameters);
    }

    public void setParameters(Map<String, String> parameters) {
        this.parameters = new HashMap<>(parameters);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DemoConfig that = (DemoConfig) o;
        return Objects.equals(demoId, that.demoId) &&
                Objects.equals(parameters, that.parameters);
    }

    @Override
    public int hashCode() {
        return Objects.hash(demoId, parameters);
    }

    @Override
    public String toString() {
        return "DemoConfig{" +
                "demoId='" + demoId + '\'' +
                ", parameters=" + parameters +
                '}';
    }
}
