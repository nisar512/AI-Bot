from elasticsearch import Elasticsearch
from typing import Optional, Dict, Any, List
import os
from openai import OpenAI
from datetime import datetime

# Initialize Elasticsearch client
es = Elasticsearch(
    os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
)

# Initialize OpenAI client with proper error handling
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    openai_client = OpenAI(api_key=openai_api_key)
except Exception as e:
    print(f"Error initializing OpenAI client: {str(e)}")
    openai_client = None

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
                        "created_at": {"type": "date"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": 1536,  # OpenAI's text-embedding-ada-002 dimension
                            "index": True,
                            "similarity": "cosine"
                        }
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

def get_embedding(text: str) -> List[float]:
    """
    Get embedding for text using OpenAI
    """
    if not openai_client:
        raise ValueError("OpenAI client is not initialized. Please set OPENAI_API_KEY environment variable.")
    
    try:
        response = openai_client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {str(e)}")
        raise

def add_document(index_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Add a document to Elasticsearch with embedding
    """
    try:
        # Get embedding for the content
        embedding = get_embedding(content)
        
        # Prepare document
        document = {
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
            "embedding": embedding
        }
        
        # Index the document
        response = es.index(
            index=index_id,
            document=document
        )
        
        return response["_id"]
    except Exception as e:
        print(f"Error adding document to index {index_id}: {str(e)}")
        raise

def search_documents(index_id: str, query: str, size: int = 10) -> List[Dict[str, Any]]:
    """
    Search documents using semantic search
    """
    try:
        # Get embedding for the query
        query_embedding = get_embedding(query)
        
        # Perform semantic search
        response = es.search(
            index=index_id,
            body={
                "size": size,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                            "params": {"query_vector": query_embedding}
                        }
                    }
                }
            }
        )
        
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        print(f"Error searching documents in index {index_id}: {str(e)}")
        raise 