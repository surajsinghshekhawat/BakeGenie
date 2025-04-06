"""
Advanced camera-based measurement system for the Baking AI application
"""

import cv2
import numpy as np
import logging
import base64
from database.ingredients_db import get_ingredient_by_name, get_measurement_by_name

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cache for measurement data to avoid repeated database calls
_measurement_cache = {}
_ingredient_cache = {}

def get_cached_measurement(measurement_type):
    """Get measurement data from cache or database"""
    if measurement_type not in _measurement_cache:
        _measurement_cache[measurement_type] = get_measurement_by_name(measurement_type)
    return _measurement_cache[measurement_type]

def get_cached_ingredient(ingredient_name):
    """Get ingredient data from cache or database"""
    if ingredient_name not in _ingredient_cache:
        _ingredient_cache[ingredient_name] = get_ingredient_by_name(ingredient_name)
    return _ingredient_cache[ingredient_name]

def detect_measuring_tool(image):
    """
    Detect measuring cups or spoons in the image
    Returns the type of tool detected, its contour, and confidence score
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive thresholding for better edge detection
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY_INV, 11, 2)
    
    # Apply morphological operations to clean up the image
    kernel = np.ones((3,3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    # Create debug image
    debug_image = image.copy()
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw all contours for debugging
    cv2.drawContours(debug_image, contours, -1, (0, 255, 0), 1)
    
    # Filter and analyze contours
    valid_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 200:  # Lower minimum area threshold
            # Get rotated rectangle
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            
            # Get width and height of rotated rectangle
            width = rect[1][0]
            height = rect[1][1]
            
            # Calculate aspect ratio considering both orientations
            aspect_ratio = max(width/height if height > 0 else 0, 
                             height/width if width > 0 else 0)
            
            # Check if shape is elongated (spoon-like)
            if aspect_ratio > 1.3:  # More lenient aspect ratio threshold
                valid_contours.append((cnt, aspect_ratio))
                # Draw rotated rectangle
                cv2.drawContours(debug_image, [box], 0, (255, 0, 0), 2)
    
    if not valid_contours:
        return None, None, 0, debug_image
    
    # Find the best spoon candidate
    best_contour = None
    best_score = 0
    
    for cnt, aspect_ratio in valid_contours:
        # Calculate shape metrics
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        
        # Calculate shape features
        convexity = area / hull_area if hull_area > 0 else 0
        compactness = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        
        # Score based on multiple features
        spoon_score = (
            aspect_ratio * 0.4 +  # Weight for elongated shape
            convexity * 0.3 +    # Weight for smooth shape
            (1 - compactness) * 0.3  # Weight for non-circular shape
        ) * 100
        
        if spoon_score > best_score:
            best_score = spoon_score
            best_contour = cnt
    
    if best_contour is not None:
        # Draw the best contour
        cv2.drawContours(debug_image, [best_contour], -1, (0, 0, 255), 2)
        
        # Get rotated rectangle
        rect = cv2.minAreaRect(best_contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        
        # Draw rotated bounding box
        cv2.drawContours(debug_image, [box], 0, (255, 0, 255), 2)
        
        # Add detection info
        cv2.putText(debug_image, f"Spoon Score: {best_score:.1f}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return "spoon", best_contour, best_score, debug_image
    
    return None, None, 0, debug_image

def estimate_fill_level(image, contour):
    """
    Estimate the fill level of the measuring tool
    Returns the fill percentage
    """
    # Create a mask for the measuring tool
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)
    
    # Convert to HSV for better color segmentation
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Extract the region of interest
    roi = cv2.bitwise_and(hsv, hsv, mask=mask)
    
    # Get the bounding rectangle
    x, y, w, h = cv2.boundingRect(contour)
    
    # Initialize bowl parameters
    bowl_height = h
    bowl_y = y
    
    # For spoons, analyze the bowl part (lower portion)
    if h > w:  # If height is greater than width (spoon-like)
        bowl_height = int(h * 0.4)  # Focus on the lower 40% where the bowl is
        bowl_y = y + h - bowl_height
    
    # Divide the bowl into 10 equal horizontal sections
    section_height = bowl_height / 10
    
    # Count from the bottom up to find the fill level
    fill_level = 0
    fill_detected = False
    
    # Create debug image for fill visualization
    debug_image = image.copy()
    
    for i in range(10):
        # Define the section
        section_y = int(bowl_y + bowl_height - (i + 1) * section_height)
        section_height_int = int(section_height)
        
        if section_y < 0 or section_y + section_height_int >= image.shape[0]:
            continue
        
        # Draw section boundaries on debug image
        cv2.line(debug_image, (x, section_y), (x + w, section_y), (0, 255, 255), 1)
        
        # Get the section ROI
        section = roi[section_y:section_y + section_height_int, x:x+w]
        
        # Check if this section has content (ingredient)
        if section.size > 0:
            # Calculate the average saturation and value in this section
            avg_saturation = np.mean(section[:,:,1])
            avg_value = np.mean(section[:,:,2])
            std_hue = np.std(section[:,:,0]) if section[:,:,0].size > 0 else 0
            
            # More strict conditions for detecting fill
            if (avg_saturation > 40 and avg_value < 200) or (std_hue > 25 and avg_value < 180):
                fill_level += 1
                fill_detected = True
                # Draw filled section in green
                cv2.rectangle(debug_image, (x, section_y), (x + w, section_y + section_height_int), (0, 255, 0), -1)
                logger.info(f"Fill detected at section {i}: avg_sat={avg_saturation:.2f}, avg_val={avg_value:.2f}, std_hue={std_hue:.2f}")
            else:
                # Draw empty section in red
                cv2.rectangle(debug_image, (x, section_y), (x + w, section_y + section_height_int), (0, 0, 255), 1)
                # If we've already detected fill below and now find an empty section, stop
                if fill_detected:
                    break
    
    # Calculate fill percentage
    fill_percentage = (fill_level / 10) * 100
    
    logger.info(f"Estimated fill level: {fill_level}/10, percentage: {fill_percentage:.2f}%")
    return fill_percentage, debug_image

def process_measurement_image(image, ingredient_name, measurement_type):
    """
    Process an image to detect a measuring tool and estimate volume
    Returns a dictionary with the measurement results
    """
    logger.info(f"Processing image for {ingredient_name} using {measurement_type}")
    
    # Detect the measuring tool
    tool_type, contour, confidence, debug_image = detect_measuring_tool(image)
    
    # If no valid measuring tool is detected, return error with debug image
    if tool_type is None or contour is None:
        logger.warning("No valid measuring tool detected in the image")
        # Convert debug image to base64 for frontend display
        _, buffer = cv2.imencode('.jpg', debug_image)
        debug_image_base64 = base64.b64encode(buffer).decode('utf-8')
        return {
            "success": False,
            "message": "No measuring cup or spoon detected. Please ensure the measuring tool is clearly visible.",
            "debug_image": f"data:image/jpeg;base64,{debug_image_base64}"
        }
    
    # Check if the detected tool matches the expected measurement type
    expected_tool = "cup" if "cup" in measurement_type.lower() else "spoon"
    if tool_type != expected_tool:
        logger.warning(f"Tool mismatch: expected {expected_tool}, detected {tool_type}")
        return {
            "success": False,
            "message": f"Detected a {tool_type}, but expected a {expected_tool}. Please use the correct measuring tool."
        }
    
    # Estimate fill level
    fill_percentage, fill_debug_image = estimate_fill_level(image, contour)
    
    # If fill level is too low, it might be an empty container
    if fill_percentage < 5:
        logger.warning("Fill level too low, possibly an empty container")
        # Convert debug image to base64 for frontend display
        _, buffer = cv2.imencode('.jpg', fill_debug_image)
        debug_image_base64 = base64.b64encode(buffer).decode('utf-8')
        return {
            "success": False,
            "message": "The measuring tool appears to be empty. Please add some ingredient and try again.",
            "debug_image": f"data:image/jpeg;base64,{debug_image_base64}"
        }
    
    # Get the base volume for the measurement type
    measurement_data = get_cached_measurement(measurement_type)
    
    if not measurement_data:
        logger.error(f"Unknown measurement type: {measurement_type}")
        return {
            "success": False,
            "message": f"Unknown measurement type: {measurement_type}"
        }
    
    # Calculate actual volume based on fill percentage
    base_volume = measurement_data['volume_ml']
    actual_volume = base_volume * (fill_percentage / 100)
    
    # Get ingredient density
    ingredient_data = get_cached_ingredient(ingredient_name)
    
    if not ingredient_data:
        logger.error(f"Unknown ingredient: {ingredient_name}")
        return {
            "success": False,
            "message": f"Unknown ingredient: {ingredient_name}"
        }
    
    # Calculate weight
    density = ingredient_data['density']
    weight = actual_volume * density
    
    logger.info(f"Measurement complete: {actual_volume:.2f}ml of {ingredient_name}, weight: {weight:.2f}g")
    
    # Add measurement info to the debug image
    cv2.putText(fill_debug_image, f"Tool: {tool_type}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(fill_debug_image, f"Fill: {fill_percentage:.1f}%", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(fill_debug_image, f"Volume: {actual_volume:.1f}ml", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(fill_debug_image, f"Weight: {weight:.1f}g", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Convert debug image to base64 for frontend display
    _, buffer = cv2.imencode('.jpg', fill_debug_image)
    debug_image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return {
        "success": True,
        "volume_ml": round(actual_volume, 2),
        "weight_g": round(weight, 2),
        "fill_percentage": round(fill_percentage),
        "tool_type": tool_type,
        "confidence": round(confidence, 2),
        "debug_image": f"data:image/jpeg;base64,{debug_image_base64}"
    }

