"""
Database connection and management utilities.
"""
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB connections and operations."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.master_db: Optional[Database] = None
    
    def connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(settings.mongodb_url)
            self.master_db = self.client[settings.database_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {settings.database_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def get_master_db(self) -> Database:
        """Get the master database instance."""
        if not self.master_db:
            raise RuntimeError("Database not connected")
        return self.master_db
    
    def get_organizations_collection(self) -> Collection:
        """Get the organizations collection from master database."""
        return self.get_master_db()["organizations"]
    
    def get_admin_users_collection(self) -> Collection:
        """Get the admin users collection from master database."""
        return self.get_master_db()["admin_users"]
    
    def get_audit_logs_collection(self) -> Collection:
        """Get the audit logs collection from master database."""
        return self.get_master_db()["audit_logs"]
    
    def create_organization_collection(self, org_name: str) -> Collection:
        """Create a new collection for an organization."""
        collection_name = f"org_{org_name.lower()}"
        collection = self.get_master_db()[collection_name]
        
        # Initialize with a basic document to ensure collection creation
        collection.insert_one({
            "_id": "metadata",
            "organization_name": org_name,
            "created_at": None,  # Will be set by the service
            "schema_version": "1.0"
        })
        
        logger.info(f"Created organization collection: {collection_name}")
        return collection
    
    def get_organization_collection(self, org_name: str) -> Collection:
        """Get an existing organization collection."""
        collection_name = f"org_{org_name.lower()}"
        return self.get_master_db()[collection_name]
    
    def delete_organization_collection(self, org_name: str) -> bool:
        """Delete an organization collection."""
        try:
            collection_name = f"org_{org_name.lower()}"
            self.get_master_db().drop_collection(collection_name)
            logger.info(f"Deleted organization collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists."""
        return collection_name in self.get_master_db().list_collection_names()
    
    def health_check(self) -> dict:
        """Perform database health check."""
        try:
            # Ping the database
            self.client.admin.command('ping')
            
            # Get database stats
            stats = self.get_master_db().command("dbstats")
            
            return {
                "status": "healthy",
                "database": settings.database_name,
                "collections": len(self.get_master_db().list_collection_names()),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global database manager instance
db_manager = DatabaseManager()