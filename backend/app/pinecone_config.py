import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class PineconeManager:
    """Manages Pinecone index operations"""
    
    def __init__(self):
        self.api_key = os.getenv('PINECONE_API_KEY')
        self.environment = os.getenv('PINECONE_ENVIRONMENT')
        self.index_name = os.getenv('PINECONE_INDEX_NAME', 'youtube-transcriptions')
        
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable is required")
        if not self.environment:
            raise ValueError("PINECONE_ENVIRONMENT environment variable is required")
        
        # Initialize Pinecone with new API
        self.pc = Pinecone(api_key=self.api_key)
    
    def get_index(self):
        """Get the Pinecone index"""
        try:
            return self.pc.Index(self.index_name)
        except Exception as e:
            logger.error(f"Error getting Pinecone index: {e}")
            raise
    
    def create_index_if_not_exists(self):
        """Create the index if it doesn't exist"""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()

            if self.index_name not in existing_indexes.names():
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=768,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',           # or 'gcp'
                        region='us-east-1'     # or 'us-central1'
                    )
                )
                logger.info(f"Index {self.index_name} created successfully")
            else:
                logger.info(f"Index {self.index_name} already exists")

            return self.get_index()

        except Exception as e:
            logger.error(f"Error creating Pinecone index: {e}")
            raise

    def delete_index(self):
        """Delete the Pinecone index"""
        try:
            existing_indexes = self.pc.list_indexes()
            if self.index_name in existing_indexes.names():
                logger.info(f"Deleting Pinecone index: {self.index_name}")
                self.pc.delete_index(self.index_name)
                logger.info(f"Index {self.index_name} deleted successfully")
                return True
            else:
                logger.info(f"Index {self.index_name} does not exist")
                return False
        except Exception as e:
            logger.error(f"Error deleting Pinecone index: {e}")
            raise

# Global instance
_pinecone_manager = None

def get_pinecone_manager():
    """Get the global Pinecone manager instance"""
    global _pinecone_manager
    if _pinecone_manager is None:
        _pinecone_manager = PineconeManager()
    return _pinecone_manager 