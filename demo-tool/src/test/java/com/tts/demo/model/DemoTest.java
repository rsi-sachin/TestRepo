package com.tts.demo.model;

import org.junit.jupiter.api.Test;
import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class DemoTest {

    @Test
    void testDemoCreation() {
        Map<String, String> params = new HashMap<>();
        params.put("host", "localhost");
        params.put("port", "5060");

        Demo demo = new Demo(
                "demo-001",
                "VoLTE Call Setup",
                "Simulates a complete VoLTE call setup and teardown",
                "Successful call establishment with proper SIP signaling",
                Demo.Protocol.SIP_IMS,
                Demo.Complexity.BASIC,
                "C:\\TTS\\bin\\templates\\tts\\tts_sip_client.jmx",
                params
        );

        assertEquals("demo-001", demo.getId());
        assertEquals("VoLTE Call Setup", demo.getTitle());
        assertEquals(Demo.Protocol.SIP_IMS, demo.getProtocol());
        assertEquals(Demo.Complexity.BASIC, demo.getComplexity());
        assertEquals(2, demo.getDefaultParams().size());
    }

    @Test
    void testProtocolDisplayName() {
        assertEquals("SIP/IMS", Demo.Protocol.SIP_IMS.getDisplayName());
        assertEquals("Diameter", Demo.Protocol.DIAMETER.getDisplayName());
        assertEquals("RADIUS", Demo.Protocol.RADIUS.getDisplayName());
    }

    @Test
    void testComplexityDisplayName() {
        assertEquals("Basic", Demo.Complexity.BASIC.getDisplayName());
        assertEquals("Intermediate", Demo.Complexity.INTERMEDIATE.getDisplayName());
        assertEquals("Advanced", Demo.Complexity.ADVANCED.getDisplayName());
    }

    @Test
    void testEqualsAndHashCode() {
        Demo demo1 = new Demo();
        demo1.setId("demo-001");
        demo1.setTitle("Test Demo");

        Demo demo2 = new Demo();
        demo2.setId("demo-001");
        demo2.setTitle("Different Title");

        Demo demo3 = new Demo();
        demo3.setId("demo-002");

        assertEquals(demo1, demo2); // Same ID
        assertNotEquals(demo1, demo3); // Different ID
        assertEquals(demo1.hashCode(), demo2.hashCode());
    }

    @Test
    void testToString() {
        Demo demo = new Demo();
        demo.setId("demo-001");
        demo.setTitle("Test Demo");
        demo.setProtocol(Demo.Protocol.DIAMETER);
        demo.setComplexity(Demo.Complexity.ADVANCED);

        String result = demo.toString();
        assertTrue(result.contains("demo-001"));
        assertTrue(result.contains("DIAMETER"));
        assertTrue(result.contains("ADVANCED"));
    }

    @Test
    void testDefaultConstructor() {
        Demo demo = new Demo();
        assertNull(demo.getId());
        assertNull(demo.getTitle());
        assertNull(demo.getProtocol());
        assertNull(demo.getComplexity());
    }

    @Test
    void testSettersAndGetters() {
        Demo demo = new Demo();
        
        demo.setId("test-id");
        assertEquals("test-id", demo.getId());

        demo.setTitle("Test Title");
        assertEquals("Test Title", demo.getTitle());

        demo.setDescription("Test Description");
        assertEquals("Test Description", demo.getDescription());

        demo.setExpectedOutcome("Test Outcome");
        assertEquals("Test Outcome", demo.getExpectedOutcome());

        demo.setProtocol(Demo.Protocol.RADIUS);
        assertEquals(Demo.Protocol.RADIUS, demo.getProtocol());

        demo.setComplexity(Demo.Complexity.INTERMEDIATE);
        assertEquals(Demo.Complexity.INTERMEDIATE, demo.getComplexity());

        demo.setJmxPath("C:\\path\\to\\test.jmx");
        assertEquals("C:\\path\\to\\test.jmx", demo.getJmxPath());

        Map<String, String> params = new HashMap<>();
        params.put("key", "value");
        demo.setDefaultParams(params);
        assertEquals(params, demo.getDefaultParams());
    }
}
