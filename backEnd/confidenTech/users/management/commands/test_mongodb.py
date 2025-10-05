from django.core.management.base import BaseCommand
from users.mongodb_utils import MongoDBConnection
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test MongoDB connection'

    def handle(self, *args, **options):
        try:
            # Test MongoDB connection
            client = MongoDBConnection.get_client()
            db = MongoDBConnection.get_database()
            
            # Test connection by listing collections
            collections = db.list_collection_names()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully connected to MongoDB!')
            )
            self.stdout.write(f'Database: {db.name}')
            self.stdout.write(f'Collections: {collections}')
            
            # Test inserting a document
            test_collection = MongoDBConnection.get_collection('test')
            test_doc = {'test': 'connection', 'timestamp': '2024-01-01'}
            result = test_collection.insert_one(test_doc)
            
            self.stdout.write(
                self.style.SUCCESS(f'Test document inserted with ID: {result.inserted_id}')
            )
            
            # Clean up test document
            test_collection.delete_one({'_id': result.inserted_id})
            self.stdout.write('Test document cleaned up.')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to connect to MongoDB: {str(e)}')
            )
            logger.error(f"MongoDB connection test failed: {str(e)}")
