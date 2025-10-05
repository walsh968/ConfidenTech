from pymongo import MongoClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MongoDBConnection:
    """
    MongoDB connection utility
    """
    _client = None
    _db = None
    
    @classmethod
    def get_client(cls):
        """Get MongoDB client"""
        if cls._client is None:
            try:
                cls._client = MongoClient(settings.MONGODB_SETTINGS['host'])
                logger.info("MongoDB client connected successfully")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                raise
        return cls._client
    
    @classmethod
    def get_database(cls):
        """Get MongoDB database"""
        if cls._db is None:
            client = cls.get_client()
            cls._db = client[settings.MONGODB_SETTINGS['db']]
        return cls._db
    
    @classmethod
    def get_collection(cls, collection_name):
        """Get MongoDB collection"""
        db = cls.get_database()
        return db[collection_name]
    
    @classmethod
    def close_connection(cls):
        """Close MongoDB connection"""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("MongoDB connection closed")


def get_mongodb_collection(collection_name):
    """
    Helper function to get MongoDB collection
    """
    return MongoDBConnection.get_collection(collection_name)


# Example usage functions
def save_user_to_mongodb(user_data):
    """
    Save user data to MongoDB
    """
    try:
        collection = get_mongodb_collection('users')
        result = collection.insert_one(user_data)
        logger.info(f"User saved to MongoDB with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logger.error(f"Failed to save user to MongoDB: {str(e)}")
        raise


def get_user_from_mongodb(email):
    """
    Get user from MongoDB by email
    """
    try:
        collection = get_mongodb_collection('users')
        user = collection.find_one({'email': email})
        return user
    except Exception as e:
        logger.error(f"Failed to get user from MongoDB: {str(e)}")
        raise


def update_user_in_mongodb(email, update_data):
    """
    Update user in MongoDB
    """
    try:
        collection = get_mongodb_collection('users')
        result = collection.update_one(
            {'email': email},
            {'$set': update_data}
        )
        logger.info(f"User updated in MongoDB: {result.modified_count} documents modified")
        return result.modified_count
    except Exception as e:
        logger.error(f"Failed to update user in MongoDB: {str(e)}")
        raise


def delete_user_from_mongodb(email):
    """
    Delete user from MongoDB
    """
    try:
        collection = get_mongodb_collection('users')
        result = collection.delete_one({'email': email})
        logger.info(f"User deleted from MongoDB: {result.deleted_count} documents deleted")
        return result.deleted_count
    except Exception as e:
        logger.error(f"Failed to delete user from MongoDB: {str(e)}")
        raise
