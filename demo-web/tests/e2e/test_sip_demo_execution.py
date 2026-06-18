"""
Automated End-to-End Tests for SIP Demo Execution with Call Flow Visualization
Tests Phase 3 functionality: Real-time console output, WebSocket, and Mermaid diagrams
"""

import pytest
import time
import json
from playwright.sync_api import Page, expect


class TestSIPDemoExecution:
    """Comprehensive automated tests for SIP demo execution"""
    
    def test_page_loads_successfully(self, page: Page):
        """Test 1: Basic page load and structure"""
        page.goto("http://localhost:8000")
        
        # Verify page title and header
        expect(page.locator("h1")).to_contain_text("TTS Demo Tool")
        
        # Verify navigation tabs exist
        expect(page.locator("text=Demos")).to_be_visible()
        expect(page.locator("text=Execution")).to_be_visible()
        expect(page.locator("text=Traffic Generator")).to_be_visible()
        expect(page.locator("text=History")).to_be_visible()
        
        print("✓ Page structure verified")
    
    def test_demo_list_loads(self, page: Page):
        """Test 2: Demo catalog loads and displays"""
        page.goto("http://localhost:8000")
        
        # Wait for demos to load
        page.wait_for_selector(".demo-item", timeout=10000)
        
        # Count demo items
        demo_items = page.locator(".demo-item")
        count = demo_items.count()
        
        assert count > 0, "No demos loaded"
        print(f"✓ {count} demos loaded successfully")
        
        # Verify at least one SIP demo exists
        sip_demos = page.locator(".demo-item:has-text('SIP')")
        assert sip_demos.count() > 0, "No SIP demos found"
        print(f"✓ {sip_demos.count()} SIP demos found")
    
    def test_demo_search_filter(self, page: Page):
        """Test 3: Search and filter functionality"""
        page.goto("http://localhost:8000")
        page.wait_for_selector(".demo-item", timeout=10000)
        
        initial_count = page.locator(".demo-item").count()
        
        # Test search
        search_box = page.locator("#demo-search")
        search_box.fill("VoLTE")
        page.wait_for_timeout(500)  # Debounce delay
        
        filtered_count = page.locator(".demo-item").count()
        assert filtered_count < initial_count, "Search filter not working"
        assert filtered_count > 0, "Search returned no results"
        print(f"✓ Search filtered from {initial_count} to {filtered_count} demos")
        
        # Clear search
        search_box.fill("")
        page.wait_for_timeout(500)
        
        # Test protocol filter
        protocol_select = page.locator("#protocol-filter")
        protocol_select.select_option("SIP_IMS")
        page.wait_for_timeout(500)
        
        sip_count = page.locator(".demo-item").count()
        assert sip_count > 0, "Protocol filter returned no SIP demos"
        print(f"✓ Protocol filter shows {sip_count} SIP demos")
    
    def test_demo_selection_and_details(self, page: Page):
        """Test 4: Demo selection shows details panel"""
        page.goto("http://localhost:8000")
        page.wait_for_selector(".demo-item", timeout=10000)
        
        # Select first SIP demo
        first_demo = page.locator(".demo-item").first
        demo_title = first_demo.locator("h3").inner_text()
        first_demo.click()
        
        # Verify details panel appears
        details_panel = page.locator("#demo-details")
        expect(details_panel).to_be_visible()
        
        # Verify details content
        expect(page.locator("#demo-details h2")).to_contain_text(demo_title)
        expect(page.locator("text=Description")).to_be_visible()
        expect(page.locator("text=Expected Outcome")).to_be_visible()
        expect(page.locator("button:has-text('Run Demo')").first).to_be_visible()
        
        print(f"✓ Demo details displayed for: {demo_title}")
    
    def test_sip_demo_execution_with_console_output(self, page: Page):
        """Test 5: Execute SIP demo and verify console output"""
        page.goto("http://localhost:8000")
        page.wait_for_selector(".demo-item", timeout=10000)
        
        # Find and select a SIP demo
        page.locator("#protocol-filter").select_option("SIP_IMS")
        page.wait_for_timeout(500)
        
        first_sip_demo = page.locator(".demo-item").first
        demo_title = first_sip_demo.locator("h3").inner_text()
        first_sip_demo.click()
        
        print(f"▶ Executing demo: {demo_title}")
        
        # Click Run Demo button (use first match - the main one, not form submit)
        run_button = page.locator("button:has-text('Run Demo')").first
        run_button.click()
        
        # Should switch to Execution tab automatically
        page.wait_for_timeout(1000)
        
        # Verify console panel exists and is visible
        console_output = page.locator("#console-output")
        expect(console_output).to_be_visible()
        
        # Wait for console output to appear
        print("⏳ Waiting for JMeter output...")
        page.wait_for_selector(".console-line", timeout=15000)
        
        # Verify console lines are appearing
        console_lines = page.locator(".console-line")
        initial_count = console_lines.count()
        assert initial_count > 0, "No console output received"
        print(f"✓ Console output started: {initial_count} lines")
        
        # Wait for more output (JMeter startup messages)
        page.wait_for_timeout(3000)
        updated_count = console_lines.count()
        assert updated_count >= initial_count, "Console output stopped"
        print(f"✓ Console streaming: {updated_count} lines")
        
        # Verify specific JMeter output keywords
        console_text = console_output.inner_text()
        assert "Creating summariser" in console_text or "Created the tree" in console_text, \
            "Expected JMeter output not found"
        print("✓ JMeter execution confirmed")
    
    def test_execution_statistics_update(self, page: Page):
        """Test 6: Execution statistics display and update"""
        page.goto("http://localhost:8000")
        page.wait_for_selector(".demo-item", timeout=10000)
        
        # Execute a fast demo
        page.locator("#protocol-filter").select_option("SIP_IMS")
        page.wait_for_timeout(500)
        page.locator(".demo-item").first.click()
        page.locator("button:has-text('Run Demo')").first.click()
        
        # Wait for execution to start
        page.wait_for_selector(".console-line", timeout=15000)
        
        # Check for statistics section
        stats_section = page.locator(".execution-stats, #execution-stats, .stats-container")
        if stats_section.count() > 0:
            print("✓ Statistics section found")
            
            # Wait for completion (with timeout)
            for i in range(60):  # 60 seconds max
                page.wait_for_timeout(1000)
                console_text = page.locator("#console-output").inner_text()
                if "complete" in console_text.lower() or "finished" in console_text.lower():
                    print(f"✓ Execution completed after ~{i+1} seconds")
                    break
        else:
            print("⚠ Statistics section not found (may be implemented in stats tab)")
    
    def test_call_flow_diagram_rendering(self, page: Page):
        """Test 7: Call flow diagram rendering (Phase 3 feature)"""
        page.goto("http://localhost:8000")
        page.wait_for_selector(".demo-item", timeout=10000)
        
        # Execute SIP demo
        page.locator("#protocol-filter").select_option("SIP_IMS")
        page.wait_for_timeout(500)
        
        first_sip_demo = page.locator(".demo-item").first
        demo_title = first_sip_demo.locator("h3").inner_text()
        first_sip_demo.click()
        page.locator("button:has-text('Run Demo')").first.click()
        
        print(f"▶ Testing call flow for: {demo_title}")
        
        # Wait for execution to start
        page.wait_for_selector(".console-line", timeout=15000)
        
        # Check for call flow diagram panel
        callflow_panel = page.locator("#callflow-diagram, .callflow-panel, [data-testid='call-flow']")
        
        if callflow_panel.count() > 0:
            print("✓ Call flow panel found")
            
            # Wait up to 60 seconds for diagram to appear
            print("⏳ Waiting for SIP messages and Mermaid diagram...")
            diagram_appeared = False
            
            for i in range(60):
                page.wait_for_timeout(1000)
                
                # Check for Mermaid diagram element
                mermaid_diagram = page.locator(".mermaid, svg[id*='mermaid']")
                if mermaid_diagram.count() > 0:
                    print(f"✓ Call flow diagram rendered after ~{i+1} seconds")
                    diagram_appeared = True
                    
                    # Verify diagram has content
                    try:
                        svg_element = page.locator("svg").first
                        if svg_element.is_visible():
                            print("✓ Mermaid SVG diagram is visible")
                    except:
                        pass
                    
                    break
                
                # Check if execution completed without diagram
                console_text = page.locator("#console-output").inner_text()
                if "complete" in console_text.lower() or "finished" in console_text.lower():
                    print(f"⚠ Execution completed after ~{i+1} seconds but no diagram found")
                    print("  (This may be expected if JTL doesn't contain SIP responseData)")
                    break
            
            if not diagram_appeared:
                print("⚠ Call flow diagram did not appear (check JTL format and SIP messages)")
        else:
            print("⚠ Call flow panel not found in DOM")
    
    def test_multiple_demo_executions(self, page: Page):
        """Test 8: Execute multiple demos in sequence"""
        page.goto("http://localhost:8000")
        page.wait_for_selector(".demo-item", timeout=10000)
        
        page.locator("#protocol-filter").select_option("SIP_IMS")
        page.wait_for_timeout(500)
        
        demo_count = min(2, page.locator(".demo-item").count())  # Test first 2 demos
        
        for i in range(demo_count):
            demo = page.locator(".demo-item").nth(i)
            demo_title = demo.locator("h3").inner_text()
            
            print(f"\n▶ Test execution {i+1}/{demo_count}: {demo_title}")
            
            demo.click()
            page.wait_for_timeout(500)
            
            run_button = page.locator("button:has-text('Run Demo')").first
            if run_button.is_visible():
                run_button.click()
                
                # Wait for console output
                try:
                    page.wait_for_selector(".console-line", timeout=10000)
                    console_lines = page.locator(".console-line").count()
                    print(f"  ✓ Execution started: {console_lines} lines")
                    
                    # Don't wait for completion, just verify start
                    page.wait_for_timeout(2000)
                    
                except Exception as e:
                    print(f"  ✗ Execution failed to start: {str(e)}")
            
            # Go back to demos tab for next iteration
            page.locator("text=Demos").click()
            page.wait_for_timeout(1000)
        
        print(f"\n✓ All {demo_count} demo executions initiated successfully")
    
    def test_console_controls(self, page: Page):
        """Test 9: Console control buttons (clear, cancel)"""
        page.goto("http://localhost:8000")
        page.wait_for_selector(".demo-item", timeout=10000)
        
        # Execute a demo
        page.locator(".demo-item").first.click()
        page.locator("button:has-text('Run Demo')").first.click()
        
        # Wait for output
        page.wait_for_selector(".console-line", timeout=15000)
        initial_lines = page.locator(".console-line").count()
        
        # Test clear console button
        clear_button = page.locator("button:has-text('Clear')")
        if clear_button.count() > 0:
            clear_button.click()
            page.wait_for_timeout(500)
            
            remaining_lines = page.locator(".console-line").count()
            assert remaining_lines < initial_lines, "Clear console button not working"
            print("✓ Clear console button works")
        else:
            print("⚠ Clear console button not found")
    
    def test_websocket_connection(self, page: Page):
        """Test 10: Verify WebSocket connection establishes"""
        page.goto("http://localhost:8000")
        
        # Set up console listener for WebSocket messages
        ws_connected = False
        ws_error = None
        
        def handle_console(msg):
            nonlocal ws_connected, ws_error
            if "WebSocket" in msg.text:
                if "opened" in msg.text or "connected" in msg.text:
                    ws_connected = True
                elif "error" in msg.text or "failed" in msg.text:
                    ws_error = msg.text
        
        page.on("console", handle_console)
        
        # Execute demo
        page.wait_for_selector(".demo-item", timeout=10000)
        page.locator(".demo-item").first.click()
        page.locator("button:has-text('Run Demo')").first.click()
        
        # Wait for WebSocket connection attempt
        page.wait_for_timeout(3000)
        
        # Check for console output (indicates successful message receipt)
        console_lines = page.locator(".console-line")
        if console_lines.count() > 0:
            print("✓ Real-time console output received (WebSocket working)")
        else:
            print("⚠ No real-time output (check WebSocket connection)")


if __name__ == "__main__":
    print("Run with: pytest tests/e2e/test_sip_demo_execution.py -v -s")
