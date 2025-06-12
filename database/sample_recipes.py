"""
Sample recipe data for initializing the database
"""

import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample recipes
SAMPLE_RECIPES = [
    {
        "name": "Classic Chocolate Chip Cookies",
        "description": "Delicious homemade chocolate chip cookies that are soft and chewy on the inside with a slight crisp on the outside.",
        "instructions": "1. Preheat oven to 350°F (175°C)\n2. Cream together butter and sugars\n3. Add eggs and vanilla\n4. Mix in dry ingredients\n5. Fold in chocolate chips\n6. Bake for 10-12 minutes",
        "dietary": "Vegetarian",
        "difficulty": "Easy",
        "serving_size": 24,
        "prep_time": 15,
        "cook_time": 12,
        "total_time": 27,
        "calories": 150,
        "protein": 2,
        "carbs": 20,
        "fat": 7,
        "fiber": 1,
        "sugar": 12,
        "cuisine_type": "American",
        "meal_type": "Dessert",
        "pro_tips": "• For chewier cookies, slightly underbake them\n• Let the dough rest in the fridge for 24 hours for better flavor\n• Use room temperature butter for best results",
        "storage_instructions": "Store in an airtight container at room temperature for up to 1 week. Can be frozen for up to 3 months.",
        "equipment_needed": "• Mixing bowls\n• Electric mixer\n• Baking sheets\n• Wire cooling rack\n• Measuring cups and spoons",
        "temperature": "350°F (175°C)",
        "author": "BakeGenie",
        "rating": 4.8,
        "review_count": 156,
        "ingredients": [
            {
                "name": "All-purpose flour",
                "amount": 2.25,
                "unit": "cups",
                "notes": "Sifted",
                "category": "Dry ingredients",
                "is_optional": False
            },
            {
                "name": "Butter",
                "amount": 1,
                "unit": "cup",
                "notes": "Room temperature",
                "substitute": "Margarine (not recommended)",
                "category": "Dairy",
                "is_optional": False
            },
            {
                "name": "Brown sugar",
                "amount": 0.75,
                "unit": "cup",
                "notes": "Packed",
                "category": "Sweeteners",
                "is_optional": False
            },
            {
                "name": "White sugar",
                "amount": 0.75,
                "unit": "cup",
                "category": "Sweeteners",
                "is_optional": False
            },
            {
                "name": "Eggs",
                "amount": 2,
                "unit": "large",
                "notes": "Room temperature",
                "category": "Dairy",
                "is_optional": False
            },
            {
                "name": "Vanilla extract",
                "amount": 1,
                "unit": "tsp",
                "category": "Flavorings",
                "is_optional": False
            },
            {
                "name": "Chocolate chips",
                "amount": 2,
                "unit": "cups",
                "notes": "Semi-sweet recommended",
                "category": "Add-ins",
                "is_optional": False
            }
        ]
    },
    {
        "name": "Classic Vanilla Cake",
        "description": "A moist and fluffy vanilla cake perfect for any celebration.",
        "instructions": "1. Preheat oven to 350°F (175°C)\n2. Cream butter and sugar\n3. Add eggs one at a time\n4. Mix in dry ingredients\n5. Add milk and vanilla\n6. Bake for 25-30 minutes",
        "dietary": "Vegetarian",
        "difficulty": "Medium",
        "serving_size": 12,
        "prep_time": 20,
        "cook_time": 30,
        "total_time": 50,
        "calories": 320,
        "protein": 4,
        "carbs": 45,
        "fat": 14,
        "fiber": 1,
        "sugar": 30,
        "cuisine_type": "American",
        "meal_type": "Dessert",
        "pro_tips": "• Ensure all ingredients are at room temperature\n• Don't overmix the batter\n• Use cake flour for a lighter texture",
        "storage_instructions": "Store in an airtight container at room temperature for up to 3 days. Can be frozen for up to 3 months.",
        "equipment_needed": "• Mixing bowls\n• Electric mixer\n• 9-inch cake pans\n• Wire cooling rack\n• Measuring cups and spoons",
        "temperature": "350°F (175°C)",
        "author": "BakeGenie",
        "rating": 4.7,
        "review_count": 89,
        "ingredients": [
            {
                "name": "All-purpose flour",
                "amount": 2.5,
                "unit": "cups",
                "notes": "Sifted",
                "category": "Dry ingredients",
                "is_optional": False
            },
            {
                "name": "Butter",
                "amount": 1,
                "unit": "cup",
                "notes": "Room temperature",
                "category": "Dairy",
                "is_optional": False
            },
            {
                "name": "Sugar",
                "amount": 2,
                "unit": "cups",
                "category": "Sweeteners",
                "is_optional": False
            },
            {
                "name": "Eggs",
                "amount": 4,
                "unit": "large",
                "notes": "Room temperature",
                "category": "Dairy",
                "is_optional": False
            },
            {
                "name": "Milk",
                "amount": 1,
                "unit": "cup",
                "notes": "Room temperature",
                "category": "Dairy",
                "is_optional": False
            },
            {
                "name": "Vanilla extract",
                "amount": 2,
                "unit": "tsp",
                "category": "Flavorings",
                "is_optional": False
            }
        ]
    },
    {
        "name": "Homemade Sourdough Bread",
        "description": "Traditional sourdough bread with a perfect crust and tangy flavor.",
        "instructions": "1. Feed starter\n2. Mix ingredients\n3. Knead dough\n4. Bulk ferment\n5. Shape and proof\n6. Bake at 450°F",
        "dietary": "Vegetarian",
        "difficulty": "Hard",
        "serving_size": 16,
        "prep_time": 30,
        "cook_time": 45,
        "total_time": 24,
        "calories": 180,
        "protein": 6,
        "carbs": 35,
        "fat": 1,
        "fiber": 2,
        "sugar": 1,
        "cuisine_type": "European",
        "meal_type": "Bread",
        "pro_tips": "• Use warm water (110°F) to activate starter properly\n• Knead until the dough is smooth and elastic\n• Let dough rise in a warm, draft-free place\n• Score the top before baking to control expansion\n• Tap the bottom - it should sound hollow when done",
        "storage_instructions": "• Store at room temperature in a paper bag for 2-3 days\n• For longer storage, wrap tightly and freeze for up to 3 months\n• Slice before freezing for easier portioning\n• Thaw at room temperature or toast directly from frozen",
        "equipment_needed": "• Large mixing bowl\n• Measuring cups and spoons\n• Bread pan or Dutch oven\n• Kitchen scale (optional)\n• Clean kitchen towel\n• Wire cooling rack",
        "temperature": "450°F (230°C)",
        "author": "BakeGenie",
        "rating": 4.6,
        "review_count": 78,
        "ingredients": [
            {"name": "Bread flour", "amount": 4, "unit": "cups"},
            {"name": "Active sourdough starter", "amount": 1, "unit": "cup"},
            {"name": "Water", "amount": 1.5, "unit": "cups"},
            {"name": "Salt", "amount": 2, "unit": "tsp"}
        ]
    },
    {
        "name": "Fudgy Chocolate Brownies",
        "description": "Rich and decadent chocolate brownies with a fudgy center.",
        "instructions": "1. Preheat oven to 350°F\n2. Melt chocolate and butter\n3. Mix in sugar and eggs\n4. Add dry ingredients\n5. Bake for 25-30 minutes",
        "dietary": "Vegetarian",
        "difficulty": "Medium",
        "serving_size": 16,
        "prep_time": 15,
        "cook_time": 30,
        "total_time": 45,
        "calories": 280,
        "protein": 4,
        "carbs": 35,
        "fat": 16,
        "fiber": 2,
        "sugar": 25,
        "cuisine_type": "American",
        "meal_type": "Dessert",
        "pro_tips": "• Use high-quality dark chocolate for best results\n• Don't overbake - the center should be slightly underdone\n• Let cool completely before cutting\n• Use a hot knife for clean cuts\n• Line the pan with parchment paper for easy removal",
        "storage_instructions": "• Store in an airtight container at room temperature for up to 1 week\n• Can be frozen for up to 3 months\n• Thaw at room temperature before serving\n• Reheat briefly in microwave for a warm, gooey treat",
        "equipment_needed": "• Mixing bowls\n• Double boiler or microwave-safe bowl\n• 9x9 inch baking pan\n• Parchment paper\n• Wire cooling rack\n• Measuring cups and spoons",
        "temperature": "350°F (175°C)",
        "author": "BakeGenie",
        "rating": 4.9,
        "review_count": 203,
        "ingredients": [
            {"name": "Dark chocolate", "amount": 8, "unit": "oz"},
            {"name": "Butter", "amount": 1, "unit": "cup"},
            {"name": "Sugar", "amount": 2, "unit": "cups"},
            {"name": "Eggs", "amount": 4, "unit": "large"},
            {"name": "All-purpose flour", "amount": 1, "unit": "cup"},
            {"name": "Cocoa powder", "amount": 0.5, "unit": "cup"}
        ]
    },
    {
        "name": "Buttery Croissants",
        "description": "Flaky, buttery croissants that are perfect for breakfast or brunch.",
        "instructions": "1. Make dough\n2. Create butter block\n3. Lamination process\n4. Shape croissants\n5. Proof and bake",
        "dietary": "Vegetarian",
        "difficulty": "Hard",
        "serving_size": 12,
        "prep_time": 45,
        "cook_time": 20,
        "total_time": 4,
        "calories": 320,
        "protein": 6,
        "carbs": 35,
        "fat": 18,
        "fiber": 2,
        "sugar": 4,
        "cuisine_type": "French",
        "meal_type": "Breakfast",
        "pro_tips": "• Keep butter cold during lamination\n• Don't rush the proofing process\n• Use high-quality butter\n• Roll dough evenly\n• Score tops before baking",
        "storage_instructions": "• Best served fresh\n• Store in airtight container for 1-2 days\n• Reheat in oven for 5 minutes\n• Freeze unbaked for up to 1 month",
        "equipment_needed": "• Stand mixer\n• Rolling pin\n• Pastry brush\n• Baking sheets\n• Parchment paper\n• Sharp knife",
        "temperature": "400°F (200°C)",
        "author": "BakeGenie",
        "rating": 4.8,
        "review_count": 92,
        "ingredients": [
            {"name": "All-purpose flour", "amount": 4, "unit": "cups"},
            {"name": "Butter", "amount": 1.5, "unit": "cups"},
            {"name": "Milk", "amount": 1, "unit": "cup"},
            {"name": "Yeast", "amount": 2.25, "unit": "tsp"},
            {"name": "Sugar", "amount": 0.25, "unit": "cup"},
            {"name": "Salt", "amount": 1, "unit": "tsp"}
        ]
    },
    {
        "name": "Cinnamon Rolls",
        "description": "Soft and fluffy cinnamon rolls with cream cheese frosting.",
        "instructions": "1. Make dough\n2. Roll out and add filling\n3. Roll up and slice\n4. Let rise\n5. Bake and frost",
        "dietary": "Vegetarian",
        "difficulty": "Medium",
        "serving_size": 12,
        "prep_time": 30,
        "cook_time": 25,
        "total_time": 3,
        "calories": 380,
        "protein": 5,
        "carbs": 45,
        "fat": 20,
        "fiber": 2,
        "sugar": 25,
        "cuisine_type": "American",
        "meal_type": "Breakfast",
        "pro_tips": "• Use warm milk to activate yeast\n• Don't overfill with cinnamon sugar\n• Let rise in a warm place\n• Frost while still warm\n• Use dental floss to slice cleanly",
        "storage_instructions": "• Best served fresh\n• Store in airtight container for 2-3 days\n• Reheat in microwave for 20 seconds\n• Freeze unfrosted for up to 1 month",
        "equipment_needed": "• Stand mixer\n• Rolling pin\n• 9x13 inch pan\n• Mixing bowls\n• Measuring cups and spoons",
        "temperature": "375°F (190°C)",
        "author": "BakeGenie",
        "rating": 4.9,
        "review_count": 145,
        "ingredients": [
            {"name": "All-purpose flour", "amount": 4, "unit": "cups"},
            {"name": "Milk", "amount": 1, "unit": "cup"},
            {"name": "Butter", "amount": 0.5, "unit": "cup"},
            {"name": "Yeast", "amount": 2.25, "unit": "tsp"},
            {"name": "Cinnamon", "amount": 2, "unit": "tbsp"},
            {"name": "Brown sugar", "amount": 0.75, "unit": "cup"}
        ]
    },
    {
        "name": "Apple Pie",
        "description": "Classic apple pie with a flaky crust and sweet-tart filling.",
        "instructions": "1. Make pie crust\n2. Prepare apple filling\n3. Assemble pie\n4. Add lattice top\n5. Bake until golden",
        "dietary": "Vegetarian",
        "difficulty": "Medium",
        "serving_size": 8,
        "prep_time": 45,
        "cook_time": 60,
        "total_time": 2,
        "calories": 350,
        "protein": 4,
        "carbs": 45,
        "fat": 18,
        "fiber": 3,
        "sugar": 25,
        "cuisine_type": "American",
        "meal_type": "Dessert",
        "pro_tips": "• Use a mix of tart and sweet apples\n• Pre-cook filling to prevent soggy crust\n• Keep butter cold for flaky crust\n• Vent top crust properly\n• Let cool completely before slicing",
        "storage_instructions": "• Store at room temperature for 2-3 days\n• Refrigerate for up to 1 week\n• Freeze unbaked for up to 3 months\n• Reheat in oven for 10 minutes",
        "equipment_needed": "• Food processor\n• Rolling pin\n• 9-inch pie pan\n• Pastry brush\n• Sharp knife\n• Mixing bowls",
        "temperature": "375°F (190°C)",
        "author": "BakeGenie",
        "rating": 4.7,
        "review_count": 112,
        "ingredients": [
            {"name": "All-purpose flour", "amount": 2.5, "unit": "cups"},
            {"name": "Butter", "amount": 1, "unit": "cup"},
            {"name": "Apples", "amount": 6, "unit": "large"},
            {"name": "Sugar", "amount": 0.75, "unit": "cup"},
            {"name": "Cinnamon", "amount": 1, "unit": "tbsp"},
            {"name": "Lemon juice", "amount": 1, "unit": "tbsp"}
        ]
    },
    {
        "name": "Pizza Dough",
        "description": "Perfect homemade pizza dough that's crispy on the outside and chewy on the inside.",
        "instructions": "1. Mix ingredients\n2. Knead dough\n3. Let rise\n4. Shape and top\n5. Bake at high heat",
        "dietary": "Vegetarian",
        "difficulty": "Medium",
        "serving_size": 4,
        "prep_time": 20,
        "cook_time": 15,
        "total_time": 2,
        "calories": 280,
        "protein": 8,
        "carbs": 45,
        "fat": 6,
        "fiber": 2,
        "sugar": 1,
        "cuisine_type": "Italian",
        "meal_type": "Main Course",
        "pro_tips": "• Use warm water to activate yeast\n• Don't over-knead the dough\n• Let rise in a warm place\n• Preheat oven with pizza stone\n• Stretch dough by hand for best texture",
        "storage_instructions": "• Best used fresh\n• Refrigerate for up to 3 days\n• Freeze for up to 3 months\n• Thaw in refrigerator overnight",
        "equipment_needed": "• Stand mixer\n• Pizza stone\n• Rolling pin\n• Pizza peel\n• Mixing bowls\n• Measuring cups",
        "temperature": "500°F (260°C)",
        "author": "BakeGenie",
        "rating": 4.8,
        "review_count": 167,
        "ingredients": [
            {"name": "All-purpose flour", "amount": 3, "unit": "cups"},
            {"name": "Yeast", "amount": 2.25, "unit": "tsp"},
            {"name": "Olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "Salt", "amount": 1, "unit": "tsp"},
            {"name": "Sugar", "amount": 1, "unit": "tsp"},
            {"name": "Warm water", "amount": 1, "unit": "cup"}
        ]
    },
    {
        "name": "Chocolate Mousse",
        "description": "Light and airy chocolate mousse that melts in your mouth.",
        "instructions": "1. Melt chocolate\n2. Whip egg whites\n3. Fold together\n4. Chill\n5. Serve with whipped cream",
        "dietary": "Vegetarian",
        "difficulty": "Medium",
        "serving_size": 6,
        "prep_time": 30,
        "cook_time": 0,
        "total_time": 4,
        "calories": 320,
        "protein": 6,
        "carbs": 25,
        "fat": 22,
        "fiber": 3,
        "sugar": 20,
        "cuisine_type": "French",
        "meal_type": "Dessert",
        "pro_tips": "• Use high-quality dark chocolate\n• Don't over-whip the cream\n• Fold gently to maintain air\n• Chill for at least 4 hours\n• Serve in chilled glasses",
        "storage_instructions": "• Keep refrigerated for up to 3 days\n• Don't freeze\n• Serve chilled\n• Top with fresh berries",
        "equipment_needed": "• Double boiler\n• Electric mixer\n• Mixing bowls\n• Rubber spatula\n• Serving glasses\n• Measuring cups",
        "temperature": "N/A",
        "author": "BakeGenie",
        "rating": 4.9,
        "review_count": 89,
        "ingredients": [
            {"name": "Dark chocolate", "amount": 8, "unit": "oz"},
            {"name": "Heavy cream", "amount": 2, "unit": "cups"},
            {"name": "Eggs", "amount": 4, "unit": "large"},
            {"name": "Sugar", "amount": 0.25, "unit": "cup"},
            {"name": "Vanilla extract", "amount": 1, "unit": "tsp"},
            {"name": "Salt", "amount": 0.25, "unit": "tsp"}
        ]
    }
]

def create_sample_database():
    """Create a sample database with common recipes"""
    db_path = os.path.join(os.path.dirname(__file__), 'recipes.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create recipes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            instructions TEXT NOT NULL,
            prep_time INTEGER,
            cook_time INTEGER,
            total_time INTEGER,
            servings INTEGER,
            difficulty TEXT,
            cuisine_type TEXT,
            meal_type TEXT,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            fiber REAL,
            sugar REAL,
            rating REAL,
            review_count INTEGER
        )
        ''')
        
        # Create ingredients table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            name TEXT NOT NULL,
            amount REAL,
            unit TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
        ''')
        
        # Clear existing data
        cursor.execute('DELETE FROM ingredients')
        cursor.execute('DELETE FROM recipes')
        
        # Insert sample recipes
        for recipe in SAMPLE_RECIPES:
            cursor.execute('''
            INSERT INTO recipes (
                name, description, instructions, prep_time, cook_time, total_time,
                servings, difficulty, cuisine_type, meal_type, calories, protein,
                carbs, fat, fiber, sugar, rating, review_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recipe['name'], recipe['description'], recipe['instructions'],
                recipe['prep_time'], recipe['cook_time'], recipe['total_time'],
                recipe['serving_size'], recipe['difficulty'], recipe['cuisine_type'],
                recipe['meal_type'], recipe['calories'], recipe['protein'],
                recipe['carbs'], recipe['fat'], recipe['fiber'], recipe['sugar'],
                recipe['rating'], recipe['review_count']
            ))
            
            recipe_id = cursor.lastrowid
            
            # Insert ingredients
            for ingredient in recipe['ingredients']:
                cursor.execute('''
                INSERT INTO ingredients (recipe_id, name, amount, unit)
                VALUES (?, ?, ?, ?)
                ''', (recipe_id, ingredient['name'], ingredient['amount'], ingredient['unit']))
        
        conn.commit()
        logger.info(f"Created sample database with {len(SAMPLE_RECIPES)} recipes at {db_path}")
        
    except Exception as e:
        logger.error(f"Error creating sample database: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    create_sample_database()
