"""
Dataset processor for downloading and processing recipe datasets from Kaggle
"""

import os
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Any
import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatasetProcessor:
    def __init__(self):
        """Initialize the dataset processor"""
        self.datasets_dir = Path('datasets')
        self.datasets_dir.mkdir(exist_ok=True)
        
        # Initialize Kaggle API
        try:
            self.api = KaggleApi()
            self.api.authenticate()
            logger.info("Successfully authenticated with Kaggle API")
        except Exception as e:
            logger.error(f"Failed to authenticate with Kaggle API: {e}")
            raise
    
    def download_dataset(self, dataset_name: str, dataset_path: str):
        """Download a dataset from Kaggle"""
        try:
            logger.info(f"Downloading dataset: {dataset_name}")
            self.api.dataset_download_files(
                dataset_path,
                path=self.datasets_dir / dataset_name,
                unzip=True
            )
            logger.info(f"Successfully downloaded {dataset_name}")
        except Exception as e:
            logger.error(f"Error downloading dataset {dataset_name}: {e}")
            raise
    
    def clean_text(self, text: str) -> str:
        """Clean text data"""
        if pd.isna(text):
            return ""
        return str(text).strip()
    
    def clean_numeric(self, value: Any, default: Any = 0) -> Any:
        """Clean numeric data"""
        try:
            if pd.isna(value):
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _estimate_nutritional_values(self, ingredients: List[Dict[str, Any]]) -> Dict[str, float]:
        """Estimate nutritional values based on ingredients"""
        # Common ingredient nutritional values (per 100g)
        ingredient_nutrition = {
            'flour': {'calories': 364, 'protein': 10, 'carbs': 76, 'fat': 1, 'fiber': 2, 'sugar': 0.3},
            'sugar': {'calories': 387, 'protein': 0, 'carbs': 100, 'fat': 0, 'fiber': 0, 'sugar': 100},
            'butter': {'calories': 717, 'protein': 0.9, 'carbs': 0.1, 'fat': 81, 'fiber': 0, 'sugar': 0.1},
            'egg': {'calories': 143, 'protein': 13, 'carbs': 0.7, 'fat': 10, 'fiber': 0, 'sugar': 0.4},
            'milk': {'calories': 42, 'protein': 3.4, 'carbs': 4.8, 'fat': 1, 'fiber': 0, 'sugar': 4.8},
            'chocolate': {'calories': 546, 'protein': 5.5, 'carbs': 61, 'fat': 31, 'fiber': 7, 'sugar': 48},
            'fruit': {'calories': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2, 'fiber': 2.4, 'sugar': 10},
            'nuts': {'calories': 607, 'protein': 20, 'carbs': 21, 'fat': 54, 'fiber': 7, 'sugar': 4.3},
            'default': {'calories': 100, 'protein': 2, 'carbs': 10, 'fat': 5, 'fiber': 1, 'sugar': 2}
        }

        # Unit conversions (to grams)
        unit_conversion = {
            'cup': 240,
            'tablespoon': 15,
            'teaspoon': 5,
            'ounce': 28.35,
            'pound': 453.59,
            'whole': 50  # for items like eggs
        }

        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0,
            'sugar': 0
        }

        for ingredient in ingredients:
            name = ingredient['name'].lower()
            amount = ingredient['amount']
            unit = ingredient['unit'].lower()

            # Convert amount to grams
            grams = amount * unit_conversion.get(unit, 1)

            # Find matching nutrition data
            nutrition = None
            for key in ingredient_nutrition:
                if key in name:
                    nutrition = ingredient_nutrition[key]
                    break
            if not nutrition:
                nutrition = ingredient_nutrition['default']

            # Add to totals
            for key in total_nutrition:
                total_nutrition[key] += (nutrition[key] * grams / 100)

        return total_nutrition

    def _generate_pro_tips(self, recipe: Dict[str, Any]) -> str:
        """Generate pro tips based on recipe characteristics"""
        tips = []
        
        # Tips based on ingredients
        ingredients = [ing['name'].lower() for ing in recipe.get('ingredients', [])]
        
        if any('egg' in ing for ing in ingredients):
            tips.append("For best results, use room temperature eggs")
        if any('butter' in ing for ing in ingredients):
            tips.append("Use room temperature butter for better creaming")
        if any('yeast' in ing for ing in ingredients):
            tips.append("Make sure your yeast is fresh and active")
        if any('chocolate' in ing for ing in ingredients):
            tips.append("Use high-quality chocolate for best flavor")
        if any('fruit' in ing for ing in ingredients):
            tips.append("Use ripe, fresh fruit for optimal flavor")
        
        # Tips based on cooking method
        if recipe.get('cook_time', 0) > 30:
            tips.append("Check for doneness 5 minutes before the timer goes off")
        if recipe.get('difficulty', '').lower() == 'hard':
            tips.append("Read through the entire recipe before starting")
        if recipe.get('prep_time', 0) > 30:
            tips.append("Mise en place - prepare all ingredients before starting")
        
        # General baking tips
        tips.extend([
            "Preheat your oven for at least 15 minutes before baking",
            "Use an oven thermometer to ensure accurate temperature",
            "Rotate pans halfway through baking for even cooking",
            "Let baked goods cool completely before storing"
        ])
        
        return '. '.join(tips)

    def _generate_storage_instructions(self, recipe: Dict[str, Any]) -> str:
        """Generate storage instructions based on recipe type"""
        storage = []
        
        # Determine recipe type
        meal_type = recipe.get('meal_type', '').lower()
        ingredients = [ing['name'].lower() for ing in recipe.get('ingredients', [])]
        
        # General storage instructions
        storage.append("Store in an airtight container")
        
        # Specific storage based on recipe type
        if 'dessert' in meal_type or any('cream' in ing for ing in ingredients):
            storage.append("Refrigerate if containing dairy or cream")
        elif 'bread' in meal_type:
            storage.append("Store at room temperature for up to 3 days")
            storage.append("Freeze for longer storage")
        elif any('fruit' in ing for ing in ingredients):
            storage.append("Best consumed within 2-3 days")
        
        # Temperature-specific storage
        if any('chocolate' in ing for ing in ingredients):
            storage.append("Store in a cool, dry place away from direct sunlight")
        
        return '. '.join(storage)

    def process_epicurious_dataset(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Process Epicurious dataset into standardized format"""
        processed_recipes = []
        
        try:
            for _, row in df.iterrows():
                # Get ingredients if available
                ingredients = row.get('ingredients', [])
                if isinstance(ingredients, str):
                    ingredients = [{'name': ing.strip(), 'amount': 1, 'unit': 'whole'} for ing in ingredients.split(',')]
                
                # Estimate nutritional values if not provided
                estimated_nutrition = self._estimate_nutritional_values(ingredients)
                
                recipe = {
                    'name': self.clean_text(row.get('title', '')),
                    'description': self.clean_text(row.get('description', '')),
                    'instructions': self.clean_text(row.get('instructions', '')),
                    'image_path': '/static/images/default-recipe.svg',
                    'dietary': self.clean_text(row.get('dietary', 'vegetarian')),
                    'difficulty': self._estimate_difficulty(row),
                    'serving_size': self.clean_numeric(row.get('serving_size', 4)),
                    'prep_time': self.clean_numeric(row.get('prep_time', 0)),
                    'cook_time': self.clean_numeric(row.get('cook_time', 0)),
                    'total_time': self.clean_numeric(row.get('total_time', 0)),
                    'calories': self.clean_numeric(row.get('calories', estimated_nutrition['calories'])),
                    'protein': self.clean_numeric(row.get('protein', estimated_nutrition['protein'])),
                    'carbs': self.clean_numeric(row.get('carbs', estimated_nutrition['carbs'])),
                    'fat': self.clean_numeric(row.get('fat', estimated_nutrition['fat'])),
                    'fiber': self.clean_numeric(row.get('fiber', estimated_nutrition['fiber'])),
                    'sugar': self.clean_numeric(row.get('sugar', estimated_nutrition['sugar'])),
                    'cuisine_type': self.clean_text(row.get('cuisine_type', '')),
                    'meal_type': self.clean_text(row.get('meal_type', '')),
                    'author': self.clean_text(row.get('author', '')),
                    'rating': self.clean_numeric(row.get('rating', 0.0)),
                    'review_count': self.clean_numeric(row.get('review_count', 0)),
                    'tips': self._generate_pro_tips(recipe),
                    'storage_instructions': self._generate_storage_instructions(recipe),
                    'ingredients': ingredients
                }
                
                # Validate required fields
                if not recipe['name']:
                    logger.warning(f"Skipping recipe with missing name")
                    continue
                    
                processed_recipes.append(recipe)
                
        except Exception as e:
            logger.error(f"Error processing Epicurious dataset: {e}")
            raise
            
        return processed_recipes
    
    def process_food_com_dataset(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Process Food.com dataset into standardized format"""
        processed_recipes = []
        
        try:
            for _, row in df.iterrows():
                recipe = {
                    'name': self.clean_text(row.get('name', '')),
                    'description': self.clean_text(row.get('description', '')),
                    'instructions': self.clean_text(row.get('steps', '')),
                    'image_path': '/static/images/default-recipe.svg',
                    'dietary': self.clean_text(row.get('dietary', 'vegetarian')),
                    'difficulty': self._estimate_difficulty(row),
                    'serving_size': self.clean_numeric(row.get('serving_size', 4)),
                    'prep_time': self.clean_numeric(row.get('prep_time', 0)),
                    'cook_time': self.clean_numeric(row.get('cook_time', 0)),
                    'total_time': self.clean_numeric(row.get('total_time', 0)),
                    'calories': self.clean_numeric(row.get('calories', 0)),
                    'protein': self.clean_numeric(row.get('protein', 0.0)),
                    'carbs': self.clean_numeric(row.get('carbs', 0.0)),
                    'fat': self.clean_numeric(row.get('fat', 0.0)),
                    'fiber': self.clean_numeric(row.get('fiber', 0.0)),
                    'sugar': self.clean_numeric(row.get('sugar', 0.0)),
                    'cuisine_type': self.clean_text(row.get('cuisine_type', '')),
                    'meal_type': self.clean_text(row.get('meal_type', '')),
                    'author': self.clean_text(row.get('author', '')),
                    'rating': self.clean_numeric(row.get('rating', 0.0)),
                    'review_count': self.clean_numeric(row.get('review_count', 0)),
                    'tips': self._extract_tips(row),
                    'storage_instructions': self.clean_text(row.get('storage_instructions', '')),
                    'equipment_needed': self.clean_text(row.get('equipment_needed', '')),
                    'temperature': self.clean_text(row.get('temperature', '')),
                    'source': 'Food.com'
                }
                
                # Validate required fields
                if not recipe['name']:
                    logger.warning(f"Skipping recipe with missing name")
                    continue
                    
                processed_recipes.append(recipe)
                
        except Exception as e:
            logger.error(f"Error processing Food.com dataset: {e}")
            raise
            
        return processed_recipes
    
    def process_food_recipes_dataset(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Process Food Recipes dataset into standardized format"""
        processed_recipes = []
        
        try:
            for _, row in df.iterrows():
                recipe = {
                    'name': self.clean_text(row.get('name', '')),
                    'description': self.clean_text(row.get('description', '')),
                    'instructions': self.clean_text(row.get('instructions', '')),
                    'image_path': '/static/images/default-recipe.svg',
                    'dietary': self.clean_text(row.get('dietary', 'vegetarian')),
                    'difficulty': self._estimate_difficulty(row),
                    'serving_size': self.clean_numeric(row.get('serving_size', 4)),
                    'prep_time': self.clean_numeric(row.get('prep_time', 0)),
                    'cook_time': self.clean_numeric(row.get('cook_time', 0)),
                    'total_time': self.clean_numeric(row.get('total_time', 0)),
                    'calories': self.clean_numeric(row.get('calories', 0)),
                    'protein': self.clean_numeric(row.get('protein', 0.0)),
                    'carbs': self.clean_numeric(row.get('carbs', 0.0)),
                    'fat': self.clean_numeric(row.get('fat', 0.0)),
                    'fiber': self.clean_numeric(row.get('fiber', 0.0)),
                    'sugar': self.clean_numeric(row.get('sugar', 0.0)),
                    'cuisine_type': self.clean_text(row.get('cuisine_type', '')),
                    'meal_type': self.clean_text(row.get('meal_type', '')),
                    'author': self.clean_text(row.get('author', '')),
                    'rating': self.clean_numeric(row.get('rating', 0.0)),
                    'review_count': self.clean_numeric(row.get('review_count', 0)),
                    'tips': self._extract_tips(row),
                    'storage_instructions': self.clean_text(row.get('storage_instructions', '')),
                    'equipment_needed': self.clean_text(row.get('equipment_needed', '')),
                    'temperature': self.clean_text(row.get('temperature', '')),
                    'source': 'Food Recipes Dataset'
                }
                
                # Validate required fields
                if not recipe['name']:
                    logger.warning(f"Skipping recipe with missing name")
                    continue
                    
                processed_recipes.append(recipe)
                
        except Exception as e:
            logger.error(f"Error processing Food Recipes dataset: {e}")
            raise
            
        return processed_recipes
    
    def _estimate_difficulty(self, row: pd.Series) -> str:
        """Estimate recipe difficulty based on various factors"""
        try:
            # Count number of ingredients
            ingredients_count = len(str(row.get('ingredients', '')).split(','))
            
            # Count number of steps
            steps_count = len(str(row.get('instructions', '')).split('\n'))
            
            # Calculate total time
            total_time = self.clean_numeric(row.get('total_time', 0))
            
            # Determine difficulty based on these factors
            if ingredients_count > 15 or steps_count > 10 or total_time > 120:
                return 'hard'
            elif ingredients_count > 8 or steps_count > 5 or total_time > 60:
                return 'medium'
            else:
                return 'easy'
                
        except Exception as e:
            logger.warning(f"Error estimating difficulty: {e}")
            return 'medium'
    
    def _extract_tips(self, row: pd.Series) -> str:
        """Extract tips from recipe data"""
        tips = []
        
        try:
            # Add tips based on recipe characteristics
            if row.get('temperature'):
                tips.append(f"Preheat oven to {row['temperature']}")
            
            if self.clean_numeric(row.get('prep_time', 0)) > 30:
                tips.append("Plan ahead - this recipe requires significant prep time")
            
            dietary = self.clean_text(row.get('dietary', ''))
            if dietary == 'vegetarian':
                tips.append("This recipe is vegetarian-friendly")
            elif dietary == 'vegan':
                tips.append("This recipe is vegan-friendly")
            
            storage = self.clean_text(row.get('storage_instructions', ''))
            if storage:
                tips.append(storage)
            
            return '. '.join(tips)
            
        except Exception as e:
            logger.warning(f"Error extracting tips: {e}")
            return ''

def main():
    """Main function to download and process datasets"""
    try:
        processor = DatasetProcessor()
        
        # Download datasets
        datasets = {
            'food_com': 'shuyangli94/food-com-recipes-and-user-interactions'
        }
        
        for name, dataset in datasets.items():
            try:
                processor.download_dataset(name, dataset)
                
                # Process the downloaded dataset
                dataset_path = processor.datasets_dir / name / "RAW_recipes.csv"
                if dataset_path.exists():
                    df = pd.read_csv(dataset_path)
                    
                    # Process the Food.com recipes dataset
                    processed_recipes = []
                    for _, row in df.iterrows():
                        # Convert time values to numeric first
                        prep_time = processor.clean_numeric(row.get('minutes', 0))
                        total_time = prep_time  # Only total time is available
                        cook_time = 0  # Not available separately
                        
                        recipe = {
                            'name': processor.clean_text(row.get('name', '')),
                            'description': processor.clean_text(row.get('description', '')),
                            'instructions': processor.clean_text(row.get('steps', '')),
                            'image_path': '/static/images/default-recipe.svg',
                            'dietary': processor.clean_text(row.get('tags', '')),  # Use tags for dietary info
                            'difficulty': processor._estimate_difficulty(row),
                            'serving_size': processor.clean_numeric(row.get('n_steps', 4)),
                            'prep_time': 0,  # Not available separately
                            'cook_time': 0,  # Not available separately
                            'total_time': total_time,
                            'calories': processor.clean_numeric(row.get('nutrition', [0])[0] if isinstance(row.get('nutrition'), list) else 0),
                            'protein': processor.clean_numeric(row.get('nutrition', [0, 0, 0, 0, 0, 0, 0])[3] if isinstance(row.get('nutrition'), list) else 0),
                            'carbs': processor.clean_numeric(row.get('nutrition', [0, 0, 0, 0, 0, 0, 0])[2] if isinstance(row.get('nutrition'), list) else 0),
                            'fat': processor.clean_numeric(row.get('nutrition', [0, 0, 0, 0, 0, 0, 0])[1] if isinstance(row.get('nutrition'), list) else 0),
                            'fiber': processor.clean_numeric(row.get('nutrition', [0, 0, 0, 0, 0, 0, 0])[5] if isinstance(row.get('nutrition'), list) else 0),
                            'sugar': processor.clean_numeric(row.get('nutrition', [0, 0, 0, 0, 0, 0, 0])[4] if isinstance(row.get('nutrition'), list) else 0),
                            'cuisine_type': processor.clean_text(row.get('tags', '').split(',')[0] if row.get('tags') else ''),
                            'meal_type': '',  # Not directly available
                            'author': processor.clean_text(row.get('contributor_id', '')),
                            'rating': processor.clean_numeric(row.get('rating', 0.0)),
                            'review_count': processor.clean_numeric(row.get('n_steps', 0)),
                            'tips': processor._extract_tips(row),
                            'storage_instructions': '',  # Not available in dataset
                            'equipment_needed': '',  # Not available in dataset
                            'temperature': '',  # Not available in dataset
                            'source': 'Food.com'
                        }
                        
                        # Validate required fields
                        if not recipe['name']:
                            logger.warning(f"Skipping recipe with missing name")
                            continue
                            
                        processed_recipes.append(recipe)
                    
                    # Save processed recipes
                    processed_path = processor.datasets_dir / name / "processed_recipes.csv"
                    pd.DataFrame(processed_recipes).to_csv(processed_path, index=False)
                    logger.info(f"Saved processed recipes to {processed_path}")
                else:
                    logger.error(f"Dataset file not found: {dataset_path}")
                    
            except Exception as e:
                logger.error(f"Error processing dataset {name}: {e}")
                continue
        
        logger.info("Dataset processing completed")
        
    except Exception as e:
        logger.error(f"Error in main processing: {e}")
        raise

if __name__ == "__main__":
    main() 