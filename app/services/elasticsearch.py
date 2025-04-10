from elasticsearch import Elasticsearch
from typing import Optional
import os

# Initialize Elasticsearch client
es = Elasticsearch(
    os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
)

def create_bot_index(index_id: str) -> bool:
    """
    Create a new Elasticsearch index for a bot
    """
    try:
        # Create index with basic settings
        es.indices.create(
            index=index_id,
            body={
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1
                },
                "mappings": {
                    "properties": {
                        "content": {"type": "text"},
                        "metadata": {"type": "object"},
                        "created_at": {"type": "date"}
                    }
                }
            }
        )
        return True
    except Exception as e:
        print(f"Error creating index {index_id}: {str(e)}")
        return False

def delete_bot_index(index_id: str) -> bool:
    """
    Delete an Elasticsearch index for a bot
    """
    try:
        es.indices.delete(index=index_id)
        return True
    except Exception as e:
        print(f"Error deleting index {index_id}: {str(e)}")
        return False

def index_exists(index_id: str) -> bool:
    """
    Check if an index exists
    """
    return es.indices.exists(index=index_id) 