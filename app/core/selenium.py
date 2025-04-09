from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from app.core.config import settings

class SeleniumClient:
    def __init__(self):
        self.driver = None

    def init(self):
        """Initialize the Selenium WebDriver with remote settings from config."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            
            self.driver = webdriver.Remote(
                command_executor=settings.SELENIUM_REMOTE_URL,
                options=chrome_options
            )
            return True
        except Exception as e:
            print(f"Error initializing Selenium WebDriver: {str(e)}")
            return False

    def close(self):
        """Close the Selenium WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error closing Selenium WebDriver: {str(e)}")

    def get_driver(self) -> WebDriver:
        """Get the Selenium WebDriver instance."""
        if not self.driver:
            self.init()
        return self.driver

# Create a singleton instance
selenium_client = SeleniumClient() 