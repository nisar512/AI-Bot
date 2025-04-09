from elasticsearch import AsyncElasticsearch
from app.core.config import settings

class ElasticsearchClient:
    def __init__(self):
        self.client = None

    async def init(self):
        """Initialize the Elasticsearch client with settings from config."""
        self.client = AsyncElasticsearch(
            hosts=[f"http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"],
            verify_certs=False,  # Set to True in production with proper certificates
            timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )

    async def close(self):
        """Close the Elasticsearch client connection."""
        if self.client:
            await self.client.close()

    async def get_client(self):
        """Get the Elasticsearch client instance."""
        if not self.client:
            await self.init()
        return self.client

# Create a singleton instance
elasticsearch_client = ElasticsearchClient() 