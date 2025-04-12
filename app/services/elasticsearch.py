from elasticsearch import Elasticsearch
from typing import Optional, Dict, Any, List
import os
from datetime import datetime
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from app.core.config import settings

# Initialize NumPy and PyTorch in the correct order
try:
    # First ensure NumPy is properly initialized
    np.array([1, 2, 3])
    
    # Then initialize PyTorch
    if not torch.cuda.is_available():
        torch.set_default_device('cpu')
    
    # Initialize the sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')  # Force CPU usage
    
except Exception as e:
    print(f"Error during initialization: {str(e)}")
    raise

# Initialize Elasticsearch client with proper connection settings
try:
    es = Elasticsearch(
        settings.ELASTICSEARCH_URL,
        basic_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
        verify_certs=False,  # Set to True in production
        request_timeout=30
    )
    
    # Test the connection
    if not es.ping():
        raise ConnectionError("Could not connect to Elasticsearch. Please make sure Elasticsearch is running.")
        
except Exception as e:
    print(f"Error initializing Elasticsearch client: {str(e)}")
    raise

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
                            "dims": 384,  # all-MiniLM-L6-v2 dimension
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
    Get embedding for text using sentence-transformers
    """
    try:
        # Generate embedding using the sentence transformer model
        embedding = model.encode(text, convert_to_tensor=False).tolist()
        return embedding
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
        
        # Perform semantic search with proper query structure
        response = es.search(
            index=index_id,
            body={
                "size": size,
                "query": {
                    "function_score": {
                        "query": {"match_all": {}},
                        "functions": [
                            {
                                "script_score": {
                                    "script": {
                                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                        "params": {"query_vector": query_embedding}
                                    }
                                }
                            }
                        ],
                        "boost_mode": "replace"
                    }
                },
                "_source": ["content", "metadata", "created_at"]
            }
        )
        
        # Extract and format the results
        results = []
        for hit in response["hits"]["hits"]:
            result = {
                "content": hit["_source"]["content"],
                "metadata": hit["_source"].get("metadata", {}),
                "created_at": hit["_source"].get("created_at"),
                "score": hit["_score"]
            }
            results.append(result)
        
        return results
    except Exception as e:
        print(f"Error searching documents in index {index_id}: {str(e)}")
        raise 
    