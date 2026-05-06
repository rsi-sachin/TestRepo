package com.tts.demo.model;

import java.util.Map;
import java.util.Objects;

/**
 * Represents a demo scenario with business-level KPI framing.
 * Maps business scenarios to underlying JMX test execution.
 */
public class Demo {
    
    private String id;
    private String title;
    private String description;
    private String expectedOutcome;
    private Protocol protocol;
    private Complexity complexity;
    private String jmxPath;
    private Map<String, String> defaultParams;

    public Demo() {
    }

    public Demo(String id, String title, String description, String expectedOutcome,
                Protocol protocol, Complexity complexity, String jmxPath,
                Map<String, String> defaultParams) {
        this.id = id;
        this.title = title;
        this.description = description;
        this.expectedOutcome = expectedOutcome;
        this.protocol = protocol;
        this.complexity = complexity;
        this.jmxPath = jmxPath;
        this.defaultParams = defaultParams;
    }

    // Getters and Setters
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getExpectedOutcome() {
        return expectedOutcome;
    }

    public void setExpectedOutcome(String expectedOutcome) {
        this.expectedOutcome = expectedOutcome;
    }

    public Protocol getProtocol() {
        return protocol;
    }

    public void setProtocol(Protocol protocol) {
        this.protocol = protocol;
    }

    public Complexity getComplexity() {
        return complexity;
    }

    public void setComplexity(Complexity complexity) {
        this.complexity = complexity;
    }

    public String getJmxPath() {
        return jmxPath;
    }

    public void setJmxPath(String jmxPath) {
        this.jmxPath = jmxPath;
    }

    public Map<String, String> getDefaultParams() {
        return defaultParams;
    }

    public void setDefaultParams(Map<String, String> defaultParams) {
        this.defaultParams = defaultParams;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Demo demo = (Demo) o;
        return Objects.equals(id, demo.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "Demo{" +
                "id='" + id + '\'' +
                ", title='" + title + '\'' +
                ", protocol=" + protocol +
                ", complexity=" + complexity +
                '}';
    }

    /**
     * Protocol types supported in Phase 1
     */
    public enum Protocol {
        SIP_IMS("SIP/IMS"),
        DIAMETER("Diameter"),
        RADIUS("RADIUS");

        private final String displayName;

        Protocol(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }
    }

    /**
     * Complexity levels for demo scenarios
     */
    public enum Complexity {
        BASIC("Basic"),
        INTERMEDIATE("Intermediate"),
        ADVANCED("Advanced");

        private final String displayName;

        Complexity(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }
    }
}
