from fastapi import APIRouter, Depends, HTTPException
from elasticsearch import AsyncElasticsearch
from typing import List, Dict, Any
from app.core.dependencies import get_elasticsearch

router = APIRouter()

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_documents(
    query: str,
    index: str = "users",
    size: int = 10,
    from_: int = 0,
    es: AsyncElasticsearch = Depends(get_elasticsearch)
):
    """Search documents in Elasticsearch."""
    try:
        search_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["name", "email"]
                }
            }
        }
        
        response = await es.search(
            index=index,
            body=search_query,
            size=size,
            from_=from_
        )
        
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching documents: {str(e)}"
        ) 