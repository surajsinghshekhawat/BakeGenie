"""
Script to list all recipe names in the database
"""

import sqlite3

def list_all_recipes():
    """List all recipe names in the database"""
    try:
        # Connect to database
        conn = sqlite3.connect('database/recipes.db')
        cursor = conn.cursor()
        
        # Get all recipes
        cursor.execute('SELECT name FROM recipes ORDER BY name')
        recipes = cursor.fetchall()
        
        # Print recipes
        print("\nList of all recipes in the database:")
        print("-" * 50)
        for i, (recipe_name,) in enumerate(recipes, 1):
            print(f"{i}. {recipe_name}")
        
        print(f"\nTotal recipes: {len(recipes)}")
        
        # Print the last 8 recipes separately
        print("\nLast 8 recipes:")
        print("-" * 50)
        for i, (recipe_name,) in enumerate(recipes[-8:], len(recipes)-7):
            print(f"{i}. {recipe_name}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    list_all_recipes() 