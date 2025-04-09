from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional, List, Dict, Any
import time

def wait_for_element(
    driver: WebDriver,
    by: By,
    value: str,
    timeout: int = 10
) -> Optional[Any]:
    """Wait for an element to be present and return it."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except Exception as e:
        print(f"Error waiting for element: {str(e)}")
        return None

def take_screenshot(driver: WebDriver, filename: str) -> bool:
    """Take a screenshot of the current page."""
    try:
        driver.save_screenshot(filename)
        return True
    except Exception as e:
        print(f"Error taking screenshot: {str(e)}")
        return False

def get_page_source(driver: WebDriver) -> str:
    """Get the page source of the current page."""
    return driver.page_source

def navigate_to_url(driver: WebDriver, url: str) -> bool:
    """Navigate to a specific URL."""
    try:
        driver.get(url)
        return True
    except Exception as e:
        print(f"Error navigating to URL: {str(e)}")
        return False

def extract_data(
    driver: WebDriver,
    selectors: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Extract data from the page using provided selectors."""
    data = {}
    for selector in selectors:
        try:
            element = wait_for_element(
                driver,
                getattr(By, selector['by']),
                selector['value']
            )
            if element:
                data[selector['name']] = element.text
        except Exception as e:
            print(f"Error extracting data for {selector['name']}: {str(e)}")
            data[selector['name']] = None
    return data

def execute_script(driver: WebDriver, script: str, *args) -> Any:
    """Execute JavaScript on the page."""
    try:
        return driver.execute_script(script, *args)
    except Exception as e:
        print(f"Error executing script: {str(e)}")
        return None 