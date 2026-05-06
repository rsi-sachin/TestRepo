package com.tts.demo.model;

import org.junit.jupiter.api.Test;
import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class DemoConfigTest {

    @Test
    void testDefaultConstructor() {
        DemoConfig config = new DemoConfig();
        assertNull(config.getDemoId());
        assertNotNull(config.getParameters());
        assertTrue(config.getParameters().isEmpty());
    }

    @Test
    void testConstructorWithDemoId() {
        DemoConfig config = new DemoConfig("demo-001");
        assertEquals("demo-001", config.getDemoId());
        assertTrue(config.getParameters().isEmpty());
    }

    @Test
    void testConstructorWithParameters() {
        Map<String, String> params = new HashMap<>();
        params.put("host", "localhost");
        params.put("port", "5060");

        DemoConfig config = new DemoConfig("demo-001", params);
        
        assertEquals("demo-001", config.getDemoId());
        assertEquals(2, config.getParameters().size());
        assertEquals("localhost", config.getParameter("host"));
        assertEquals("5060", config.getParameter("port"));
    }

    @Test
    void testSetAndGetParameter() {
        DemoConfig config = new DemoConfig("demo-001");
        
        config.setParameter("host", "192.168.1.1");
        config.setParameter("port", "8080");
        
        assertEquals("192.168.1.1", config.getParameter("host"));
        assertEquals("8080", config.getParameter("port"));
        assertNull(config.getParameter("nonexistent"));
    }

    @Test
    void testGetParameterWithDefault() {
        DemoConfig config = new DemoConfig("demo-001");
        config.setParameter("host", "localhost");
        
        assertEquals("localhost", config.getParameter("host", "default"));
        assertEquals("default", config.getParameter("nonexistent", "default"));
    }

    @Test
    void testHasParameter() {
        DemoConfig config = new DemoConfig("demo-001");
        config.setParameter("host", "localhost");
        
        assertTrue(config.hasParameter("host"));
        assertFalse(config.hasParameter("port"));
    }

    @Test
    void testMergeDefaults() {
        DemoConfig config = new DemoConfig("demo-001");
        config.setParameter("host", "192.168.1.1");
        config.setParameter("threads", "10");
        
        Map<String, String> defaults = new HashMap<>();
        defaults.put("host", "localhost"); // Should NOT override
        defaults.put("port", "5060");      // Should be added
        defaults.put("loops", "1");        // Should be added
        
        config.mergeDefaults(defaults);
        
        assertEquals("192.168.1.1", config.getParameter("host")); // Not overridden
        assertEquals("5060", config.getParameter("port"));         // Added
        assertEquals("1", config.getParameter("loops"));           // Added
        assertEquals("10", config.getParameter("threads"));        // Preserved
    }

    @Test
    void testMergeDefaultsWithNull() {
        DemoConfig config = new DemoConfig("demo-001");
        config.setParameter("host", "localhost");
        
        config.mergeDefaults(null);
        
        assertEquals("localhost", config.getParameter("host"));
        assertEquals(1, config.getParameters().size());
    }

    @Test
    void testToJMeterArgs() {
        DemoConfig config = new DemoConfig("demo-001");
        config.setParameter("host", "localhost");
        config.setParameter("port", "5060");
        config.setParameter("threads", "10");
        
        String[] args = config.toJMeterArgs();
        
        assertEquals(3, args.length);
        assertTrue(containsArg(args, "-Jhost=localhost"));
        assertTrue(containsArg(args, "-Jport=5060"));
        assertTrue(containsArg(args, "-Jthreads=10"));
    }

    @Test
    void testToJMeterArgsEmpty() {
        DemoConfig config = new DemoConfig("demo-001");
        String[] args = config.toJMeterArgs();
        assertEquals(0, args.length);
    }

    @Test
    void testEqualsAndHashCode() {
        Map<String, String> params1 = new HashMap<>();
        params1.put("host", "localhost");
        
        DemoConfig config1 = new DemoConfig("demo-001", params1);
        DemoConfig config2 = new DemoConfig("demo-001", params1);
        DemoConfig config3 = new DemoConfig("demo-002", params1);
        
        assertEquals(config1, config2);
        assertNotEquals(config1, config3);
        assertEquals(config1.hashCode(), config2.hashCode());
    }

    @Test
    void testToString() {
        DemoConfig config = new DemoConfig("demo-001");
        config.setParameter("host", "localhost");
        
        String str = config.toString();
        assertTrue(str.contains("demo-001"));
        assertTrue(str.contains("host"));
        assertTrue(str.contains("localhost"));
    }

    @Test
    void testGetParametersReturnsDefensiveCopy() {
        DemoConfig config = new DemoConfig("demo-001");
        config.setParameter("host", "localhost");
        
        Map<String, String> params = config.getParameters();
        params.put("malicious", "value");
        
        // Original should not be affected
        assertFalse(config.hasParameter("malicious"));
        assertEquals(1, config.getParameters().size());
    }

    @Test
    void testSetParametersCreatesDefensiveCopy() {
        Map<String, String> params = new HashMap<>();
        params.put("host", "localhost");
        
        DemoConfig config = new DemoConfig("demo-001");
        config.setParameters(params);
        
        // Modify original map
        params.put("malicious", "value");
        
        // Config should not be affected
        assertFalse(config.hasParameter("malicious"));
        assertEquals(1, config.getParameters().size());
    }

    // Helper method
    private boolean containsArg(String[] args, String target) {
        for (String arg : args) {
            if (arg.equals(target)) {
                return true;
            }
        }
        return false;
    }
}
