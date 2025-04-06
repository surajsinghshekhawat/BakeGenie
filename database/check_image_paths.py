"""
Script to check image paths in the database
"""

import sqlite3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_image_paths():
    """Check image paths for all recipes"""
    try:
        # Connect to database
        conn = sqlite3.connect('database/recipes.db')
        cursor = conn.cursor()
        
        # Get all image paths
        cursor.execute('SELECT name, image_path FROM recipes')
        recipes = cursor.fetchall()
        
        # Print paths
        print("\nRecipe Image Paths:")
        print("-" * 50)
        for name, path in recipes:
            print(f"{name}: {path}")
        
        print(f"\nTotal recipes checked: {len(recipes)}")
        
    except Exception as e:
        logger.error(f"Error checking image paths: {e}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_image_paths() 