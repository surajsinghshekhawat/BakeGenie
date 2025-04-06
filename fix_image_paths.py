import sqlite3
import os

def fix_image_paths():
    try:
        # Connect to database
        conn = sqlite3.connect('database/recipes.db')
        cursor = conn.cursor()
        
        # Get all recipes
        cursor.execute('SELECT id, name FROM recipes')
        recipes = cursor.fetchall()
        
        # Update paths
        for recipe_id, name in recipes:
            # Convert name to image filename format
            image_filename = name.lower().replace(' ', '_') + '.jpg'
            image_path = f'/static/images/recipes/{image_filename}'
            
            # Check if image exists
            full_path = os.path.join('static', 'images', 'recipes', image_filename)
            if os.path.exists(full_path):
                # Update database
                cursor.execute(
                    'UPDATE recipes SET image_path = ? WHERE id = ?',
                    (image_path, recipe_id)
                )
                print(f"Updated path for {name}: {image_path}")
            else:
                # Set default image if recipe image doesn't exist
                cursor.execute(
                    'UPDATE recipes SET image_path = ? WHERE id = ?',
                    ('/static/images/recipes/default.jpg', recipe_id)
                )
                print(f"Set default image for {name} (image not found)")
        
        # Commit changes
        conn.commit()
        print("\nDatabase update complete!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_image_paths()