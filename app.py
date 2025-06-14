from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, send_from_directory
import os
import cv2
import numpy as np
import json
import base64
from PIL import Image
import io
import google.generativeai as genai
from datetime import datetime
import sqlite3
import logging
from functools import lru_cache
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import torch
import torchvision
from dotenv import load_dotenv
from utils.calibration import calibrator
from utils.measurement_detector import MeasurementDetector
from utils.rcnn_measurement_system import RCNNMeasurementSystem
import requests
import gdown

# Import our database modules
from database.ingredients_db import get_all_ingredients, get_ingredient_by_name, get_all_measurements, get_measurement_by_name, init_ingredients_db
from database.recipes_db import get_all_recipes, get_recipe_by_id, search_recipes, find_recipes_by_ingredients, init_recipes_db
from init_databases import init_all_databases

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/images/ingredients', exist_ok=True)
os.makedirs('static/images/recipes', exist_ok=True)

# Initialize Gemini Pro Vision
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

# Configure Gemini API with the API key
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize models
model = genai.GenerativeModel('models/gemini-1.5-pro')
chat_model = genai.GenerativeModel('models/gemini-1.5-pro')

# Initialize RCNN measurement system
try:
    checkpoint_path = os.path.join('models', 'checkpoint.pth')
    if not os.path.exists(checkpoint_path):
        logger.warning(f"No checkpoint found at {checkpoint_path}. Using default model.")
        rcnn_measurement = RCNNMeasurementSystem()
    else:
        logger.info(f"Loading checkpoint from {checkpoint_path}")
        rcnn_measurement = RCNNMeasurementSystem(checkpoint_path)
except Exception as e:
    logger.error(f"Error initializing RCNN: {e}")
    logger.info("Initializing RCNN with default model")
    rcnn_measurement = RCNNMeasurementSystem()

# Initialize YOLOv8 model
yolo_model = YOLO('yolov8n.pt')

# Initialize measurement detector
measurement_detector = MeasurementDetector()

# Cache for frequently accessed data
@lru_cache(maxsize=100)
def get_cached_ingredients():
    return [ingredient['name'] for ingredient in get_all_ingredients()]

# Model download configuration
MODEL_PATH = 'models/checkpoint.pth'
MODEL_URL = 'https://drive.google.com/uc?id=1VaB9qmln89nWr74fhceatvvaTqUQMgqU'

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Model not found. Downloading...")
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        
        try:
            # Download using gdown
            gdown.download(MODEL_URL, MODEL_PATH, quiet=False)
            print("Model downloaded successfully!")
        except Exception as e:
            print(f"Error downloading model: {e}")
            raise

# Download model if not present
download_model()

@app.route('/')
def index():
    """Render the main page"""
    try:
        recipes = get_all_recipes()
        return render_template('index.html', recipes=recipes)
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return render_template('error.html', error="Failed to load recipes")

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check if model exists
        model_exists = os.path.exists('models/checkpoint.pth')
        return jsonify({
            'status': 'healthy',
            'model_loaded': model_exists,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/measure')
def measure():
    ingredients = get_cached_ingredients()
    measurements = get_all_measurements()
    return render_template('measure.html', ingredients=ingredients, measurements=measurements)

@app.route('/adjust')
def adjust():
    recipe_id = request.args.get('recipe_id')
    recipes = get_all_recipes()
    
    if recipe_id:
        selected_recipe = get_recipe_by_id(int(recipe_id))
        return render_template('adjust.html', recipes=recipes, selected_recipe=selected_recipe)
    
    return render_template('adjust.html', recipes=recipes)

@app.route('/ingredients')
def ingredients():
    ingredients = get_cached_ingredients()
    return render_template('ingredients.html', ingredients=ingredients)

@app.route('/recipes')
def recipes():
    query = request.args.get('query', '')
    dietary = request.args.get('dietary', '')
    difficulty = request.args.get('difficulty', '')
    
    if query or dietary or difficulty:
        recipes_list = search_recipes(query, dietary, difficulty)
    else:
        recipes_list = get_all_recipes()
    
    return render_template('recipes.html', recipes=recipes_list)

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    """Render the recipe detail page"""
    try:
        recipe = get_recipe_by_id(recipe_id)
        if not recipe:
            logger.error(f"Recipe {recipe_id} not found")
            return render_template('error.html', error="Recipe not found")
            
        # Ensure recipe has all required fields
        if 'ingredients' not in recipe:
            recipe['ingredients'] = []
        if 'image_path' not in recipe:
            recipe['image_path'] = '/static/images/default-recipe.jpg'
            
        # Format instructions
        if 'instructions' in recipe and recipe['instructions']:
            # Split instructions into steps and remove empty lines
            steps = [step.strip() for step in recipe['instructions'].split('\n') if step.strip()]
            recipe['instructions'] = steps
        else:
            recipe['instructions'] = []
            
        return render_template('recipe_detail.html', recipe=recipe)
    except Exception as e:
        logger.error(f"Error rendering recipe {recipe_id}: {e}")
        return render_template('error.html', error="Failed to load recipe")

@app.route('/api/get_ingredient_details', methods=['GET'])
def get_ingredient_details_api():
    ingredient_name = request.args.get('ingredient')
    ingredient = get_ingredient_by_name(ingredient_name)
    
    if ingredient:
        # Format the ingredient data
        formatted_ingredient = {
            'name': ingredient['name'],
            'base_density': ingredient['base_density'],
            'unit': ingredient['unit'],
            'category': ingredient['category'],
            'description': ingredient['description'],
            'image_path': ingredient['image_path'],
            'notes': ingredient['notes'],
            'available_states': ingredient['available_states'].split(',') if ingredient['available_states'] else [],
            'temp_points': ingredient['temp_points'].split(',') if ingredient['temp_points'] else []
        }
        return jsonify(formatted_ingredient)
    return jsonify({"error": "Ingredient not found"}), 404

@app.route('/api/upload_photo', methods=['POST'])
def upload_photo():
    try:
        if 'photo' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No photo uploaded'
            })
            
        photo = request.files['photo']
        if photo.filename == '':
            return jsonify({
                'success': False,
                'message': 'No selected file'
            })
            
        # Get measurement parameters
        container_type = request.form.get('container_type')
        ingredient_type = request.form.get('ingredient_type')
        
        if not container_type or not ingredient_type:
            return jsonify({
                'success': False,
                'message': 'Missing container or ingredient type'
            })
            
        # Save the uploaded file
        filename = secure_filename(photo.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(filepath)
        
        # Process the measurement using RCNN
        result = rcnn_measurement.process_measurement(filepath, container_type, ingredient_type)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'message': result.get('message', 'Failed to process measurement')
            })
        
        # Get ingredient density for weight calculation
        ingredient_data = get_ingredient_by_name(ingredient_type)
        if ingredient_data and 'base_density' in ingredient_data:
            density = float(ingredient_data['base_density'])
            volume_ml = float(result['volume'].replace('ml', ''))
            weight = volume_ml * density
            result['weight_g'] = f"{weight:.1f}g"
        
        # Add debug image path
        result['debug_image'] = f'/static/uploads/{filename}'
        result['success'] = True
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing photo upload: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/process_image', methods=['POST'])
def process_image():
    try:
        # Get data from request
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({
                "success": False,
                "message": "No image data provided"
            })
            
        # Extract base64 image data
        try:
            img_data = data.get('image').split(',')[1]
        except (IndexError, AttributeError):
            return jsonify({
                "success": False,
                "message": "Invalid image data format"
            })
            
        container_type = data.get('container_type', 'teaspoon')
        ingredient_type = data.get('ingredient_type', 'flour')
        
        # Convert base64 to image
        try:
            img_bytes = base64.b64decode(img_data)
            img = Image.open(io.BytesIO(img_bytes))
            img = np.array(img)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"Error decoding image: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Invalid image data"
            })
        
        # Save temporary image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"temp_{timestamp}.jpg"
        temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        cv2.imwrite(temp_filepath, img)
        
        # Process measurement using RCNN
        result = rcnn_measurement.process_measurement(temp_filepath, container_type, ingredient_type)
        
        if result['success']:
            # Get ingredient density for weight calculation
            ingredient_data = get_ingredient_by_name(ingredient_type)
            if ingredient_data and 'base_density' in ingredient_data:
                density = float(ingredient_data['base_density'])
                volume_ml = float(result['volume'].replace('ml', ''))
                weight = volume_ml * density
                result['weight_g'] = f"{weight:.1f}g"
            
            # Add debug image path
            result['debug_image'] = f'/static/uploads/{temp_filename}'
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        })

@app.route('/api/chat_recipe_suggestions', methods=['POST'])
def chat_recipe_suggestions():
    try:
        data = request.get_json()
        ingredients = data.get("ingredients", [])
        servings = data.get("servings", 4)

        if not ingredients:
            return jsonify({"success": False, "message": "No ingredients provided"})

        # Log the search
        logging.info(f"Searching for recipes with ingredients: {ingredients}")

        # Prepare prompt for Gemini
        prompt = f"""Generate exactly 4 recipes based on these ingredients: {', '.join(ingredients)}
        For {servings} servings.
        Return ONLY a JSON object with this exact structure:
        {{
            "recipes": [
                {{
                    "name": "Recipe name",
                    "cooking_time": "30-45 minutes",
                    "difficulty": "Easy/Medium/Hard",
                    "ingredients": [
                        {{
                            "name": "ingredient name",
                            "amount": "amount with unit",
                            "is_provided": true/false
                        }},
                        ...
                    ],
                    "instructions": ["step 1", "step 2", ...],
                    "missing_ingredients": [
                        {{
                            "name": "missing ingredient name",
                            "amount": "amount with unit"
                        }},
                        ...
                    ]
                }},
                ...
            ]
        }}
        Important rules:
        1. Generate EXACTLY 4 recipes
        2. For each ingredient in the recipe, set is_provided=true if it's in the provided ingredients list
        3. List all missing ingredients with their required amounts
        4. Do not include any text before or after the JSON object"""

        # Generate response using Gemini
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Log the raw response for debugging
        logging.info(f"Raw Gemini response: {response_text}")
        
        # Try to parse the response as JSON
        try:
            # Clean the response text to ensure it's valid JSON
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(response_text)
            
            # Ensure we have the expected structure
            if not isinstance(data, dict) or "recipes" not in data:
                raise ValueError("Invalid response structure")
            
            # Process each recipe to ensure missing ingredients are properly formatted
            for recipe in data["recipes"]:
                # Ensure ingredients list exists
                if "ingredients" not in recipe:
                    recipe["ingredients"] = []
                
                # Ensure missing_ingredients list exists
                if "missing_ingredients" not in recipe:
                    recipe["missing_ingredients"] = []
                
                # Process ingredients to identify missing ones
                missing_ingredients = []
                seen_missing = set()  # Track unique missing ingredients
                
                for ingredient in recipe["ingredients"]:
                    if not ingredient.get("is_provided", False):
                        missing_key = f"{ingredient['name']}_{ingredient['amount']}"
                        if missing_key not in seen_missing:
                            missing_ingredients.append({
                                "name": ingredient["name"],
                                "amount": ingredient["amount"]
                            })
                            seen_missing.add(missing_key)
                
                # Update missing_ingredients if not already set
                if missing_ingredients and not recipe["missing_ingredients"]:
                    recipe["missing_ingredients"] = missing_ingredients
                
                # Format ingredients for display
                formatted_ingredients = []
                for ing in recipe["ingredients"]:
                    formatted_ingredients.append(f"{ing['amount']} {ing['name']}")
                recipe["formatted_ingredients"] = formatted_ingredients
            
            # Ensure we have exactly 4 recipes
            if len(data["recipes"]) < 4:
                logging.warning(f"Received only {len(data['recipes'])} recipes, expected 4")
            elif len(data["recipes"]) > 4:
                data["recipes"] = data["recipes"][:4]
            
            return jsonify({"success": True, "recipes": data["recipes"]})
            
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing error: {e}")
            logging.error(f"Response text: {response_text}")
            return jsonify({
                "success": False,
                "message": "Failed to parse recipe suggestions. Please try again."
            })

    except Exception as e:
        logging.error(f"Error in chat_recipe_suggestions: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while generating recipe suggestions. Please try again."
        })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower()
        
        # Check if the message is about recipe suggestions
        if any(keyword in user_message for keyword in ['recipe', 'suggest', 'make', 'bake', 'cook']):
            # Extract ingredients from the message
            ingredients = []
            for ingredient in get_all_ingredients():
                if ingredient.lower() in user_message:
                    ingredients.append(ingredient)
            
            if ingredients:
                # Find recipes that use these ingredients
                matching_recipes = find_recipes_by_ingredients(ingredients)
                
                if matching_recipes:
                    # Sort recipes by ingredient match percentage
                    sorted_recipes = sorted(matching_recipes, key=lambda x: x['match_percentage'], reverse=True)
                    
                    # Only include recipes with high ingredient match (70% or more)
                    good_matches = [recipe for recipe in sorted_recipes if recipe['match_percentage'] >= 70]
                    
                    if good_matches:
                        response = []
                        # Show top 4 matches
                        for recipe in good_matches[:4]:
                            full_recipe = get_recipe_by_id(recipe['id'])
                            if full_recipe:
                                recipe_text = f"🍳 {full_recipe['name']}\n"
                                recipe_text += f"Matching ingredients: {recipe['match_percentage']}%\n\n"
                                recipe_text += "Ingredients:\n"
                                # Use a set to track unique ingredients
                                seen_ingredients = set()
                                for ing in full_recipe['ingredients']:
                                    ing_key = f"{ing['amount']} {ing['name']}"
                                    if ing_key not in seen_ingredients:
                                        recipe_text += f"• {ing_key}\n"
                                        seen_ingredients.add(ing_key)
                                
                                if recipe['missing_ingredients']:
                                    recipe_text += "\nMissing:\n"
                                    # Use a set to track unique missing ingredients
                                    seen_missing = set()
                                    for missing in recipe['missing_ingredients']:
                                        if missing not in seen_missing:
                                            recipe_text += f"• {missing}\n"
                                            seen_missing.add(missing)
                                
                                recipe_text += "\nSteps:\n"
                                for i, step in enumerate(full_recipe['instructions'], 1):
                                    recipe_text += f"{i}. {step}\n"
                                
                                response.append(recipe_text)
                        
                        return jsonify({"response": "\n\n".join(response)})
                    else:
                        return jsonify({"response": "❌ No recipes found with enough matching ingredients (need 70% or more)."})
                else:
                    return jsonify({"response": "❌ No recipes found with those ingredients."})
            else:
                return jsonify({"response": "❓ Please mention some ingredients you have."})
        
        # For non-recipe queries, use Gemini
        response = model.generate_content(user_message)
        return jsonify({"response": response.text})
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({"response": "Sorry, I encountered an error. Please try again."})

@app.route('/api/adjust_recipe', methods=['POST'])
def adjust_recipe():
    try:
        data = request.get_json()
        recipe_id = data.get('recipe_id')
        servings = data.get('servings')
        texture = data.get('texture')

        if not recipe_id or not servings:
            return jsonify({
                'success': False,
                'message': 'Missing required parameters'
            }), 400

        # Get the original recipe
        recipe = get_recipe_by_id(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found'
            }), 404

        # Calculate adjustment factor
        original_servings = recipe.get('serving_size', 1)
        adjustment_factor = float(servings) / float(original_servings)

        # Adjust ingredients
        adjusted_ingredients = []
        for ingredient in recipe.get('ingredients', []):
            # Get ingredient name from the ingredient dictionary
            ingredient_name = ingredient.get('ingredient_name', '')
            if not ingredient_name:
                ingredient_name = ingredient.get('name', '')
            
            # Get amount and unit
            amount = ingredient.get('amount', 0)
            unit = ingredient.get('unit', '')
            
            # Calculate adjusted amount
            adjusted_amount = float(amount) * adjustment_factor
            
            adjusted_ingredients.append({
                'name': ingredient_name,
                'original_amount': f"{amount} {unit}",
                'adjusted_amount': f"{adjusted_amount:.2f} {unit}"
            })

        return jsonify({
            'success': True,
            'original_servings': original_servings,
            'adjusted_servings': servings,
            'texture': texture,
            'adjusted_ingredients': adjusted_ingredients
        })

    except Exception as e:
        logger.error(f"Error adjusting recipe: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def convert_to_base_unit(amount, unit):
    """Convert various units to base units for scaling."""
    try:
        # Handle fractions
        if '/' in str(amount):
            whole, fraction = str(amount).split()
            num, denom = map(int, fraction.split('/'))
            amount = float(whole) + (num / denom)
        else:
            amount = float(amount)
            
        # Convert to base units
        unit = unit.lower().strip()
        if unit in ['cup', 'cups']:
            return amount * 16  # Convert to tablespoons
        elif unit in ['tbsp', 'tablespoon', 'tablespoons']:
            return amount * 3  # Convert to teaspoons
        elif unit in ['tsp', 'teaspoon', 'teaspoons']:
            return amount
        elif unit in ['oz', 'ounce', 'ounces']:
            return amount * 2  # Convert to tablespoons
        elif unit in ['lb', 'pound', 'pounds']:
            return amount * 16  # Convert to ounces
        elif unit in ['g', 'gram', 'grams']:
            return amount
        elif unit in ['kg', 'kilogram', 'kilograms']:
            return amount * 1000  # Convert to grams
        elif unit in ['ml', 'milliliter', 'milliliters']:
            return amount
        elif unit in ['l', 'liter', 'liters']:
            return amount * 1000  # Convert to milliliters
        else:
            return amount  # Return as is for other units
    except:
        return None

def convert_from_base_unit(amount, unit):
    """Convert from base units back to original unit."""
    try:
        unit = unit.lower().strip()
        if unit in ['cup', 'cups']:
            return round(amount / 16, 2)  # Convert from tablespoons
        elif unit in ['tbsp', 'tablespoon', 'tablespoons']:
            return round(amount / 3, 2)  # Convert from teaspoons
        elif unit in ['tsp', 'teaspoon', 'teaspoons']:
            return round(amount, 2)
        elif unit in ['oz', 'ounce', 'ounces']:
            return round(amount / 2, 2)  # Convert from tablespoons
        elif unit in ['lb', 'pound', 'pounds']:
            return round(amount / 16, 2)  # Convert from ounces
        elif unit in ['g', 'gram', 'grams']:
            return round(amount, 2)
        elif unit in ['kg', 'kilogram', 'kilograms']:
            return round(amount / 1000, 2)  # Convert from grams
        elif unit in ['ml', 'milliliter', 'milliliters']:
            return round(amount, 2)
        elif unit in ['l', 'liter', 'liters']:
            return round(amount / 1000, 2)  # Convert from milliliters
        else:
            return round(amount, 2)  # Return as is for other units
    except:
        return amount

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/test_image')
def test_image():
    """Test route to verify image path"""
    try:
        image_path = os.path.join('static', 'images', 'ingredients', 'defualt_ingr.jpeg')
        if os.path.exists(image_path):
            return send_file(image_path, mimetype='image/jpeg')
        else:
            return f"Image not found at: {image_path}", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/calibrate')
def calibrate_page():
    return render_template('calibrate.html')

@app.route('/api/calibrate', methods=['POST'])
def calibrate():
    try:
        data = request.json
        image_data = data['image'].split(',')[1]  # Remove data URL prefix
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process image to get pixel height
        result = measurement_detector.process_measurement(image)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'message': 'Failed to detect measuring tool'
            })
        
        return jsonify({
            'success': True,
            'pixel_height': result['pixel_height']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/save_calibration', methods=['POST'])
def save_calibration():
    try:
        data = request.json
        tool_type = data['tool_type']
        measurements = data['measurements']
        
        # Sort measurements by fill level
        measurements.sort(key=lambda x: x['fill_level'])
        
        # Extract pixel heights and volumes
        pixel_heights = [m['pixel_height'] for m in measurements]
        volumes = [m['volume'] for m in measurements]
        
        # Calibrate the tool
        success = calibrator.calibrate_container(
            tool_type=tool_type,
            pixel_heights=pixel_heights,
            volumes=volumes
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Calibration saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save calibration'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
