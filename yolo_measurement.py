"""
YOLOv8-based real-time measurement detection system
"""

import cv2
import numpy as np
import torch
from ultralytics import YOLO
import logging
from database.ingredients_db import get_ingredient_by_name, get_measurement_by_name

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MeasurementDetector:
    def __init__(self):
        """Initialize the YOLO model and measurement system"""
        # Load YOLO model with custom configuration
        self.model = YOLO('yolov8s.pt')  # Use small model for better accuracy
        
        # Configure model parameters
        self.model.conf = 0.3  # Lower confidence threshold for better detection
        self.model.iou = 0.5   # IOU threshold
        self.model.max_det = 5 # Maximum number of detections per frame
        
        # Define measurement tool classes and their corresponding YOLO class IDs
        # YOLO class IDs: spoon (44), bowl (45), cup (41)
        self.tool_classes = {
            'measuring_spoon': [44],  # spoon class
            'measuring_cup': [41, 45]  # cup and bowl classes
        }
        
        # Initialize detection cache
        self.last_detection = None
        self.detection_confidence = 0.3  # Lower confidence threshold
        
        logger.info("Measurement detector initialized with enhanced configuration")
    
    def preprocess_frame(self, frame):
        """Preprocess frame for better detection"""
        # Convert to RGB (YOLO expects RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Normalize
        normalized = rgb_frame.astype(np.float32) / 255.0
        
        return normalized
    
    def detect_tools(self, frame):
        """Detect measuring tools in the frame"""
        # Run YOLO detection
        results = self.model(frame, verbose=False)
        
        # Process results
        detections = []
        debug_frame = frame.copy()
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get box coordinates and convert to integers
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                confidence = float(box.conf.cpu().numpy()[0])
                class_id = int(box.cls.cpu().numpy()[0])
                
                # Determine tool type based on class ID
                tool_type = None
                for tool, class_ids in self.tool_classes.items():
                    if class_id in class_ids:
                        tool_type = tool
                        break
                
                if tool_type and confidence > self.detection_confidence:
                    detection = {
                        'bbox': (x1, y1, x2, y2),
                        'confidence': float(confidence),
                        'class': tool_type
                    }
                    detections.append(detection)
                    
                    # Draw detection on debug frame
                    cv2.rectangle(debug_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"{tool_type}: {confidence:.2f}"
                    cv2.putText(debug_frame, label, (x1, y1-10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return detections, debug_frame
    
    def estimate_volume(self, frame, detection):
        """Estimate volume of ingredient in the detected tool"""
        x1, y1, x2, y2 = detection['bbox']
        tool_region = frame[y1:y2, x1:x2]
        
        if tool_region.size == 0:
            return 0
        
        # Convert to HSV for better ingredient detection
        hsv = cv2.cvtColor(tool_region, cv2.COLOR_BGR2HSV)
        
        # Calculate fill level using adaptive thresholding
        gray = cv2.cvtColor(tool_region, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV, 11, 2)
        
        # Calculate fill percentage
        height = y2 - y1
        sections = 20  # Increase number of sections for more precise measurement
        section_height = height / sections
        filled_sections = 0
        
        for i in range(sections):
            section_y = int(y1 + (sections - i - 1) * section_height)
            section = thresh[int(section_y - section_height):int(section_y), :]
            
            if section.size > 0:
                # Calculate fill using both color and texture
                fill_ratio = np.count_nonzero(section) / section.size
                avg_saturation = np.mean(hsv[int(section_y - section_height):int(section_y), :, 1])
                
                if fill_ratio > 0.2 or avg_saturation > 30:
                    filled_sections += 1
        
        fill_percentage = (filled_sections / sections) * 100
        return min(100, max(0, fill_percentage))  # Clamp between 0 and 100
    
    def process_measurement(self, frame, ingredient_name, measurement_type):
        """Process frame to detect tools and measure ingredients"""
        # Detect tools
        detections, debug_frame = self.detect_tools(frame)
        
        if not detections:
            return {
                'success': False,
                'message': 'No measuring tools detected',
                'debug_frame': debug_frame
            }
        
        # Find best detection matching the measurement type
        best_detection = None
        for detection in detections:
            if ('cup' in measurement_type and 'measuring_cup' in detection['class']) or \
               ('spoon' in measurement_type and 'measuring_spoon' in detection['class']):
                if best_detection is None or detection['confidence'] > best_detection['confidence']:
                    best_detection = detection
        
        if best_detection is None:
            return {
                'success': False,
                'message': f'No matching {measurement_type} detected',
                'debug_frame': debug_frame
            }
        
        # Estimate volume
        fill_percentage = self.estimate_volume(frame, best_detection)
        
        # Get measurement data
        measurement_data = get_measurement_by_name(measurement_type)
        if not measurement_data:
            return {
                'success': False,
                'message': f'Unknown measurement type: {measurement_type}',
                'debug_frame': debug_frame
            }
        
        # Calculate volume
        base_volume = measurement_data['volume_ml']
        actual_volume = base_volume * (fill_percentage / 100)
        
        # Get ingredient density
        ingredient_data = get_ingredient_by_name(ingredient_name)
        if not ingredient_data:
            return {
                'success': False,
                'message': f'Unknown ingredient: {ingredient_name}',
                'debug_frame': debug_frame
            }
        
        # Get density with fallback
        density = ingredient_data.get('density', 1.0)  # Default density of 1.0 g/ml if not specified
        
        # Calculate weight
        weight = actual_volume * density
        
        # Add measurement info to debug frame
        cv2.putText(debug_frame, f"Fill: {fill_percentage:.1f}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(debug_frame, f"Volume: {actual_volume:.1f}ml", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(debug_frame, f"Weight: {weight:.1f}g", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return {
            'success': True,
            'volume_ml': round(actual_volume, 2),
            'weight_g': round(weight, 2),
            'fill_percentage': round(fill_percentage),
            'confidence': round(best_detection['confidence'] * 100, 2),
            'debug_frame': debug_frame
        } 