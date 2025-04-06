"""
Database for recipes and their details
"""

import sqlite3
import json
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = os.path.join('database', 'recipes.db')

def get_db_connection():
    """Get a database connection"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def get_all_recipes():
    """Get all recipes with their ingredients"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all recipes ordered by rating and review count
        cursor.execute('''
            SELECT * FROM recipes 
            ORDER BY rating DESC, review_count DESC
        ''')
        recipes = [dict(row) for row in cursor.fetchall()]
        
        # Get ingredients for each recipe
        for recipe in recipes:
            cursor.execute('''
                SELECT * FROM recipe_ingredients 
                WHERE recipe_id = ?
            ''', (recipe['id'],))
            recipe['ingredients'] = [dict(row) for row in cursor.fetchall()]
        
        return recipes
    except sqlite3.Error as e:
        logger.error(f"Error getting recipes: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_recipe_by_id(recipe_id: int):
    """Get a specific recipe by its ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the recipe
        cursor.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
        recipe = cursor.fetchone()
        
        if not recipe:
            logger.warning(f"Recipe {recipe_id} not found")
            return None
            
        recipe = dict(recipe)
        
        # Get ingredients
        cursor.execute('SELECT * FROM recipe_ingredients WHERE recipe_id = ?', (recipe_id,))
        recipe['ingredients'] = [dict(row) for row in cursor.fetchall()]
        
        # Ensure required fields exist
        if 'image_path' not in recipe:
            recipe['image_path'] = '/static/images/default-recipe.jpg'
        if 'ingredients' not in recipe:
            recipe['ingredients'] = []
        if 'instructions' not in recipe:
            recipe['instructions'] = ''
        if 'description' not in recipe:
            recipe['description'] = ''
        if 'dietary' not in recipe:
            recipe['dietary'] = ''
        if 'difficulty' not in recipe:
            recipe['difficulty'] = ''
        if 'serving_size' not in recipe:
            recipe['serving_size'] = 1
        if 'prep_time' not in recipe:
            recipe['prep_time'] = 0
        if 'cook_time' not in recipe:
            recipe['cook_time'] = 0
        if 'total_time' not in recipe:
            recipe['total_time'] = 0
        if 'calories' not in recipe:
            recipe['calories'] = 0
        if 'protein' not in recipe:
            recipe['protein'] = 0
        if 'carbs' not in recipe:
            recipe['carbs'] = 0
        if 'fat' not in recipe:
            recipe['fat'] = 0
        if 'fiber' not in recipe:
            recipe['fiber'] = 0
        if 'sugar' not in recipe:
            recipe['sugar'] = 0
        if 'cuisine_type' not in recipe:
            recipe['cuisine_type'] = ''
        if 'meal_type' not in recipe:
            recipe['meal_type'] = ''
        if 'author' not in recipe:
            recipe['author'] = ''
        if 'rating' not in recipe:
            recipe['rating'] = 0
        if 'review_count' not in recipe:
            recipe['review_count'] = 0
        if 'tips' not in recipe:
            recipe['tips'] = ''
        if 'storage_instructions' not in recipe:
            recipe['storage_instructions'] = ''
        if 'equipment_needed' not in recipe:
            recipe['equipment_needed'] = ''
        if 'temperature' not in recipe:
            recipe['temperature'] = ''
        if 'source' not in recipe:
            recipe['source'] = ''
            
        return recipe
    except sqlite3.Error as e:
        logger.error(f"Error getting recipe {recipe_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def search_recipes(query: str = '', dietary: str = '', difficulty: str = '', cuisine_type: str = '', meal_type: str = ''):
    """Search recipes with various filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build the query
        sql = 'SELECT * FROM recipes WHERE 1=1'
        params = []
        
        if query:
            sql += ' AND (name LIKE ? OR description LIKE ? OR instructions LIKE ?)'
            params.extend([f'%{query}%'] * 3)
        
        if dietary:
            sql += ' AND dietary = ?'
            params.append(dietary)
            
        if difficulty:
            sql += ' AND difficulty = ?'
            params.append(difficulty)
            
        if cuisine_type:
            sql += ' AND cuisine_type = ?'
            params.append(cuisine_type)
            
        if meal_type:
            sql += ' AND meal_type = ?'
            params.append(meal_type)
            
        sql += ' ORDER BY rating DESC, review_count DESC'
        
        # Execute the query
        cursor.execute(sql, params)
        recipes = [dict(row) for row in cursor.fetchall()]
        
        # Get ingredients for each recipe
        for recipe in recipes:
            cursor.execute('SELECT * FROM recipe_ingredients WHERE recipe_id = ?', (recipe['id'],))
            recipe['ingredients'] = [dict(row) for row in cursor.fetchall()]
        
        return recipes
    except sqlite3.Error as e:
        logger.error(f"Error searching recipes: {e}")
        return []
    finally:
        if conn:
            conn.close()

def find_recipes_by_ingredients(ingredients: List[str]):
    """Find recipes that can be made with given ingredients"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all recipes and their ingredients
        recipes = get_all_recipes()
        matching_recipes = []
        
        for recipe in recipes:
            recipe_ingredients = set(ing['ingredient_name'].lower() for ing in recipe['ingredients'])
            provided_ingredients = set(ing.lower() for ing in ingredients)
            
            # Calculate match percentage
            if recipe_ingredients:
                matching = recipe_ingredients.intersection(provided_ingredients)
                match_percentage = (len(matching) / len(recipe_ingredients)) * 100
                missing = recipe_ingredients - provided_ingredients
                
                matching_recipes.append({
                    'id': recipe['id'],
                    'name': recipe['name'],
                    'match_percentage': round(match_percentage, 1),
                    'matching_ingredients': list(matching),
                    'missing_ingredients': list(missing)
                })
        
        # Sort by match percentage
        matching_recipes.sort(key=lambda x: x['match_percentage'], reverse=True)
        return matching_recipes
        
    except sqlite3.Error as e:
        logger.error(f"Error finding recipes by ingredients: {e}")
        return []
    finally:
        if conn:
            conn.close()

def init_recipes_db():
    """Initialize the database with sample recipes"""
    try:
        # Create database directory if it doesn't exist
        os.makedirs('database', exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
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
        
        # Insert sample recipes
        sample_recipes = [
            {
                'name': 'Classic Chocolate Cake',
                'description': 'A moist and rich chocolate cake that\'s perfect for any occasion.',
                'instructions': '1. Preheat oven to 350°F\n2. Mix dry ingredients\n3. Add wet ingredients\n4. Bake for 30 minutes',
                'dietary': 'Vegetarian',
                'difficulty': 'Medium',
                'serving_size': 8,
                'prep_time': 20,
                'cook_time': 30,
                'total_time': 50,
                'calories': 350,
                'protein': 5,
                'carbs': 45,
                'fat': 20,
                'fiber': 2,
                'sugar': 30,
                'cuisine_type': 'American',
                'meal_type': 'Dessert',
                'author': 'Baking App',
                'rating': 4.5,
                'review_count': 100,
                'ingredients': [
                    {'name': 'All-purpose flour', 'amount': 2, 'unit': 'cups'},
                    {'name': 'Sugar', 'amount': 1.5, 'unit': 'cups'},
                    {'name': 'Cocoa powder', 'amount': 0.75, 'unit': 'cup'},
                    {'name': 'Eggs', 'amount': 2, 'unit': 'large'},
                    {'name': 'Milk', 'amount': 1, 'unit': 'cup'},
                    {'name': 'Vegetable oil', 'amount': 0.5, 'unit': 'cup'},
                    {'name': 'Vanilla extract', 'amount': 1, 'unit': 'tsp'}
                ]
            },
            {
                'name': 'Vanilla Cupcakes',
                'description': 'Light and fluffy vanilla cupcakes with buttercream frosting.',
                'instructions': '1. Preheat oven to 350°F\n2. Mix ingredients\n3. Fill cupcake liners\n4. Bake for 20 minutes',
                'dietary': 'Vegetarian',
                'difficulty': 'Easy',
                'serving_size': 12,
                'prep_time': 15,
                'cook_time': 20,
                'total_time': 35,
                'calories': 200,
                'protein': 3,
                'carbs': 30,
                'fat': 8,
                'fiber': 1,
                'sugar': 20,
                'cuisine_type': 'American',
                'meal_type': 'Dessert',
                'author': 'Baking App',
                'rating': 4.3,
                'review_count': 80,
                'ingredients': [
                    {'name': 'All-purpose flour', 'amount': 1.5, 'unit': 'cups'},
                    {'name': 'Sugar', 'amount': 1, 'unit': 'cup'},
                    {'name': 'Eggs', 'amount': 2, 'unit': 'large'},
                    {'name': 'Milk', 'amount': 0.75, 'unit': 'cup'},
                    {'name': 'Butter', 'amount': 0.5, 'unit': 'cup'},
                    {'name': 'Vanilla extract', 'amount': 1, 'unit': 'tsp'}
                ]
            }
        ]
        
        # Insert recipes and their ingredients
        for recipe_data in sample_recipes:
            # Remove ingredients from recipe data
            ingredients = recipe_data.pop('ingredients')
            
            # Insert recipe
            cursor.execute('''
                INSERT INTO recipes (
                    name, description, instructions, dietary, difficulty,
                    serving_size, prep_time, cook_time, total_time,
                    calories, protein, carbs, fat, fiber, sugar,
                    cuisine_type, meal_type, author, rating, review_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recipe_data['name'], recipe_data['description'], recipe_data['instructions'],
                recipe_data['dietary'], recipe_data['difficulty'], recipe_data['serving_size'],
                recipe_data['prep_time'], recipe_data['cook_time'], recipe_data['total_time'],
                recipe_data['calories'], recipe_data['protein'], recipe_data['carbs'],
                recipe_data['fat'], recipe_data['fiber'], recipe_data['sugar'],
                recipe_data['cuisine_type'], recipe_data['meal_type'], recipe_data['author'],
                recipe_data['rating'], recipe_data['review_count']
            ))
            
            # Get the recipe ID
            recipe_id = cursor.lastrowid
            
            # Insert ingredients
            for ingredient in ingredients:
                cursor.execute('''
                    INSERT INTO recipe_ingredients (
                        recipe_id, ingredient_name, amount, unit
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    recipe_id, ingredient['name'],
                    ingredient['amount'], ingredient['unit']
                ))
        
        # Commit changes
        conn.commit()
        logger.info("Sample database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing sample database: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Initialize the database when this module is imported
if __name__ == "__main__":
    init_recipes_db()

