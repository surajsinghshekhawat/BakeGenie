import cv2
import numpy as np
import logging
from typing import Dict, Tuple, Optional
from .calibration import calibrator

logger = logging.getLogger(__name__)

class MeasurementDetector:
    def __init__(self):
        """Initialize the measurement detector"""
        logger.info("Initializing MeasurementDetector")
        self.min_confidence = 0.5
        self.max_volume = 1000  # ml
        self.max_weight = 2000  # g
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better detection"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive histogram equalization
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
        
        return blurred
    
    def detect_container(self, image: np.ndarray) -> Tuple[Optional[np.ndarray], float]:
        """Detect measuring container in the image"""
        try:
            # Preprocess image
            processed = self.preprocess_image(image)
            
            # Apply Canny edge detection
            edges = cv2.Canny(processed, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None, 0.0
            
            # Find the largest contour (assuming it's the container)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate confidence based on contour properties
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
            
            # Higher confidence for more circular shapes
            confidence = min(1.0, circularity * 1.5)
            
            return largest_contour, confidence
            
        except Exception as e:
            logger.error(f"Error detecting container: {e}")
            return None, 0.0
    
    def estimate_fill_level(self, image: np.ndarray, contour: np.ndarray) -> Tuple[float, float]:
        """Estimate fill level based on ingredient color and container shape"""
        try:
            # Create mask for the container
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Get average saturation and value in the container area
            mean_saturation = np.mean(hsv[mask > 0, 1])
            mean_value = np.mean(hsv[mask > 0, 2])
            
            # Apply adaptive thresholding based on lighting conditions
            if mean_value < 100:  # Low light
                threshold = 30
            elif mean_value > 200:  # Bright light
                threshold = 50
            else:  # Normal lighting
                threshold = 40
            
            # Create binary mask for filled area
            _, binary = cv2.threshold(hsv[:,:,2], threshold, 255, cv2.THRESH_BINARY)
            binary = cv2.bitwise_and(binary, mask)
            
            # Find the top edge of the filled area
            filled_pixels = np.where(binary > 0)
            if len(filled_pixels[0]) == 0:
                return 0.0, 0
            
            top_edge = np.min(filled_pixels[0])
            bottom_edge = np.max(filled_pixels[0])
            height = bottom_edge - top_edge
            
            # Calculate fill percentage
            total_height = np.max(contour[:,:,1]) - np.min(contour[:,:,1])
            fill_percentage = height / total_height if total_height > 0 else 0
            
            return fill_percentage, height
            
        except Exception as e:
            logger.error(f"Error estimating fill level: {e}")
            return 0.0, 0
    
    def process_measurement(self, image: np.ndarray, tool_type: str = None) -> Dict:
        """Process measurement image and return results"""
        try:
            # Detect container
            contour, confidence = self.detect_container(image)
            if contour is None:
                return {
                    'success': False,
                    'message': 'No measuring container detected'
                }
            
            # Estimate fill level
            fill_percentage, pixel_height = self.estimate_fill_level(image, contour)
            
            # Get calibrated volume if tool type is provided
            volume = None
            if tool_type:
                volume = calibrator.get_calibrated_volume(tool_type, pixel_height)
                
            # Validate measurement if volume is available
            if volume:
                is_valid = calibrator.validate_measurement(tool_type, volume)
                if not is_valid:
                    return {
                        'success': False,
                        'message': 'Measurement outside valid range'
                    }
                    
            return {
                'success': True,
                'fill_percentage': fill_percentage,
                'pixel_height': pixel_height,
                'volume': volume,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error processing measurement: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            } 