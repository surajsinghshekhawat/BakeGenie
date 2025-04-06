"""
Script to add sample recipes to the database
"""

import sqlite3
import os
import logging
from sample_recipes import SAMPLE_RECIPES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_image_path(recipe_name):
    """Generate image path for a recipe"""
    # Convert recipe name to lowercase and replace spaces with underscores
    image_name = recipe_name.lower().replace(' ', '_')
    return f'/static/images/recipes/{image_name}.jpg'

def add_sample_recipes():
    """Add sample recipes to the database"""
    try:
        # Connect to database
        conn = sqlite3.connect('database/recipes.db')
        cursor = conn.cursor()
        
        # Process each recipe
        for recipe_data in SAMPLE_RECIPES:
            # Prepare recipe data
            recipe_values = (
                recipe_data['name'],
                recipe_data['description'],
                recipe_data['instructions'],
                get_image_path(recipe_data['name']),  # Use recipe-specific image path
                'Vegetarian',  # Default dietary
                recipe_data['difficulty'],
                recipe_data['servings'],
                recipe_data['prep_time'],
                recipe_data['cook_time'],
                recipe_data['total_time'],
                recipe_data['calories'],
                recipe_data['protein'],
                recipe_data['carbs'],
                recipe_data['fat'],
                recipe_data['fiber'],
                recipe_data['sugar'],
                recipe_data['cuisine_type'],
                recipe_data['meal_type'],
                'Baking App',  # Default author
                recipe_data['rating'],
                recipe_data['review_count'],
                '',  # Default tips
                '',  # Default storage instructions
                '',  # Default equipment needed
                '',  # Default temperature
                'Sample Recipes'  # Default source
            )
            
            # Insert recipe
            cursor.execute('''
                INSERT INTO recipes (
                    name, description, instructions, image_path, dietary, difficulty,
                    serving_size, prep_time, cook_time, total_time,
                    calories, protein, carbs, fat, fiber, sugar,
                    cuisine_type, meal_type, author, rating, review_count,
                    tips, storage_instructions, equipment_needed, temperature, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', recipe_values)
            
            # Get the recipe ID
            recipe_id = cursor.lastrowid
            
            # Insert ingredients
            for ingredient in recipe_data['ingredients']:
                cursor.execute('''
                    INSERT INTO recipe_ingredients (
                        recipe_id, ingredient_name, amount, unit, is_optional
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    recipe_id,
                    ingredient['name'],
                    ingredient['amount'],
                    ingredient['unit'],
                    False  # Default is_optional
                ))
        
        # Commit changes
        conn.commit()
        logger.info(f"Successfully added {len(SAMPLE_RECIPES)} sample recipes to the database")
        
    except Exception as e:
        logger.error(f"Error adding sample recipes: {e}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_sample_recipes() 