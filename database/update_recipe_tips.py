import sqlite3
from dataset_processor import DatasetProcessor

def get_required_equipment(recipe_type: str, difficulty: str) -> list:
    """Determine required equipment based on recipe type and difficulty"""
    equipment = ["Measuring cups and spoons", "Mixing bowls"]  # Basic equipment for all recipes
    
    # Common equipment by recipe type
    if recipe_type and recipe_type.lower() == 'bread':
        equipment.extend([
            "Large mixing bowl",
            "Dough hook or wooden spoon",
            "Loaf pan",
            "Pastry brush",
            "Clean kitchen towel",
            "Cooling rack",
            "Bench scraper",
            "Proofing basket or banneton",
            "Scoring lame or sharp knife",
            "Spray bottle for water",
            "Dutch oven (for crusty breads)",
            "Dough scraper"
        ])
    elif recipe_type and recipe_type.lower() == 'cake':
        equipment.extend([
            "Round or square cake pans",
            "Stand mixer or hand mixer",
            "Rubber spatula",
            "Offset spatula",
            "Wire whisk",
            "Cake tester or toothpick",
            "Cooling rack",
            "Cake leveler or serrated knife",
            "Turntable for decorating",
            "Piping bags and tips",
            "Cake board or plate",
            "Cake strips (for even baking)",
            "Cake smoother",
            "Bench scraper for sides"
        ])
    elif recipe_type and recipe_type.lower() == 'cookies':
        equipment.extend([
            "Heavy-duty baking sheets",
            "Silicone baking mats or parchment paper",
            "Stand mixer or hand mixer",
            "Cookie scoop (various sizes)",
            "Spatula",
            "Cooling rack",
            "Cookie cutters (if needed)",
            "Rolling pin (for cut-outs)",
            "Piping bags and tips (for decoration)",
            "Cookie stamps or presses",
            "Offset spatula",
            "Airtight storage containers"
        ])
    elif recipe_type and recipe_type.lower() == 'pie':
        equipment.extend([
            "9-inch pie dish",
            "Rolling pin",
            "Pastry cutter or food processor",
            "Pastry brush",
            "Sharp knife",
            "Cooling rack",
            "Pie weights or dried beans",
            "Pie shield or aluminum foil",
            "Pastry wheel",
            "Bench scraper",
            "Pie server",
            "Glass measuring cup for liquids"
        ])
    elif recipe_type and recipe_type.lower() == 'pastry':
        equipment.extend([
            "Heavy-duty baking sheets",
            "Silicone baking mats or parchment paper",
            "Rolling pin",
            "Pastry brush",
            "Sharp knife",
            "Cooling rack",
            "Pastry cutter or wheel",
            "Bench scraper",
            "Ruler (for even cuts)",
            "Piping bags and tips",
            "Pastry brush",
            "Spray bottle for water",
            "Dough docker",
            "Pastry rings or cutters"
        ])
    elif recipe_type and recipe_type.lower() == 'muffins':
        equipment.extend([
            "Muffin tin",
            "Paper liners",
            "Ice cream scoop or large spoon",
            "Wire whisk",
            "Rubber spatula",
            "Cooling rack",
            "Pastry brush",
            "Sifter or fine-mesh strainer"
        ])
    elif recipe_type and recipe_type.lower() == 'cheesecake':
        equipment.extend([
            "Springform pan",
            "Large roasting pan (for water bath)",
            "Heavy-duty aluminum foil",
            "Stand mixer or hand mixer",
            "Rubber spatula",
            "Measuring cups and spoons",
            "Food processor (for crust)",
            "Cooling rack",
            "Offset spatula",
            "Sharp knife for clean cuts"
        ])
    elif recipe_type and recipe_type.lower() == 'tart':
        equipment.extend([
            "Tart pan with removable bottom",
            "Rolling pin",
            "Pastry brush",
            "Pie weights or dried beans",
            "Sharp knife",
            "Cooling rack",
            "Pastry cutter",
            "Bench scraper",
            "Offset spatula"
        ])
    
    # Additional equipment for difficult recipes
    if difficulty and difficulty.lower() == 'hard':
        equipment.extend([
            "Stand mixer with multiple attachments",
            "Food processor",
            "Digital kitchen scale",
            "Digital probe thermometer",
            "Candy thermometer",
            "Silicone mats",
            "Specialty molds",
            "Acetate strips",
            "Cake ring",
            "Microplane grater",
            "Fine-mesh strainers (various sizes)",
            "Immersion blender",
            "Kitchen torch"
        ])
    
    # Additional equipment for specific techniques
    if 'chocolate' in str(recipe_type).lower():
        equipment.extend([
            "Double boiler or heatproof bowl",
            "Chocolate thermometer",
            "Dipping forks",
            "Transfer sheets",
            "Chocolate molds",
            "Offset spatula",
            "Bench scraper"
        ])
    
    if 'decoration' in str(recipe_type).lower() or difficulty == 'hard':
        equipment.extend([
            "Turntable",
            "Various piping tips",
            "Piping bags",
            "Offset spatulas (various sizes)",
            "Cake combs",
            "Fondant tools",
            "Stencils",
            "Food coloring kit",
            "Edible paint brushes"
        ])
    
    return list(set(equipment))  # Remove duplicates

def update_recipe_tips():
    """Update all recipes with pro tips, storage instructions, and required equipment"""
    processor = DatasetProcessor()
    
    try:
        # Connect to the database
        conn = sqlite3.connect('database/recipes.db')
        cursor = conn.cursor()
        
        # Get all recipes
        cursor.execute("""
            SELECT id, name, difficulty, prep_time, cook_time, meal_type
            FROM recipes
        """)
        recipes = cursor.fetchall()
        
        # Update each recipe
        for recipe in recipes:
            recipe_id, name, difficulty, prep_time, cook_time, meal_type = recipe
            
            # Create recipe dictionary
            recipe_dict = {
                'ingredients': [],  # We'll generate general tips without ingredients
                'difficulty': difficulty,
                'prep_time': prep_time,
                'cook_time': cook_time,
                'meal_type': meal_type
            }
            
            # Generate tips and storage instructions
            tips = [
                "Read through the entire recipe before starting",
                "Preheat your oven for at least 15 minutes before baking",
                "Use an oven thermometer to ensure accurate temperature",
                "Rotate pans halfway through baking for even cooking",
                "Let baked goods cool completely before storing"
            ]
            
            if prep_time and int(prep_time) > 30:
                tips.append("Mise en place - prepare all ingredients before starting")
            
            if cook_time and int(cook_time) > 30:
                tips.append("Check for doneness 5 minutes before the timer goes off")
            
            if difficulty and difficulty.lower() == 'hard':
                tips.append("Take your time and follow each step carefully")
            
            # Storage instructions based on meal type
            storage = ["Store in an airtight container"]
            
            if meal_type:
                meal_type = meal_type.lower()
                if 'dessert' in meal_type:
                    storage.append("Refrigerate if containing dairy or cream")
                elif 'bread' in meal_type:
                    storage.append("Store at room temperature for up to 3 days")
                    storage.append("Freeze for longer storage")
            
            # Get required equipment
            equipment = get_required_equipment(meal_type, difficulty)
            
            # Update the recipe
            cursor.execute("""
                UPDATE recipes 
                SET tips = ?, storage_instructions = ?, equipment_needed = ?
                WHERE id = ?
            """, ('. '.join(tips), '. '.join(storage), ', '.join(equipment), recipe_id))
            
            print(f"Updated tips, storage, and equipment for: {name}")
        
        # Commit changes
        conn.commit()
        print(f"Successfully updated {len(recipes)} recipes")
        
    except Exception as e:
        print(f"Error updating recipes: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_recipe_tips() 