"""
Script to set default image paths for all ingredients
"""

import sqlite3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def set_default_ingredient_images():
    """Set default image paths for all ingredients"""
    try:
        # Connect to database
        conn = sqlite3.connect('database/ingredients.db')
        cursor = conn.cursor()
        
        # Update ALL ingredients with default image path
        cursor.execute('''
            UPDATE ingredients 
            SET image_path = '/static/images/ingredients/defualt_ingr.jpeg'
        ''')
        
        # Commit changes
        conn.commit()
        logger.info("Successfully set default images for all ingredients")
        
        # Print number of ingredients updated
        cursor.execute('SELECT COUNT(*) FROM ingredients')
        total_ingredients = cursor.fetchone()[0]
        logger.info(f"Total ingredients in database: {total_ingredients}")
        
        # Print all ingredients and their image paths to verify
        cursor.execute('SELECT name, image_path FROM ingredients')
        ingredients = cursor.fetchall()
        print("\nIngredient Image Paths:")
        print("-" * 50)
        for name, path in ingredients:
            print(f"{name}: {path}")
        
    except Exception as e:
        logger.error(f"Error setting default images: {e}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    set_default_ingredient_images() 