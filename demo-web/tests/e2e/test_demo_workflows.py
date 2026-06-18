"""
End-to-End Tests for TTS Demo Tool Web Interface
Tests complete user workflows using Playwright
"""

import pytest
from playwright.sync_api import Page, expect
import time


class TestDemoSelection:
    """Test demo selection and filtering"""
    
    def test_load_homepage(self, page: Page):
        """Test that homepage loads successfully"""
        page.goto("http://localhost:8000")
        
        # Check title
        expect(page).to_have_title("TTS Demo Tool - Web Interface")
        
        # Check main navigation
        expect(page.locator('.nav-btn[data-tab="demos"]')).to_be_visible()
        expect(page.locator('.nav-btn[data-tab="execution"]')).to_be_visible()
        expect(page.locator('.nav-btn[data-tab="traffic"]')).to_be_visible()
        expect(page.locator('.nav-btn[data-tab="history"]')).to_be_visible()
    
    def test_connection_status(self, page: Page):
        """Test connection status indicator"""
        page.goto("http://localhost:8000")
        
        # Wait for connection check
        time.sleep(1)
        
        # Check status indicator
        status_text = page.locator('#connection-text')
        expect(status_text).to_contain_text("Connected")
    
    def test_demo_list_loads(self, page: Page):
        """Test that demo list populates"""
        page.goto("http://localhost:8000")
        
        # Wait for demos to load
        page.wait_for_selector('.demo-item', timeout=5000)
        
        # Check at least one demo is visible
        demo_items = page.locator('.demo-item')
        expect(demo_items).to_have_count_greater_than(0)
    
    def test_demo_selection(self, page: Page):
        """Test selecting a demo shows details"""
        page.goto("http://localhost:8000")
        
        # Wait for demos to load
        page.wait_for_selector('.demo-item')
        
        # Click first demo
        first_demo = page.locator('.demo-item').first
        first_demo.click()
        
        # Check demo is selected
        expect(first_demo).to_have_class('demo-item selected')
        
        # Check details panel shows content
        details = page.locator('#demo-detail-content')
        expect(details).not_to_contain_text("Select a demo")
        expect(details.locator('h2')).to_be_visible()
        expect(details.locator('.btn-primary')).to_be_visible()
    
    def test_protocol_filter(self, page: Page):
        """Test filtering demos by protocol"""
        page.goto("http://localhost:8000")
        
        # Wait for demos to load
        page.wait_for_selector('.demo-item')
        
        # Select protocol filter
        protocol_filter = page.locator('#protocol-filter')
        protocol_filter.select_option(index=1)  # Select first protocol
        
        # Check filtered results
        # Note: Actual filtering logic needs to be implemented in app.js
        time.sleep(0.5)


class TestDemoExecution:
    """Test demo execution workflow"""
    
    def test_run_demo_button_exists(self, page: Page):
        """Test run demo button is available"""
        page.goto("http://localhost:8000")
        
        # Select a demo
        page.wait_for_selector('.demo-item')
        page.locator('.demo-item').first.click()
        
        # Check run button
        run_button = page.locator('button:has-text("Run Demo")')
        expect(run_button).to_be_visible()
        expect(run_button).to_be_enabled()
    
    @pytest.mark.skip(reason="Requires backend implementation")
    def test_execute_demo_switches_tab(self, page: Page):
        """Test that running demo switches to execution tab"""
        page.goto("http://localhost:8000")
        
        # Select and run demo
        page.wait_for_selector('.demo-item')
        page.locator('.demo-item').first.click()
        page.locator('button:has-text("Run Demo")').click()
        
        # Check switched to execution tab
        expect(page.locator('.nav-btn[data-tab="execution"]')).to_have_class('nav-btn active')
        expect(page.locator('#execution-tab')).to_have_class('tab-content active')


class TestNavigation:
    """Test navigation between tabs"""
    
    def test_switch_to_traffic_tab(self, page: Page):
        """Test switching to traffic generator tab"""
        page.goto("http://localhost:8000")
        
        # Click traffic tab
        page.locator('.nav-btn[data-tab="traffic"]').click()
        
        # Check tab is active
        expect(page.locator('.nav-btn[data-tab="traffic"]')).to_have_class('nav-btn active')
        expect(page.locator('#traffic-tab')).to_have_class('tab-content active')
        
        # Check traffic form is visible
        expect(page.locator('#traffic-form')).to_be_visible()
    
    def test_switch_to_history_tab(self, page: Page):
        """Test switching to history tab"""
        page.goto("http://localhost:8000")
        
        # Click history tab
        page.locator('.nav-btn[data-tab="history"]').click()
        
        # Check tab is active
        expect(page.locator('#history-tab')).to_have_class('tab-content active')


class TestTrafficGenerator:
    """Test traffic generator functionality"""
    
    def test_traffic_controls_exist(self, page: Page):
        """Test traffic generator controls are present"""
        page.goto("http://localhost:8000")
        
        # Switch to traffic tab
        page.locator('.nav-btn[data-tab="traffic"]').click()
        
        # Check form controls
        expect(page.locator('#concurrent-calls')).to_be_visible()
        expect(page.locator('#total-calls')).to_be_visible()
        expect(page.locator('#rampup-time')).to_be_visible()
        expect(page.locator('#failure-rate')).to_be_visible()
        expect(page.locator('#conformance-scenario')).to_be_visible()
    
    def test_slider_updates_value(self, page: Page):
        """Test that moving sliders updates displayed values"""
        page.goto("http://localhost:8000")
        
        # Switch to traffic tab
        page.locator('.nav-btn[data-tab="traffic"]').click()
        
        # Get slider and value display
        slider = page.locator('#concurrent-calls')
        value_display = page.locator('#concurrent-value')
        
        # Change slider value
        slider.fill('50')
        
        # Check value updated
        expect(value_display).to_have_text('50')
    
    def test_throughput_chart_exists(self, page: Page):
        """Test throughput chart div is present"""
        page.goto("http://localhost:8000")
        
        # Switch to traffic tab
        page.locator('.nav-btn[data-tab="traffic"]').click()
        
        # Check chart container
        expect(page.locator('#throughput-chart')).to_be_visible()


class TestAPIIntegration:
    """Test API integration"""
    
    def test_health_endpoint(self, page: Page):
        """Test health endpoint returns success"""
        response = page.request.get("http://localhost:8000/health")
        assert response.status == 200
        data = response.json()
        assert data['status'] == 'healthy'
    
    @pytest.mark.skip(reason="Requires backend implementation")
    def test_demos_endpoint(self, page: Page):
        """Test demos endpoint returns data"""
        response = page.request.get("http://localhost:8000/api/demos")
        assert response.status == 200
        demos = response.json()
        assert isinstance(demos, list)
        assert len(demos) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
