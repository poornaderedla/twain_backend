"""Database connection and initialization module."""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.config.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global database client
client: AsyncIOMotorClient = None
sync_client: MongoClient = None
database = None


async def connect_to_mongo():
    """Create database connection."""
    global client, database
    try:
        client = AsyncIOMotorClient(settings.MONGO_URL)
        database = client[settings.DATABASE_NAME]
        
        # Test the connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        
        return database
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


def connect_to_mongo_sync():
    """Create synchronous database connection."""
    global sync_client
    try:
        sync_client = MongoClient(settings.MONGO_URL)
        # Test the connection
        sync_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB (sync)!")
        return sync_client[settings.DATABASE_NAME]
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB (sync): {e}")
        raise


async def close_mongo_connection():
    """Close database connection."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed.")


def close_mongo_connection_sync():
    """Close synchronous database connection."""
    global sync_client
    if sync_client:
        sync_client.close()
        logger.info("MongoDB connection closed (sync).")


def get_database():
    """Get database instance."""
    return database


def get_sync_database():
    """Get synchronous database instance."""
    if sync_client:
        return sync_client[settings.DATABASE_NAME]
    return None
