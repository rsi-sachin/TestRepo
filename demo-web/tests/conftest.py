"""
Playwright Configuration
"""

from playwright.sync_api import sync_playwright
import pytest

# Test Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"
HEADLESS = False  # Set to True for CI/CD
SLOW_MO = 100  # Milliseconds delay between actions for debugging


@pytest.fixture(scope="session")
def browser_context():
    """Create browser context for tests"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir="test-results/videos"
        )
        yield context
        context.close()
        browser.close()


@pytest.fixture
def page(browser_context):
    """Create new page for each test"""
    page = browser_context.new_page()
    yield page
    page.close()
