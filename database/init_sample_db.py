import sqlite3
import os
import logging

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
        
        # Insert sample recipes
        sample_recipes = [
            {
                'name': 'Classic Chocolate Cake',
                'description': 'A moist and rich chocolate cake that\'s perfect for any occasion.',
                'instructions': '1. Preheat oven to 350°F\n2. Mix dry ingredients\n3. Add wet ingredients\n4. Bake for 30 minutes',
                'image_path': '/static/images/default-recipe.jpg',
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
                'tips': '1. Make sure all ingredients are at room temperature\n2. Sift dry ingredients for a lighter texture\n3. Don\'t overmix the batter',
                'storage_instructions': 'Store in an airtight container at room temperature for up to 3 days',
                'equipment_needed': 'Mixing bowls, Whisk, Cake pan, Oven, Measuring cups',
                'temperature': '350°F',
                'source': 'Baking App Collection',
                'ingredients': [
                    {'name': 'All-purpose flour', 'amount': 2, 'unit': 'cups', 'is_optional': False},
                    {'name': 'Sugar', 'amount': 1.5, 'unit': 'cups', 'is_optional': False},
                    {'name': 'Cocoa powder', 'amount': 0.75, 'unit': 'cup', 'is_optional': False},
                    {'name': 'Eggs', 'amount': 2, 'unit': 'large', 'is_optional': False},
                    {'name': 'Milk', 'amount': 1, 'unit': 'cup', 'is_optional': False},
                    {'name': 'Vegetable oil', 'amount': 0.5, 'unit': 'cup', 'is_optional': False},
                    {'name': 'Vanilla extract', 'amount': 1, 'unit': 'tsp', 'is_optional': True}
                ]
            },
            {
                'name': 'Vanilla Cupcakes',
                'description': 'Light and fluffy vanilla cupcakes with buttercream frosting.',
                'instructions': '1. Preheat oven to 350°F\n2. Mix ingredients\n3. Fill cupcake liners\n4. Bake for 20 minutes',
                'image_path': '/static/images/default-recipe.jpg',
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
                'tips': '1. Use room temperature ingredients\n2. Don\'t overfill cupcake liners\n3. Let cool completely before frosting',
                'storage_instructions': 'Store in an airtight container at room temperature for up to 2 days',
                'equipment_needed': 'Mixing bowls, Whisk, Cupcake pan, Oven, Measuring cups',
                'temperature': '350°F',
                'source': 'Baking App Collection',
                'ingredients': [
                    {'name': 'All-purpose flour', 'amount': 1.5, 'unit': 'cups', 'is_optional': False},
                    {'name': 'Sugar', 'amount': 1, 'unit': 'cup', 'is_optional': False},
                    {'name': 'Eggs', 'amount': 2, 'unit': 'large', 'is_optional': False},
                    {'name': 'Milk', 'amount': 0.75, 'unit': 'cup', 'is_optional': False},
                    {'name': 'Butter', 'amount': 0.5, 'unit': 'cup', 'is_optional': False},
                    {'name': 'Vanilla extract', 'amount': 1, 'unit': 'tsp', 'is_optional': True}
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
                    name, description, instructions, image_path, dietary, difficulty,
                    serving_size, prep_time, cook_time, total_time,
                    calories, protein, carbs, fat, fiber, sugar,
                    cuisine_type, meal_type, author, rating, review_count,
                    tips, storage_instructions, equipment_needed, temperature, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recipe_data['name'], recipe_data['description'], recipe_data['instructions'],
                recipe_data['image_path'], recipe_data['dietary'], recipe_data['difficulty'],
                recipe_data['serving_size'], recipe_data['prep_time'], recipe_data['cook_time'],
                recipe_data['total_time'], recipe_data['calories'], recipe_data['protein'],
                recipe_data['carbs'], recipe_data['fat'], recipe_data['fiber'],
                recipe_data['sugar'], recipe_data['cuisine_type'], recipe_data['meal_type'],
                recipe_data['author'], recipe_data['rating'], recipe_data['review_count'],
                recipe_data['tips'], recipe_data['storage_instructions'],
                recipe_data['equipment_needed'], recipe_data['temperature'],
                recipe_data['source']
            ))
            
            # Get the recipe ID
            recipe_id = cursor.lastrowid
            
            # Insert ingredients
            for ingredient in ingredients:
                cursor.execute('''
                    INSERT INTO recipe_ingredients (
                        recipe_id, ingredient_name, amount, unit, is_optional
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    recipe_id, ingredient['name'],
                    ingredient['amount'], ingredient['unit'],
                    ingredient['is_optional']
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

if __name__ == "__main__":
    init_sample_db() 