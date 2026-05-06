package com.tts.demo.service;

import com.tts.demo.model.Demo;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class DemoCatalogTest {

    private DemoCatalog catalog;

    @BeforeEach
    void setUp() {
        catalog = new DemoCatalog();
    }

    @Test
    void testCatalogLoadsSuccessfully() {
        assertFalse(catalog.isEmpty(), "Catalog should not be empty");
        assertTrue(catalog.getDemoCount() > 0, "Catalog should contain demos");
    }

    @Test
    void testGetAllDemos() {
        List<Demo> demos = catalog.getAllDemos();
        assertNotNull(demos);
        assertFalse(demos.isEmpty());
        
        // Verify we have at least 10 demos from our catalog
        assertTrue(demos.size() >= 10, "Should have at least 10 demos");
    }

    @Test
    void testGetDemoById() {
        // Test with known demo ID from catalog
        Demo demo = catalog.getDemoById("sip-001");
        assertNotNull(demo, "Should find demo with ID sip-001");
        assertEquals("sip-001", demo.getId());
        assertEquals("Simulate VoLTE Call Setup & Teardown", demo.getTitle());
        assertEquals(Demo.Protocol.SIP_IMS, demo.getProtocol());
    }

    @Test
    void testGetDemoByIdNotFound() {
        Demo demo = catalog.getDemoById("nonexistent-id");
        assertNull(demo, "Should return null for nonexistent demo ID");
    }

    @Test
    void testGetDemosByProtocol() {
        List<Demo> sipDemos = catalog.getDemosByProtocol(Demo.Protocol.SIP_IMS);
        assertFalse(sipDemos.isEmpty(), "Should have SIP/IMS demos");
        
        // Verify all returned demos are SIP/IMS
        for (Demo demo : sipDemos) {
            assertEquals(Demo.Protocol.SIP_IMS, demo.getProtocol());
        }

        List<Demo> diameterDemos = catalog.getDemosByProtocol(Demo.Protocol.DIAMETER);
        assertFalse(diameterDemos.isEmpty(), "Should have Diameter demos");

        List<Demo> radiusDemos = catalog.getDemosByProtocol(Demo.Protocol.RADIUS);
        assertFalse(radiusDemos.isEmpty(), "Should have RADIUS demos");
    }

    @Test
    void testGetDemosByComplexity() {
        List<Demo> basicDemos = catalog.getDemosByComplexity(Demo.Complexity.BASIC);
        assertFalse(basicDemos.isEmpty(), "Should have basic demos");
        
        // Verify all returned demos are basic
        for (Demo demo : basicDemos) {
            assertEquals(Demo.Complexity.BASIC, demo.getComplexity());
        }

        List<Demo> advancedDemos = catalog.getDemosByComplexity(Demo.Complexity.ADVANCED);
        assertFalse(advancedDemos.isEmpty(), "Should have advanced demos");
    }

    @Test
    void testSearchDemos() {
        // Search by title keyword
        List<Demo> results = catalog.searchDemos("VoLTE");
        assertFalse(results.isEmpty(), "Should find demos with 'VoLTE' in title");
        
        // Search by description keyword
        results = catalog.searchDemos("authentication");
        assertFalse(results.isEmpty(), "Should find demos with 'authentication' in description");
        
        // Case-insensitive search
        results = catalog.searchDemos("volte");
        assertFalse(results.isEmpty(), "Search should be case-insensitive");
    }

    @Test
    void testSearchDemosEmpty() {
        List<Demo> results = catalog.searchDemos("");
        assertEquals(catalog.getDemoCount(), results.size(), 
                "Empty search should return all demos");
    }

    @Test
    void testSearchDemosNull() {
        List<Demo> results = catalog.searchDemos(null);
        assertEquals(catalog.getDemoCount(), results.size(), 
                "Null search should return all demos");
    }

    @Test
    void testSearchDemosNoMatch() {
        List<Demo> results = catalog.searchDemos("XyZaBc12345");
        assertTrue(results.isEmpty(), "Should return empty list for no matches");
    }

    @Test
    void testGetAvailableProtocols() {
        Set<Demo.Protocol> protocols = catalog.getAvailableProtocols();
        assertNotNull(protocols);
        assertFalse(protocols.isEmpty());
        
        // Should have all three Phase 1 protocols
        assertTrue(protocols.contains(Demo.Protocol.SIP_IMS));
        assertTrue(protocols.contains(Demo.Protocol.DIAMETER));
        assertTrue(protocols.contains(Demo.Protocol.RADIUS));
    }

    @Test
    void testGetAvailableComplexityLevels() {
        Set<Demo.Complexity> complexities = catalog.getAvailableComplexityLevels();
        assertNotNull(complexities);
        assertFalse(complexities.isEmpty());
        
        // Should have multiple complexity levels
        assertTrue(complexities.contains(Demo.Complexity.BASIC));
        assertTrue(complexities.contains(Demo.Complexity.ADVANCED));
    }

    @Test
    void testDemoCount() {
        int count = catalog.getDemoCount();
        assertTrue(count >= 10, "Should have at least 10 demos");
        assertEquals(catalog.getAllDemos().size(), count);
    }

    @Test
    void testIsEmpty() {
        assertFalse(catalog.isEmpty());
    }

    @Test
    void testDemoDataIntegrity() {
        // Verify each demo has required fields populated
        for (Demo demo : catalog.getAllDemos()) {
            assertNotNull(demo.getId(), "Demo ID should not be null");
            assertNotNull(demo.getTitle(), "Demo title should not be null");
            assertNotNull(demo.getDescription(), "Demo description should not be null");
            assertNotNull(demo.getExpectedOutcome(), "Demo expected outcome should not be null");
            assertNotNull(demo.getProtocol(), "Demo protocol should not be null");
            assertNotNull(demo.getComplexity(), "Demo complexity should not be null");
            assertNotNull(demo.getJmxPath(), "Demo JMX path should not be null");
            assertNotNull(demo.getDefaultParams(), "Demo default params should not be null");
            
            // Verify business-level language (REQ-006)
            assertFalse(demo.getTitle().toLowerCase().contains(".jmx"), 
                    "Title should not contain technical JMX references");
        }
    }

    @Test
    void testGetAllDemosReturnsDefensiveCopy() {
        List<Demo> demos1 = catalog.getAllDemos();
        List<Demo> demos2 = catalog.getAllDemos();
        
        assertNotSame(demos1, demos2, "Should return different list instances");
        assertEquals(demos1.size(), demos2.size());
    }
}
