from fastapi import APIRouter, Depends, HTTPException
from selenium.webdriver.remote.webdriver import WebDriver
from app.core.dependencies import get_selenium
from app.utils.selenium_utils import (
    navigate_to_url,
    extract_data,
    take_screenshot,
    wait_for_element
)
from selenium.webdriver.common.by import By
from typing import Dict, Any
import os
import time

router = APIRouter()

@router.get("/scrape", response_model=Dict[str, Any])
def scrape_website(
    url: str,
    driver: WebDriver = Depends(get_selenium)
):
    """Scrape data from a website using Selenium."""
    try:
        # Navigate to the URL
        if not navigate_to_url(driver, url):
            raise HTTPException(
                status_code=500,
                detail="Failed to navigate to URL"
            )

        # Define selectors for data extraction
        selectors = [
            {"name": "title", "by": "TAG_NAME", "value": "h1"},
            {"name": "description", "by": "CSS_SELECTOR", "value": "meta[name='description']"},
        ]

        # Extract data
        data = extract_data(driver, selectors)

        # Take a screenshot
        screenshot_dir = "screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"screenshot_{int(time.time())}.png")
        take_screenshot(driver, screenshot_path)

        return {
            "data": data,
            "screenshot": screenshot_path
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scraping website: {str(e)}"
        ) 