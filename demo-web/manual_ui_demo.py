"""
Manual UI Demonstration Script
Opens browser, navigates through UI, executes a demo, and keeps browser open
"""

from playwright.sync_api import sync_playwright
import time

def main():
    """Run manual UI demonstration"""
    print("=" * 60)
    print("TTS Demo Tool - Manual UI Demonstration")
    print("=" * 60)
    print("\nStarting browser (will stay open for demonstration)...")
    
    with sync_playwright() as p:
        # Launch browser in headed mode with slow motion
        browser = p.chromium.launch(
            headless=False,
            slow_mo=500,  # 500ms delay between actions for visibility
            args=['--start-maximized']
        )
        
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            no_viewport=True  # Use browser's viewport
        )
        
        page = context.new_page()
        
        print("\n✓ Browser launched")
        print("\n" + "=" * 60)
        print("STEP 1: Loading TTS Demo Tool UI")
        print("=" * 60)
        
        # Navigate to the application
        page.goto("http://localhost:8000")
        page.wait_for_load_state("networkidle")
        print("✓ UI loaded at http://localhost:8000")
        time.sleep(2)
        
        print("\n" + "=" * 60)
        print("STEP 2: Viewing Demo Catalog")
        print("=" * 60)
        
        # Wait for demos to load
        page.wait_for_selector(".demo-item", timeout=10000)
        demo_count = page.locator(".demo-item").count()
        print(f"✓ {demo_count} demos loaded in catalog")
        time.sleep(2)
        
        print("\n" + "=" * 60)
        print("STEP 3: Filtering SIP/IMS Demos")
        print("=" * 60)
        
        # Filter by SIP protocol
        page.locator("#protocol-filter").select_option("SIP_IMS")
        page.wait_for_timeout(1000)
        sip_count = page.locator(".demo-item").count()
        print(f"✓ Filtered to {sip_count} SIP/IMS demos")
        time.sleep(2)
        
        print("\n" + "=" * 60)
        print("STEP 4: Selecting a Demo")
        print("=" * 60)
        
        # Click first demo
        first_demo = page.locator(".demo-item").first
        demo_title = first_demo.locator("h3").inner_text()
        print(f"✓ Selected demo: {demo_title}")
        first_demo.click()
        page.wait_for_timeout(1000)
        time.sleep(2)
        
        print("\n" + "=" * 60)
        print("STEP 5: Executing Demo")
        print("=" * 60)
        
        # Click Run Demo button
        run_button = page.locator("button:has-text('Run Demo')").first
        print("✓ Clicking 'Run Demo' button...")
        run_button.click()
        page.wait_for_timeout(2000)
        
        print("✓ Execution started - switching to Execution tab")
        print("\n" + "=" * 60)
        print("MONITORING EXECUTION (watch the browser window)")
        print("=" * 60)
        print("\nThe browser window shows three key panels:")
        print("  1. CONSOLE OUTPUT - Real-time JMeter execution logs")
        print("  2. STATISTICS - Success/failure counts and timing")
        print("  3. CALL FLOW DIAGRAM - SIP message sequence (if available)")
        print("\nWaiting 60 seconds for demo to complete...")
        print("(Execution includes ramp-up times and listen timeouts)")
        
        # Wait for execution to complete and show results
        for i in range(12):  # 12 x 5 seconds = 60 seconds
            time.sleep(5)
            # Check if console has output
            try:
                console_lines = page.locator(".console-line").count()
                if console_lines > 0:
                    print(f"  [{(i+1)*5}s] Console output: {console_lines} lines")
                else:
                    print(f"  [{(i+1)*5}s] Waiting for output...")
            except:
                print(f"  [{(i+1)*5}s] Waiting for execution to start...")
        
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("\nBrowser will stay open for 30 more seconds")
        print("You can:")
        print("  - Review the execution results")
        print("  - Check the console output")
        print("  - View statistics")
        print("  - Inspect the call flow diagram (if rendered)")
        print("  - Switch to other tabs (History, Traffic Generator)")
        
        time.sleep(30)
        
        print("\nClosing browser...")
        context.close()
        browser.close()
        
        print("\n✓ Demonstration complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
