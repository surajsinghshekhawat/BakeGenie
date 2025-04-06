"""
Database for ingredients and their properties with comprehensive density information
"""

import sqlite3
import json
import os

# Create database directory if it doesn't exist
os.makedirs('database', exist_ok=True)

def init_ingredients_db():
    """Initialize the ingredients database with comprehensive density information"""
    conn = sqlite3.connect('database/ingredients.db')
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS ingredients')
    cursor.execute('DROP TABLE IF EXISTS measurements')
    cursor.execute('DROP TABLE IF EXISTS ingredient_states')
    cursor.execute('DROP TABLE IF EXISTS temperature_effects')
    cursor.execute('DROP TABLE IF EXISTS substitutions')
    
    # Create ingredients table with enhanced fields
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        base_density REAL,
        unit TEXT,
        category TEXT,
        description TEXT,
        image_path TEXT,
        notes TEXT
    )
    ''')
    
    # Create ingredient states table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ingredient_states (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingredient_id INTEGER,
        state TEXT,
        density_multiplier REAL,
        description TEXT,
        FOREIGN KEY (ingredient_id) REFERENCES ingredients (id)
    )
    ''')
    
    # Create temperature effects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS temperature_effects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingredient_id INTEGER,
        temperature_celsius REAL,
        density_multiplier REAL,
        notes TEXT,
        FOREIGN KEY (ingredient_id) REFERENCES ingredients (id)
    )
    ''')
    
    # Create substitutions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS substitutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_ingredient_id INTEGER,
        substitute_ingredient_id INTEGER,
        ratio REAL,
        notes TEXT,
        FOREIGN KEY (original_ingredient_id) REFERENCES ingredients (id),
        FOREIGN KEY (substitute_ingredient_id) REFERENCES ingredients (id)
    )
    ''')
    
    # Create measurements table (enhanced)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        volume_ml REAL,
        description TEXT
    )
    ''')
    
    # Comprehensive ingredients data with accurate densities
    ingredients_data = [
        # Flours & Starches
        ("all-purpose flour", 0.59, "g/ml", "Flours & Starches", "Standard wheat flour for general baking", "/static/images/ingredients/defualt_ingr.jpeg", "Density varies with sifting and packing"),
        ("bread flour", 0.58, "g/ml", "dry", "High-protein flour for bread baking", "/static/images/ingredients/defualt_ingr.jpeg", "Higher density than AP flour"),
        ("cake flour", 0.50, "g/ml", "dry", "Fine-textured low-protein flour", "/static/images/ingredients/defualt_ingr.jpeg", "Lightest flour variety"),
        ("whole wheat flour", 0.64, "g/ml", "Flours & Starches", "Whole grain wheat flour with bran and germ", "/static/images/ingredients/defualt_ingr.jpeg", "Higher density than all-purpose flour"),
        ("pastry flour", 0.53, "g/ml", "dry", "Medium-protein flour for pastries", "/static/images/ingredients/defualt_ingr.jpeg", "Between AP and cake flour"),
        ("rye flour", 0.62, "g/ml", "dry", "Flour from rye grain", "/static/images/ingredients/defualt_ingr.jpeg", "Denser than wheat flour"),
        ("cornstarch", 0.45, "g/ml", "dry", "Corn-based thickener", "/static/images/ingredients/defualt_ingr.jpeg", "Lightens when heated"),
        ("potato starch", 0.48, "g/ml", "dry", "Starch from potatoes", "/static/images/ingredients/defualt_ingr.jpeg", "Good for gluten-free baking"),
        ("tapioca starch", 0.46, "g/ml", "dry", "Starch from cassava root", "/static/images/ingredients/defualt_ingr.jpeg", "Creates chewy texture"),
        ("arrowroot", 0.47, "g/ml", "dry", "Starch from arrowroot plant", "/static/images/ingredients/defualt_ingr.jpeg", "Clear thickening power"),
        
        # Sugars & Sweeteners
        ("granulated sugar", 0.85, "g/ml", "dry", "Standard white sugar", "/static/images/ingredients/defualt_ingr.jpeg", "Density varies with humidity"),
        ("brown sugar", 0.93, "g/ml", "dry", "Sugar with molasses", "/static/images/ingredients/defualt_ingr.jpeg", "Pack firmly for accurate measure"),
        ("powdered sugar", 0.56, "g/ml", "dry", "Finely ground sugar", "/static/images/ingredients/defualt_ingr.jpeg", "Sift before measuring"),
        ("honey", 1.42, "g/ml", "liquid", "Natural sweetener", "/static/images/ingredients/defualt_ingr.jpeg", "Temperature sensitive"),
        ("maple syrup", 1.37, "g/ml", "liquid", "Tree sap syrup", "/static/images/ingredients/defualt_ingr.jpeg", "Grade A slightly less dense"),
        ("corn syrup", 1.38, "g/ml", "liquid", "Glucose syrup", "/static/images/ingredients/defualt_ingr.jpeg", "Light version available"),
        ("molasses", 1.45, "g/ml", "liquid", "Byproduct of sugar refining", "/static/images/ingredients/defualt_ingr.jpeg", "Blackstrap is thickest"),
        
        # Fats & Oils
        ("butter", 0.911, "g/ml", "fat", "Dairy fat", "/static/images/ingredients/defualt_ingr.jpeg", "Density varies with temperature"),
        ("vegetable oil", 0.92, "g/ml", "liquid", "Neutral cooking oil", "/static/images/ingredients/defualt_ingr.jpeg", "Consistent density"),
        ("olive oil", 0.92, "g/ml", "liquid", "Fruit oil from olives", "/static/images/ingredients/defualt_ingr.jpeg", "Extra virgin is standard"),
        ("coconut oil", 0.92, "g/ml", "fat", "Oil from coconut meat", "/static/images/ingredients/defualt_ingr.jpeg", "Solid at room temperature"),
        ("shortening", 0.88, "g/ml", "fat", "Vegetable fat", "/static/images/ingredients/defualt_ingr.jpeg", "100% fat, no water"),
        
        # Dairy Products
        ("whole milk", 1.03, "g/ml", "liquid", "Standard dairy milk", "/static/images/ingredients/defualt_ingr.jpeg", "Temperature sensitive"),
        ("heavy cream", 0.994, "g/ml", "liquid", "High-fat dairy cream", "/static/images/ingredients/defualt_ingr.jpeg", "Whips to different density"),
        ("sour cream", 1.05, "g/ml", "liquid", "Cultured cream", "/static/images/ingredients/defualt_ingr.jpeg", "Full fat version"),
        ("buttermilk", 1.03, "g/ml", "liquid", "Cultured milk", "/static/images/ingredients/defualt_ingr.jpeg", "Lower fat than milk"),
        ("yogurt", 1.04, "g/ml", "liquid", "Cultured milk product", "/static/images/ingredients/defualt_ingr.jpeg", "Greek style is thicker"),
        
        # Eggs & Leaveners
        ("eggs", 1.03, "g/ml", "liquid", "Whole eggs", "/static/images/ingredients/defualt_ingr.jpeg", "Average large egg = 50ml"),
        ("egg whites", 1.04, "g/ml", "liquid", "Albumen only", "/static/images/ingredients/defualt_ingr.jpeg", "About 30ml per large egg"),
        ("egg yolks", 1.07, "g/ml", "liquid", "Yolks only", "/static/images/ingredients/defualt_ingr.jpeg", "About 20ml per large egg"),
        ("baking powder", 0.9, "g/ml", "dry", "Double-acting leavener", "/static/images/ingredients/defualt_ingr.jpeg", "Keep dry for accuracy"),
        ("baking soda", 0.85, "g/ml", "dry", "Sodium bicarbonate", "/static/images/ingredients/defualt_ingr.jpeg", "Single-acting leavener"),
        ("yeast", 0.75, "g/ml", "dry", "Active dry yeast", "/static/images/ingredients/defualt_ingr.jpeg", "Instant yeast similar"),
        
        # Salt & Spices
        ("table salt", 2.17, "g/ml", "dry", "Fine ground salt", "/static/images/ingredients/defualt_ingr.jpeg", "Most dense common ingredient"),
        ("kosher salt", 1.2, "g/ml", "dry", "Coarse flaked salt", "/static/images/ingredients/defualt_ingr.jpeg", "Less dense than table salt"),
        ("cinnamon", 0.56, "g/ml", "dry", "Ground cinnamon", "/static/images/ingredients/defualt_ingr.jpeg", "Light and fluffy"),
        ("nutmeg", 0.45, "g/ml", "dry", "Ground nutmeg", "/static/images/ingredients/defualt_ingr.jpeg", "Use freshly grated"),
        ("vanilla extract", 0.89, "g/ml", "liquid", "Alcohol-based extract", "/static/images/ingredients/defualt_ingr.jpeg", "Pure extract preferred"),
        
        # Nuts & Seeds
        ("almonds", 0.45, "g/ml", "dry", "Whole almonds", "/static/images/ingredients/defualt_ingr.jpeg", "Varies by chop size"),
        ("walnuts", 0.42, "g/ml", "dry", "Whole walnuts", "/static/images/ingredients/defualt_ingr.jpeg", "Lighter when chopped"),
        ("pecans", 0.40, "g/ml", "dry", "Whole pecans", "/static/images/ingredients/defualt_ingr.jpeg", "Similar to walnuts"),
        ("hazelnuts", 0.44, "g/ml", "dry", "Whole hazelnuts", "/static/images/ingredients/defualt_ingr.jpeg", "Also called filberts"),
        ("peanuts", 0.46, "g/ml", "dry", "Whole peanuts", "/static/images/ingredients/defualt_ingr.jpeg", "Technically a legume"),
        
        # Chocolate & Cocoa
        ("cocoa powder", 0.53, "g/ml", "dry", "Unsweetened chocolate powder", "/static/images/ingredients/defualt_ingr.jpeg", "Dutch-process similar density"),
        ("chocolate chips", 0.63, "g/ml", "solid", "Semi-sweet chocolate", "/static/images/ingredients/defualt_ingr.jpeg", "Melted = different density"),
        ("white chocolate", 1.11, "g/ml", "solid", "Cocoa butter based", "/static/images/ingredients/defualt_ingr.jpeg", "Melts at lower temperature"),
        ("dark chocolate", 1.10, "g/ml", "solid", "High cocoa content", "/static/images/ingredients/defualt_ingr.jpeg", "70% or higher preferred"),
        ("milk chocolate", 1.12, "g/ml", "solid", "Milk solids added", "/static/images/ingredients/defualt_ingr.jpeg", "Sweetest chocolate type"),
        
        # Additional Ingredients
        ("rolled oats", 0.41, "g/ml", "dry", "Flattened oat groats", "/static/images/ingredients/defualt_ingr.jpeg", "Steel-cut more dense"),
        ("rice", 0.75, "g/ml", "dry", "White rice", "/static/images/ingredients/defualt_ingr.jpeg", "Brown rice slightly denser"),
        ("bread crumbs", 0.35, "g/ml", "dry", "Dried bread pieces", "/static/images/ingredients/defualt_ingr.jpeg", "Fresh crumbs are heavier"),
        ("coconut", 0.45, "g/ml", "dry", "Shredded coconut", "/static/images/ingredients/defualt_ingr.jpeg", "Sweetened version available"),
        ("raisins", 0.65, "g/ml", "dry", "Dried grapes", "/static/images/ingredients/defualt_ingr.jpeg", "Golden raisins similar")
    ]
    
    # Insert ingredients
    for ingredient in ingredients_data:
        cursor.execute('''
        INSERT OR IGNORE INTO ingredients 
        (name, base_density, unit, category, description, image_path, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ingredient)
    
    # Insert ingredient states
    states_data = [
        (1, "sifted", 0.45, "Flour after sifting"),
        (1, "packed", 0.65, "Flour when packed"),
        (7, "melted", 0.92, "Butter in liquid state"),
        (7, "softened", 0.911, "Butter at room temperature"),
        (7, "cold", 0.96, "Butter at refrigerator temperature"),
        (20, "whole", 0.45, "Whole nuts"),
        (20, "chopped", 0.55, "Roughly chopped nuts"),
        (20, "ground", 0.65, "Finely ground nuts")
    ]
    
    for state in states_data:
        cursor.execute('''
        INSERT INTO ingredient_states (ingredient_id, state, density_multiplier, description)
        VALUES (?, ?, ?, ?)
        ''', state)
    
    # Temperature effects
    temperature_data = [
        (7, 4, 0.96, "Refrigerated butter"),
        (7, 20, 0.911, "Room temperature butter"),
        (7, 35, 0.92, "Melted butter"),
        (13, 20, 1.37, "Room temperature maple syrup"),
        (13, 4, 1.42, "Cold maple syrup"),
        (12, 20, 1.42, "Room temperature honey"),
        (12, 35, 1.36, "Warm honey")
    ]
    
    for temp_effect in temperature_data:
        cursor.execute('''
        INSERT INTO temperature_effects (ingredient_id, temperature_celsius, density_multiplier, notes)
        VALUES (?, ?, ?, ?)
        ''', temp_effect)
    
    # Substitutions with density ratios
    substitutions_data = [
        (1, 2, 1.05, "Bread flour for AP flour"),
        (1, 3, 0.91, "Cake flour for AP flour"),
        (7, 8, 1.01, "Oil for melted butter"),
        (4, 5, 1.09, "Brown sugar for white sugar"),
        (9, 10, 0.965, "Heavy cream for whole milk")
    ]
    
    for sub in substitutions_data:
        cursor.execute('''
        INSERT INTO substitutions (original_ingredient_id, substitute_ingredient_id, ratio, notes)
        VALUES (?, ?, ?, ?)
        ''', sub)
    
    # Enhanced measurements data
    measurements_data = [
        ("cup", 236.588, "Standard US cup"),
        ("half_cup", 118.294, "1/2 US cup"),
        ("third_cup", 78.863, "1/3 US cup"),
        ("quarter_cup", 59.147, "1/4 US cup"),
        ("eighth_cup", 29.573, "1/8 US cup"),
        ("tablespoon", 14.787, "US tablespoon"),
        ("teaspoon", 4.929, "US teaspoon"),
        ("half_tablespoon", 7.393, "1/2 US tablespoon"),
        ("half_teaspoon", 2.464, "1/2 US teaspoon"),
        ("quarter_teaspoon", 1.232, "1/4 US teaspoon"),
        ("milliliter", 1.0, "Metric milliliter"),
        ("liter", 1000.0, "Metric liter"),
        ("fluid_ounce", 29.5735, "US fluid ounce")
    ]
    
    for measurement in measurements_data:
        cursor.execute('''
        INSERT OR IGNORE INTO measurements (name, volume_ml, description)
        VALUES (?, ?, ?)
        ''', measurement)
    
    conn.commit()
    conn.close()

def get_ingredient_density(name, state=None, temperature=None):
    """Get ingredient density considering state and temperature"""
    conn = sqlite3.connect('database/ingredients.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    base_density = cursor.execute(
        'SELECT id, base_density FROM ingredients WHERE name = ?', 
        (name,)
    ).fetchone()
    
    if not base_density:
        conn.close()
        return None
        
    density = base_density['base_density']
    ingredient_id = base_density['id']
    
    if state:
        state_mult = cursor.execute(
            '''SELECT density_multiplier FROM ingredient_states 
            WHERE ingredient_id = ? AND state = ?''',
            (ingredient_id, state)
        ).fetchone()
        if state_mult:
            density *= state_mult['density_multiplier']
    
    if temperature is not None:
        temp_effect = cursor.execute(
            '''SELECT density_multiplier FROM temperature_effects 
            WHERE ingredient_id = ? 
            ORDER BY ABS(temperature_celsius - ?) LIMIT 1''',
            (ingredient_id, temperature)
        ).fetchone()
        if temp_effect:
            density *= temp_effect['density_multiplier']
    
    conn.close()
    return density

def get_substitution(original_name, substitute_name):
    """Get substitution ratio between two ingredients"""
    conn = sqlite3.connect('database/ingredients.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    ratio = cursor.execute('''
        SELECT s.ratio, s.notes
        FROM ingredients i1
        JOIN substitutions s ON i1.id = s.original_ingredient_id
        JOIN ingredients i2 ON i2.id = s.substitute_ingredient_id
        WHERE i1.name = ? AND i2.name = ?
    ''', (original_name, substitute_name)).fetchone()
    
    conn.close()
    return dict(ratio) if ratio else None

# Keep existing functions
def get_all_ingredients():
    """Get all ingredients"""
    conn = sqlite3.connect('database/ingredients.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT i.*, GROUP_CONCAT(DISTINCT ist.state) as available_states
        FROM ingredients i
        LEFT JOIN ingredient_states ist ON i.id = ist.ingredient_id
        GROUP BY i.id
        ORDER BY i.name
    ''')
    ingredients = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return ingredients

def get_ingredient_by_name(name):
    """Get detailed ingredient information by name"""
    conn = sqlite3.connect('database/ingredients.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            i.*,
            GROUP_CONCAT(DISTINCT ist.state) as available_states,
            GROUP_CONCAT(DISTINCT te.temperature_celsius) as temp_points
        FROM ingredients i
        LEFT JOIN ingredient_states ist ON i.id = ist.ingredient_id
        LEFT JOIN temperature_effects te ON i.id = te.ingredient_id
        WHERE i.name = ?
        GROUP BY i.id
    ''', (name,))
    ingredient = cursor.fetchone()
    
    conn.close()
    return dict(ingredient) if ingredient else None

# Keep existing measurement functions
def get_all_measurements():
    """Get all measurements"""
    conn = sqlite3.connect('database/ingredients.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM measurements ORDER BY volume_ml DESC')
    measurements = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return measurements

def get_measurement_by_name(name):
    """Get measurement details by name"""
    conn = sqlite3.connect('database/ingredients.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM measurements WHERE name = ?', (name,))
    measurement = cursor.fetchone()
    
    conn.close()
    return dict(measurement) if measurement else None

# Initialize the database when this module is imported
init_ingredients_db()

