"""
Functions to enhance recipe data with additional details like pro tips, storage instructions, etc.
"""

def get_pro_tips(recipe_name: str, meal_type: str, cuisine_type: str) -> str:
    """Get pro tips for a recipe based on its type."""
    tips = {
        "Dessert": """
• Use room temperature ingredients for better mixing
• Don't overmix the batter
• Let cool completely before serving
• Use quality ingredients for best results
• Follow temperature instructions precisely""",
        
        "Bread": """
• Use warm water (110°F) to activate yeast properly
• Knead until the dough is smooth and elastic
• Let dough rise in a warm, draft-free place
• Score the top before baking to control expansion
• Tap the bottom - it should sound hollow when done""",
        
        "Breakfast": """
• Prepare ingredients the night before when possible
• Use fresh ingredients for best flavor
• Don't overcrowd the pan
• Keep finished items warm in a low oven
• Serve immediately for best results""",
        
        "Snack": """
• Store in airtight containers
• Make ahead for convenience
• Use fresh ingredients
• Follow temperature guidelines
• Let cool completely before storing"""
    }
    return tips.get(meal_type, """
• Use fresh, quality ingredients
• Follow temperature instructions precisely
• Don't rush the process
• Clean as you go
• Taste and adjust seasonings as needed""")

def get_storage_instructions(recipe_name: str, meal_type: str, cuisine_type: str) -> str:
    """Get storage instructions for a recipe based on its type."""
    storage = {
        "Dessert": """
• Store in an airtight container at room temperature for up to 1 week
• For longer storage, freeze for up to 3 months
• Thaw at room temperature before serving
• Keep away from direct sunlight""",
        
        "Bread": """
• Store at room temperature in a paper bag for 2-3 days
• For longer storage, wrap tightly and freeze for up to 3 months
• Slice before freezing for easier portioning
• Thaw at room temperature or toast directly from frozen""",
        
        "Breakfast": """
• Best served fresh
• Store in refrigerator for up to 3 days
• Reheat in oven or toaster for best results
• Freeze for up to 1 month""",
        
        "Snack": """
• Store in an airtight container at room temperature
• Keep in a cool, dry place
• Consume within 1 week
• Freeze for longer storage"""
    }
    return storage.get(meal_type, """
• Store in an airtight container
• Keep in a cool, dry place
• Consume within recommended time
• Freeze for longer storage""")

def get_equipment_needed(recipe_name: str, meal_type: str, cuisine_type: str) -> str:
    """Get required equipment for a recipe based on its type."""
    equipment = {
        "Dessert": """
• Mixing bowls
• Electric mixer or stand mixer
• Measuring cups and spoons
• Baking pans
• Wire cooling rack
• Parchment paper""",
        
        "Bread": """
• Large mixing bowl
• Measuring cups and spoons
• Bread pan or Dutch oven
• Kitchen scale (optional)
• Clean kitchen towel
• Wire cooling rack""",
        
        "Breakfast": """
• Mixing bowls
• Measuring cups and spoons
• Skillet or griddle
• Spatula
• Whisk
• Timer""",
        
        "Snack": """
• Mixing bowls
• Measuring cups and spoons
• Baking sheet
• Parchment paper
• Cooling rack
• Storage containers"""
    }
    return equipment.get(meal_type, """
• Mixing bowls
• Measuring cups and spoons
• Basic kitchen utensils
• Appropriate cookware
• Timer
• Storage containers""")

def get_temperature(recipe_name: str, meal_type: str, cuisine_type: str) -> str:
    """Get cooking temperature for a recipe based on its type."""
    temps = {
        "Dessert": "350°F (175°C)",
        "Bread": "375°F (190°C)",
        "Breakfast": "350°F (175°C)",
        "Snack": "350°F (175°C)"
    }
    return temps.get(meal_type, "Follow recipe instructions for temperature")

def enhance_recipe(recipe: dict) -> dict:
    """Enhance a recipe with additional details based on its type."""
    recipe['pro_tips'] = get_pro_tips(recipe['name'], recipe.get('meal_type', ''), recipe.get('cuisine_type', ''))
    recipe['storage_instructions'] = get_storage_instructions(recipe['name'], recipe.get('meal_type', ''), recipe.get('cuisine_type', ''))
    recipe['equipment_needed'] = get_equipment_needed(recipe['name'], recipe.get('meal_type', ''), recipe.get('cuisine_type', ''))
    recipe['temperature'] = get_temperature(recipe['name'], recipe.get('meal_type', ''), recipe.get('cuisine_type', ''))
    return recipe 