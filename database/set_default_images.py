"""
Script to set default image paths for all recipes
"""

import sqlite3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def set_default_images():
    """Set default image paths for all recipes"""
    try:
        # Connect to database
        conn = sqlite3.connect('database/recipes.db')
        cursor = conn.cursor()
        
        # Update ALL recipes with default image path
        cursor.execute('''
            UPDATE recipes 
            SET image_path = '/static/images/recipes/default.jpg'
        ''')
        
        # Commit changes
        conn.commit()
        logger.info("Successfully set default images for all recipes")
        
        # Print number of recipes updated
        cursor.execute('SELECT COUNT(*) FROM recipes')
        total_recipes = cursor.fetchone()[0]
        logger.info(f"Total recipes in database: {total_recipes}")
        
    except Exception as e:
        logger.error(f"Error setting default images: {e}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    set_default_images() 