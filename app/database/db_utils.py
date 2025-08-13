"""Database utility functions for common operations."""
from typing import Dict, List, Any, Optional
from app.database import get_database, get_sync_database
import logging

logger = logging.getLogger(__name__)


async def insert_document(collection_name: str, document: Dict[str, Any]) -> str:
    """Insert a document into the specified collection."""
    try:
        db = get_database()
        if db is None:
            raise Exception("Database not connected")
        
        collection = db[collection_name]
        result = await collection.insert_one(document)
        logger.info(f"Document inserted with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting document: {e}")
        raise


def insert_document_sync(collection_name: str, document: Dict[str, Any]) -> str:
    """Insert a document into the specified collection (synchronous)."""
    try:
        db = get_sync_database()
        if db is None:
            raise Exception("Database not connected")
        
        collection = db[collection_name]
        result = collection.insert_one(document)
        logger.info(f"Document inserted with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting document: {e}")
        raise


async def find_documents(collection_name: str, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
    """Find documents in the specified collection."""
    try:
        db = get_database()
        if db is None:
            raise Exception("Database not connected")
        
        collection = db[collection_name]
        cursor = collection.find(query).limit(limit)
        documents = await cursor.to_list(length=limit)
        return documents
    except Exception as e:
        logger.error(f"Error finding documents: {e}")
        raise


def find_documents_sync(collection_name: str, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
    """Find documents in the specified collection (synchronous)."""
    try:
        db = get_sync_database()
        if db is None:
            raise Exception("Database not connected")
        
        collection = db[collection_name]
        documents = list(collection.find(query).limit(limit))
        return documents
    except Exception as e:
        logger.error(f"Error finding documents: {e}")
        raise


async def find_document_by_id(collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
    """Find a document by its ID."""
    try:
        db = get_database()
        if db is None:
            raise Exception("Database not connected")
        
        collection = db[collection_name]
        from bson import ObjectId
        document = await collection.find_one({"_id": ObjectId(document_id)})
        return document
    except Exception as e:
        logger.error(f"Error finding document by ID: {e}")
        raise


async def update_document(collection_name: str, document_id: str, update_data: Dict[str, Any]) -> bool:
    """Update a document by its ID."""
    try:
        db = get_database()
        if db is None:
            raise Exception("Database not connected")
        
        collection = db[collection_name]
        from bson import ObjectId
        result = await collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        raise


async def delete_document(collection_name: str, document_id: str) -> bool:
    """Delete a document by its ID."""
    try:
        db = get_database()
        if db is None:
            raise Exception("Database not connected")
        
        collection = db[collection_name]
        from bson import ObjectId
        result = await collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise


async def count_documents(collection_name: str, query: Optional[Dict[str, Any]] = None) -> int:
    """Count documents in the specified collection."""
    try:
        db = get_database()
        if db is None:
            raise Exception("Database not connected")
        
        collection = db[collection_name]
        if query is None:
            query = {}
        count = await collection.count_documents(query)
        return count
    except Exception as e:
        logger.error(f"Error counting documents: {e}")
        raise
