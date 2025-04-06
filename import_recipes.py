import os
import pandas as pd
import sqlite3
import logging
from kaggle.api.kaggle_api_extended import KaggleApi

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_dataset():
    """Download the Food.com dataset"""
    try:
        api = KaggleApi()
        api.authenticate()
        
        # Create datasets directory if it doesn't exist
        os.makedirs('datasets', exist_ok=True)
        
        # Download the dataset
        logger.info("Downloading Food.com dataset...")
        api.dataset_download_files(
            'shuyangli94/food-com-recipes-and-user-interactions',
            path='datasets',
            unzip=True
        )
        logger.info("Dataset downloaded successfully")
        
    except Exception as e:
        logger.error(f"Error downloading dataset: {e}")
        raise

def process_recipes():
    """Process the downloaded recipes and import them into our database"""
    try:
        # Read the recipes dataset
        recipes_df = pd.read_csv('datasets/RAW_recipes.csv')
        
        # Filter for baking recipes
        baking_keywords = [
            'bake', 'cake', 'bread', 'cookie', 'pastry', 'pie', 
            'muffin', 'cupcake', 'brownie', 'dessert'
        ]
        
        # Check if any of the keywords are in the name or cooking method
        baking_mask = recipes_df['name'].str.lower().str.contains('|'.join(baking_keywords), na=False)
        
        baking_recipes = recipes_df[baking_mask].copy()
        logger.info(f"Found {len(baking_recipes)} baking recipes")
        
        # Connect to our database
        conn = sqlite3.connect('database/recipes.db')
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM recipe_ingredients')
        cursor.execute('DELETE FROM recipes')
        
        # Process each recipe
        for _, recipe in baking_recipes.iterrows():
            try:
                # Insert recipe
                cursor.execute('''
                    INSERT INTO recipes (
                        name, description, instructions, dietary,
                        difficulty, serving_size, prep_time, cook_time,
                        total_time, calories, rating, review_count,
                        source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    recipe['name'],
                    f"A delicious {recipe['name']} recipe",  # Default description
                    recipe['steps'],
                    'vegetarian' if 'vegetarian' in recipe['tags'].lower() else '',
                    'medium',  # Default difficulty
                    recipe['n_steps'],  # Using number of steps as serving size
                    recipe['minutes'],  # Using total minutes as prep time
                    0,  # Default cook time
                    recipe['minutes'],  # Total time
                    0,  # Default calories
                    recipe['rating'],
                    recipe['n_steps'],  # Using number of steps as review count
                    'Food.com'
                ))
                
                recipe_id = cursor.lastrowid
                
                # Process ingredients
                ingredients = eval(recipe['ingredients'])  # Convert string list to actual list
                for ingredient in ingredients:
                    cursor.execute('''
                        INSERT INTO recipe_ingredients (
                            recipe_id, ingredient_name, amount, unit
                        ) VALUES (?, ?, ?, ?)
                    ''', (
                        recipe_id,
                        ingredient,
                        1.0,  # Default amount
                        'unit'  # Default unit
                    ))
                
            except Exception as e:
                logger.error(f"Error processing recipe {recipe['name']}: {e}")
                continue
        
        # Commit changes
        conn.commit()
        logger.info("Recipe import completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing recipes: {e}")
        raise
    finally:
        if conn:
            conn.close()

def main():
    """Main function to run the import process"""
    try:
        download_dataset()
        process_recipes()
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        raise

if __name__ == "__main__":
    main() 