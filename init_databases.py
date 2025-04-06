import os
import logging
from database.init_sample_db import init_sample_db
from database.ingredients_db import init_ingredients_db
from database.sample_recipes import SAMPLE_RECIPES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_all_databases():
    """Initialize all databases with sample data"""
    try:
        # Create database directory if it doesn't exist
        os.makedirs('database', exist_ok=True)
        
        # Initialize ingredients database
        logger.info("Initializing ingredients database...")
        init_ingredients_db()
        
        # Initialize recipes database
        logger.info("Initializing recipes database...")
        init_sample_db()
        
        logger.info("All databases initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing databases: {e}")
        raise

if __name__ == "__main__":
    init_all_databases() 