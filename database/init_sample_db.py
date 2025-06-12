"""
Initialize the database with sample recipe data
"""

import sqlite3
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.sample_recipes import SAMPLE_RECIPES
from database.recipe_enhancer import enhance_recipe

def init_sample_db():
    # Connect to the database
    conn = sqlite3.connect('database/recipes.db')
    cursor = conn.cursor()

    # Create recipes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
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
    CREATE TABLE IF NOT EXISTS recipe_ingredients (
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

    # Clear existing data
    cursor.execute('DELETE FROM recipe_ingredients')
    cursor.execute('DELETE FROM recipes')

    # Insert sample recipes
    for recipe in SAMPLE_RECIPES:
        # Enhance recipe with additional details
        enhanced_recipe = enhance_recipe(recipe)
        
        cursor.execute('''
        INSERT INTO recipes (
            name, description, instructions, image_path, dietary, difficulty,
            serving_size, prep_time, cook_time, total_time, calories,
            protein, carbs, fat, fiber, sugar, cuisine_type, meal_type,
            author, rating, review_count, tips, storage_instructions,
            equipment_needed, temperature, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            enhanced_recipe['name'], enhanced_recipe['description'], enhanced_recipe['instructions'],
            enhanced_recipe.get('image_path', '/static/images/default-recipe.jpg'),
            enhanced_recipe.get('dietary', ''), enhanced_recipe.get('difficulty', ''),
            enhanced_recipe.get('serving_size', 1), enhanced_recipe.get('prep_time', 0),
            enhanced_recipe.get('cook_time', 0), enhanced_recipe.get('total_time', 0),
            enhanced_recipe.get('calories', 0), enhanced_recipe.get('protein', 0),
            enhanced_recipe.get('carbs', 0), enhanced_recipe.get('fat', 0),
            enhanced_recipe.get('fiber', 0), enhanced_recipe.get('sugar', 0),
            enhanced_recipe.get('cuisine_type', ''), enhanced_recipe.get('meal_type', ''),
            enhanced_recipe.get('author', 'BakeGenie'), enhanced_recipe.get('rating', 0),
            enhanced_recipe.get('review_count', 0), enhanced_recipe.get('tips', ''),
            enhanced_recipe.get('storage_instructions', ''),
            enhanced_recipe.get('equipment_needed', ''),
            enhanced_recipe.get('temperature', ''),
            enhanced_recipe.get('source', '')
        ))
        
        recipe_id = cursor.lastrowid
        
        # Insert ingredients
        for ingredient in enhanced_recipe['ingredients']:
            cursor.execute('''
            INSERT INTO recipe_ingredients (
                recipe_id, ingredient_name, amount, unit, notes, substitute,
                is_optional, category, preparation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recipe_id,
                ingredient['name'],
                ingredient['amount'],
                ingredient['unit'],
                ingredient.get('notes', ''),
                ingredient.get('substitute', ''),
                ingredient.get('is_optional', False),
                ingredient.get('category', ''),
                ingredient.get('preparation', '')
            ))

    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_sample_db()
    print("Database initialized with sample recipes!") 