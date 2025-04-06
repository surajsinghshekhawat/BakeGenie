import sqlite3
import os
import logging
from .sample_recipes import SAMPLE_RECIPES

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_sample_db():
    """Initialize the sample database with some basic recipes"""
    try:
        # Create database directory if it doesn't exist
        os.makedirs('database', exist_ok=True)
        
        # Create images directory if it doesn't exist
        os.makedirs('static/images/recipes', exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect('database/recipes.db')
        cursor = conn.cursor()
        
        # Drop existing tables if they exist
        cursor.execute('DROP TABLE IF EXISTS recipe_ingredients')
        cursor.execute('DROP TABLE IF EXISTS recipes')
        
        # Create recipes table
        cursor.execute('''
            CREATE TABLE recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                instructions TEXT,
                image_path TEXT,
                dietary TEXT,
                difficulty TEXT,
                serving_size INTEGER,
                prep_time INTEGER,
                cook_time INTEGER,
                total_time INTEGER,
                calories INTEGER,
                protein REAL,
                carbs REAL,
                fat REAL,
                fiber REAL,
                sugar REAL,
                cuisine_type TEXT,
                meal_type TEXT,
                author TEXT,
                rating REAL,
                review_count INTEGER,
                tips TEXT,
                storage_instructions TEXT,
                equipment_needed TEXT,
                temperature TEXT,
                source TEXT
            )
        ''')
        
        # Create recipe_ingredients table
        cursor.execute('''
            CREATE TABLE recipe_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                ingredient_name TEXT NOT NULL,
                amount REAL,
                unit TEXT,
                notes TEXT,
                substitute TEXT,
                is_optional BOOLEAN,
                category TEXT,
                preparation TEXT,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        
        # Insert sample recipes from sample_recipes.py
        for recipe_data in SAMPLE_RECIPES:
            # Remove ingredients from recipe data
            ingredients = recipe_data.pop('ingredients', [])
            
            # Generate image path
            image_name = recipe_data['name'].lower().replace(' ', '_') + '.jpg'
            image_path = f'/static/images/recipes/{image_name}'
            
            # Insert recipe
            cursor.execute('''
                INSERT INTO recipes (
                    name, description, instructions, image_path, dietary, difficulty,
                    serving_size, prep_time, cook_time, total_time,
                    calories, protein, carbs, fat, fiber, sugar,
                    cuisine_type, meal_type, author, rating, review_count,
                    tips, storage_instructions, equipment_needed, temperature, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recipe_data['name'], recipe_data.get('description', ''),
                recipe_data.get('instructions', ''), image_path,
                recipe_data.get('dietary', 'Non-Vegetarian'),  # Default to Non-Vegetarian if not specified
                recipe_data.get('difficulty', 'Medium'),
                recipe_data.get('servings', 4), recipe_data.get('prep_time', 30),
                recipe_data.get('cook_time', 30), recipe_data.get('total_time', 60),
                recipe_data.get('calories', 0), recipe_data.get('protein', 0),
                recipe_data.get('carbs', 0), recipe_data.get('fat', 0),
                recipe_data.get('fiber', 0), recipe_data.get('sugar', 0),
                recipe_data.get('cuisine_type', 'General'), recipe_data.get('meal_type', 'Main'),
                recipe_data.get('author', 'BakeGenie'), recipe_data.get('rating', 0),
                recipe_data.get('review_count', 0), recipe_data.get('tips', ''),
                recipe_data.get('storage_instructions', ''), recipe_data.get('equipment_needed', ''),
                recipe_data.get('temperature', ''), recipe_data.get('source', 'BakeGenie')
            ))
            
            # Get the recipe ID
            recipe_id = cursor.lastrowid
            
            # Insert ingredients
            for ingredient in ingredients:
                cursor.execute('''
                    INSERT INTO recipe_ingredients (
                        recipe_id, ingredient_name, amount, unit, notes,
                        substitute, is_optional, category, preparation
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    recipe_id,
                    ingredient['name'],
                    ingredient.get('amount', 0),
                    ingredient.get('unit', ''),
                    ingredient.get('notes', ''),
                    ingredient.get('substitute', ''),
                    ingredient.get('is_optional', False),
                    ingredient.get('category', ''),
                    ingredient.get('preparation', '')
                ))
        
        # Commit changes
        conn.commit()
        logger.info(f"Successfully initialized database with {len(SAMPLE_RECIPES)} recipes")
        
    except Exception as e:
        logger.error(f"Error initializing sample database: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    init_sample_db() 