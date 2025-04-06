"""
YOLOv8-based real-time measurement detection system
"""

import cv2
import numpy as np
import torch
from ultralytics import YOLO
import logging
from database.ingredients_db import get_ingredient_by_name, get_measurement_by_name
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MeasurementDetector:
    def __init__(self):
        """Initialize the measurement detector with YOLOv8 model"""
        try:
            # Use YOLOv8n model for faster detection
            model_path = 'yolov8n.pt'
            if not os.path.exists(model_path):
                logger.error(f"YOLO model file not found at {model_path}")
                raise FileNotFoundError(f"YOLO model file not found at {model_path}")
            
            self.model = YOLO(model_path)
            logger.info("YOLO model loaded successfully")
            
            # Configure model parameters
            self.conf_threshold = 0.15  # Lower confidence threshold for better detection
            self.iou_threshold = 0.4    # Lower IOU threshold for better detection
            self.max_det = 20           # Increase maximum detections
            
            # Define measurement tool classes
            self.spoon_classes = [44, 46, 47]  # Multiple class IDs for spoons
            self.cup_classes = [45, 48]        # Multiple class IDs for cups
            
            logger.info("Measurement detector initialized with enhanced configuration")
            
        except Exception as e:
            logger.error(f"Error initializing measurement detector: {e}")
            raise
    
    def detect_tools(self, frame):
        """Detect measuring tools in the frame"""
        try:
            # Run YOLO detection
            results = self.model(frame, conf=self.conf_threshold, iou=self.iou_threshold, max_det=self.max_det)[0]
            
            # Initialize lists for detections
            spoons = []
            cups = []
            
            # Process detections
            for box in results.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Calculate aspect ratio
                width = x2 - x1
                height = y2 - y1
                aspect_ratio = width / height if height > 0 else 0
                
                # Log detection details
                logger.info(f"Detection: class={class_id}, conf={confidence:.2f}, ratio={aspect_ratio:.2f}")
                
                # Check if detection is a spoon
                if class_id in self.spoon_classes and 0.3 < aspect_ratio < 3.0:
                    spoons.append({
                        'bbox': (x1, y1, x2, y2),
                        'confidence': confidence,
                        'class_id': class_id
                    })
                
                # Check if detection is a cup
                elif class_id in self.cup_classes and 0.5 < aspect_ratio < 2.0:
                    cups.append({
                        'bbox': (x1, y1, x2, y2),
                        'confidence': confidence,
                        'class_id': class_id
                    })
            
            logger.info(f"Found {len(spoons)} spoons and {len(cups)} cups")
            return spoons, cups
            
        except Exception as e:
            logger.error(f"Error detecting tools: {e}")
            return [], []
    
    def estimate_volume(self, tool_type, bbox):
        """Estimate the volume of ingredients in the detected tool"""
        try:
            x1, y1, x2, y2 = bbox
            width = x2 - x1
            height = y2 - y1
            
            # Calculate volume based on tool type and size
            if tool_type == 'spoon':
                # Assume standard tablespoon is about 15ml
                volume = (width * height) / 1000  # Convert to ml
                return max(5, min(volume, 30))  # Limit between 5ml and 30ml
            
            elif tool_type == 'cup':
                # Assume standard cup is about 240ml
                volume = (width * height) / 100  # Convert to ml
                return max(30, min(volume, 500))  # Limit between 30ml and 500ml
            
            return 0
            
        except Exception as e:
            logger.error(f"Error estimating volume: {e}")
            return 0
    
    def process_measurements(self, frame):
        """Process the frame and return detected measurements"""
        try:
            # Detect tools
            spoons, cups = self.detect_tools(frame)
            
            # Process measurements
            measurements = []
            
            # Process spoons
            for spoon in spoons:
                volume = self.estimate_volume('spoon', spoon['bbox'])
                measurements.append({
                    'type': 'spoon',
                    'volume': volume,
                    'confidence': spoon['confidence'],
                    'bbox': spoon['bbox']
                })
            
            # Process cups
            for cup in cups:
                volume = self.estimate_volume('cup', cup['bbox'])
                measurements.append({
                    'type': 'cup',
                    'volume': volume,
                    'confidence': cup['confidence'],
                    'bbox': cup['bbox']
                })
            
            logger.info(f"Processed {len(measurements)} measurements")
            return measurements
            
        except Exception as e:
            logger.error(f"Error processing measurements: {e}")
            return []
    
    def preprocess_frame(self, frame):
        """Preprocess frame for better detection"""
        # Convert to RGB (YOLO expects RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Normalize
        normalized = rgb_frame.astype(np.float32) / 255.0
        
        return normalized
    
    def process_measurement(self, frame, ingredient_name, measurement_type):
        """Process frame to detect tools and measure ingredients"""
        # Detect tools
        spoons, cups = self.detect_tools(frame)
        
        if not spoons and not cups:
            return {
                'success': False,
                'message': 'No measuring tools detected',
                'debug_frame': frame
            }
        
        # Find best detection matching the measurement type
        best_detection = None
        for detection in spoons + cups:
            if ('cup' in measurement_type and detection['class_id'] in self.cup_classes) or \
               ('spoon' in measurement_type and detection['class_id'] in self.spoon_classes):
                if best_detection is None or detection['confidence'] > best_detection['confidence']:
                    best_detection = detection
        
        if best_detection is None:
            return {
                'success': False,
                'message': f'No matching {measurement_type} detected',
                'debug_frame': frame
            }
        
        # Estimate volume
        fill_percentage = self.estimate_volume(measurement_type, best_detection['bbox'])
        
        # Get measurement data
        measurement_data = get_measurement_by_name(measurement_type)
        if not measurement_data:
            return {
                'success': False,
                'message': f'Unknown measurement type: {measurement_type}',
                'debug_frame': frame
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
                'debug_frame': frame
            }
        
        # Get density with fallback
        density = ingredient_data.get('density', 1.0)  # Default density of 1.0 g/ml if not specified
        
        # Calculate weight
        weight = actual_volume * density
        
        # Add measurement info to debug frame
        cv2.putText(frame, f"Fill: {fill_percentage:.1f}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Volume: {actual_volume:.1f}ml", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Weight: {weight:.1f}g", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return {
            'success': True,
            'volume_ml': round(actual_volume, 2),
            'weight_g': round(weight, 2),
            'fill_percentage': round(fill_percentage),
            'confidence': round(best_detection['confidence'] * 100, 2),
            'debug_frame': frame
        } 