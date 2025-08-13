#!/usr/bin/env python3
"""Test script to verify MongoDB connection."""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.config.config import settings


async def test_connection():
    """Test the MongoDB connection."""
    print("Testing MongoDB connection...")
    print(f"MongoDB URL: {settings.MONGO_URL}")
    print(f"Database Name: {settings.DATABASE_NAME}")
    
    try:
        # Test async connection
        print("\n1. Testing async connection...")
        await connect_to_mongo()
        print("✅ Async connection successful!")
        
        # Test database access
        print("\n2. Testing database access...")
        db = get_database()
        if db:
            print("✅ Database access successful!")
            
            # Test collection creation
            print("\n3. Testing collection creation...")
            test_collection = db["test_connection"]
            await test_collection.insert_one({"test": "connection", "timestamp": "2024"})
            print("✅ Collection creation and document insertion successful!")
            
            # Clean up test data
            await test_collection.delete_one({"test": "connection"})
            print("✅ Test data cleanup successful!")
        else:
            print("❌ Database access failed!")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    finally:
        # Close connection
        print("\n4. Closing connection...")
        await close_mongo_connection()
        print("✅ Connection closed successfully!")
    
    return True


def test_sync_connection():
    """Test the synchronous MongoDB connection."""
    print("\n5. Testing sync connection...")
    
    try:
        from app.database import connect_to_mongo_sync, close_mongo_connection_sync, get_sync_database
        
        db = connect_to_mongo_sync()
        if db:
            print("✅ Sync connection successful!")
            
            # Test collection access
            test_collection = db["test_sync_connection"]
            result = test_collection.insert_one({"test": "sync_connection", "timestamp": "2024"})
            print("✅ Sync collection access successful!")
            
            # Clean up
            test_collection.delete_one({"test": "sync_connection"})
            print("✅ Sync test data cleanup successful!")
            
            close_mongo_connection_sync()
            print("✅ Sync connection closed successfully!")
            return True
        else:
            print("❌ Sync connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Sync connection failed: {e}")
        return False


async def main():
    """Main test function."""
    print("=" * 50)
    print("MongoDB Connection Test")
    print("=" * 50)
    
    # Test async connection
    async_success = await test_connection()
    
    # Test sync connection
    sync_success = test_sync_connection()
    
    print("\n" + "=" * 50)
    print("Test Results")
    print("=" * 50)
    print(f"Async Connection: {'✅ PASSED' if async_success else '❌ FAILED'}")
    print(f"Sync Connection:  {'✅ PASSED' if sync_success else '❌ FAILED'}")
    
    if async_success and sync_success:
        print("\n🎉 All tests passed! MongoDB is properly configured.")
        return 0
    else:
        print("\n💥 Some tests failed. Please check your configuration.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
