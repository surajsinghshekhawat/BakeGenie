import sqlite3
import os

def check_database():
    # Check both databases
    databases = [
        ('Sample Database', 'database/recipes.db'),
        ('Kaggle Dataset', 'dataset_processing/datasets/baking_recipes.db')
    ]
    
    for db_name, db_path in databases:
        print(f"\nChecking {db_name} at {db_path}")
        if not os.path.exists(db_path):
            print(f"Database file not found: {db_path}")
            continue
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Tables: {[table[0] for table in tables]}")
            
            # Get recipe count
            cursor.execute("SELECT COUNT(*) FROM recipes")
            recipe_count = cursor.fetchone()[0]
            print(f"Total recipes: {recipe_count}")
            
            # Get sample recipe
            cursor.execute("SELECT * FROM recipes LIMIT 1")
            recipe = cursor.fetchone()
            if recipe:
                print("\nSample recipe columns:")
                cursor.execute("PRAGMA table_info(recipes)")
                columns = cursor.fetchall()
                for col in columns:
                    print(f"- {col[1]}: {col[2]}")
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Error accessing database: {e}")

if __name__ == "__main__":
    check_database() 