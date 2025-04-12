from fastapi import APIRouter, Depends, HTTPException
from selenium.webdriver.remote.webdriver import WebDriver
from app.core.dependencies import get_selenium
from app.utils.selenium_utils import navigate_to_url, take_screenshot
from app.services.elasticsearch import add_document
from app.services.document import create_document
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.document import DocumentCreate
import os
import time
from selenium.webdriver.common.by import By

router = APIRouter()

@router.post("/scrape")
async def scrape_website(
    url: str,
    chatbot_id: int,
    driver: WebDriver = Depends(get_selenium),
    db: Session = Depends(get_db)
):
    """Scrape website content and store in Elasticsearch."""
    try:
        # Navigate to the URL
        if not navigate_to_url(driver, url):
            raise HTTPException(
                status_code=500,
                detail="Failed to navigate to URL"
            )

        # Get full page text
        page_text = driver.find_element(By.TAG_NAME, "body").text

        # Take a screenshot
        screenshot_dir = "screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"screenshot_{int(time.time())}.png")
        take_screenshot(driver, screenshot_path)

        # Create document in Elasticsearch
        document = create_document(
            db=db,
            document=DocumentCreate(
                chatbot_id=chatbot_id,
                content=page_text,
                metadata={
                    "url": url,
                    "screenshot": screenshot_path,
                    "type": "webpage"
                }
            )
        )

        return {
            "document_id": document.id,
            "screenshot": screenshot_path
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scraping website: {str(e)}"
        ) 