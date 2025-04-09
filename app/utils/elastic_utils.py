from elasticsearch import AsyncElasticsearch
from typing import Dict, List, Any, Optional

async def create_index(es: AsyncElasticsearch, index_name: str, mappings: Dict[str, Any]) -> bool:
    """Create an Elasticsearch index with the specified mappings."""
    try:
        if not await es.indices.exists(index=index_name):
            await es.indices.create(index=index_name, body=mappings)
            return True
        return False
    except Exception as e:
        print(f"Error creating index {index_name}: {str(e)}")
        return False

async def index_document(es: AsyncElasticsearch, index_name: str, document: Dict[str, Any], doc_id: Optional[str] = None) -> bool:
    """Index a document in Elasticsearch."""
    try:
        await es.index(index=index_name, body=document, id=doc_id)
        return True
    except Exception as e:
        print(f"Error indexing document: {str(e)}")
        return False

async def search_documents(
    es: AsyncElasticsearch,
    index_name: str,
    query: Dict[str, Any],
    size: int = 10,
    from_: int = 0
) -> List[Dict[str, Any]]:
    """Search documents in Elasticsearch."""
    try:
        response = await es.search(
            index=index_name,
            body=query,
            size=size,
            from_=from_
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        print(f"Error searching documents: {str(e)}")
        return []

async def delete_document(es: AsyncElasticsearch, index_name: str, doc_id: str) -> bool:
    """Delete a document from Elasticsearch."""
    try:
        await es.delete(index=index_name, id=doc_id)
        return True
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        return False

async def update_document(
    es: AsyncElasticsearch,
    index_name: str,
    doc_id: str,
    doc: Dict[str, Any]
) -> bool:
    """Update a document in Elasticsearch."""
    try:
        await es.update(index=index_name, id=doc_id, body={"doc": doc})
        return True
    except Exception as e:
        print(f"Error updating document: {str(e)}")
        return False 