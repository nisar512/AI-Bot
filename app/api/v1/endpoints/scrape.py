from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
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
import xml.etree.ElementTree as ET
from selenium.webdriver.common.by import By
from typing import List
import asyncio

router = APIRouter()

async def process_url(url: str, chatbot_id: int, driver: WebDriver, db: Session) -> dict:
    """Process a single URL and store its content."""
    try:
        if not navigate_to_url(driver, url):
            return {"url": url, "status": "failed", "error": "Failed to navigate"}

        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        screenshot_dir = "screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"screenshot_{int(time.time())}.png")
        take_screenshot(driver, screenshot_path)

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
            "url": url,
            "status": "success",
            "document_id": document.id,
            "screenshot": screenshot_path
        }
    except Exception as e:
        return {"url": url, "status": "failed", "error": str(e)}

@router.post("/scrape")
async def scrape_website(
    url: str,
    chatbot_id: int,
    driver: WebDriver = Depends(get_selenium),
    db: Session = Depends(get_db)
):
    """Scrape a single website and store in Elasticsearch."""
    try:
        result = await process_url(url, chatbot_id, driver, db)
        if result["status"] == "failed":
            raise HTTPException(
                status_code=500,
                detail=f"Failed to scrape website: {result.get('error', 'Unknown error')}"
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scraping website: {str(e)}"
        )

@router.post("/process-sitemap")
async def process_sitemap(
    sitemap_url: str,
    chatbot_id: int,
    limit: int = 100,  # Default limit of 100 URLs
    driver: WebDriver = Depends(get_selenium),
    db: Session = Depends(get_db)
):
    """Process a sitemap URL and scrape all URLs from it."""
    try:
        # Navigate to sitemap URL
        if not navigate_to_url(driver, sitemap_url):
            raise HTTPException(
                status_code=500,
                detail="Failed to access sitemap URL"
            )

        # Get sitemap content
        sitemap_content = driver.page_source
        root = ET.fromstring(sitemap_content)
        
        # Extract URLs from sitemap
        urls = []
        for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
            loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if loc is not None:
                urls.append(loc.text)

        # Apply limit to URLs
        urls = urls[:limit]

        # Process URLs in batches to avoid overwhelming the system
        results = []
        batch_size = 5
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            tasks = [process_url(url, chatbot_id, driver, db) for url in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            time.sleep(2)  # Add delay between batches

        return {
            "total_urls": len(urls),
            "processed": len(results),
            "limit": limit,
            "results": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing sitemap: {str(e)}"
        ) 