from fastapi import Depends
from app.core.elastic import elasticsearch_client
from app.core.selenium import selenium_client
from selenium.webdriver.remote.webdriver import WebDriver

async def get_elasticsearch():
    """Dependency to get Elasticsearch client."""
    client = await elasticsearch_client.get_client()
    try:
        yield client
    finally:
        await elasticsearch_client.close()

def get_selenium() -> WebDriver:
    """Dependency to get Selenium WebDriver."""
    driver = selenium_client.get_driver()
    try:
        yield driver
    finally:
        selenium_client.close() 