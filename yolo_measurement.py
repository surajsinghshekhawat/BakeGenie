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
            # Use YOLOv8n model directly
            self.model = YOLO('yolov8n.pt')
            logger.info("YOLO model loaded successfully")
            
            # Configure model parameters - make detection more lenient
            self.conf_threshold = 0.1    # Lower confidence threshold
            self.iou_threshold = 0.3     # Lower IOU threshold
            self.max_det = 10            # More maximum detections
            
            # Define measurement tool classes (COCO dataset IDs)
            # 44: spoon, 45: bowl, 46: banana, 47: apple, 48: sandwich, 49: orange
            self.spoon_classes = [44, 45, 46, 47, 48, 49]  # More class IDs for spoons
            self.cup_classes = [44, 45, 46, 47, 48, 49]    # More class IDs for cups
            
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
                
                # Check if detection is a spoon (very lenient ratio)
                if class_id in self.spoon_classes and 0.1 < aspect_ratio < 5.0:
                    spoons.append({
                        'bbox': (x1, y1, x2, y2),
                        'confidence': confidence,
                        'class_id': class_id
                    })
                
                # Check if detection is a cup (very lenient ratio)
                elif class_id in self.cup_classes and 0.1 < aspect_ratio < 5.0:
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
            
            # Draw bounding boxes on the frame
            debug_frame = frame.copy()
            
            # Draw spoon bounding boxes in green
            for spoon in spoons:
                x1, y1, x2, y2 = spoon['bbox']
                cv2.rectangle(debug_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(debug_frame, f"Spoon {spoon['confidence']:.2f}", (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw cup bounding boxes in blue
            for cup in cups:
                x1, y1, x2, y2 = cup['bbox']
                cv2.rectangle(debug_frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                cv2.putText(debug_frame, f"Cup {cup['confidence']:.2f}", (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
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
            return measurements, debug_frame
            
        except Exception as e:
            logger.error(f"Error processing measurements: {e}")
            return [], frame
    
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
        
        # Draw bounding boxes on the frame
        debug_frame = frame.copy()
        
        # Draw spoon bounding boxes in green
        for spoon in spoons:
            x1, y1, x2, y2 = spoon['bbox']
            cv2.rectangle(debug_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(debug_frame, f"Spoon {spoon['confidence']:.2f}", (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw cup bounding boxes in blue
        for cup in cups:
            x1, y1, x2, y2 = cup['bbox']
            cv2.rectangle(debug_frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(debug_frame, f"Cup {cup['confidence']:.2f}", (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        if not spoons and not cups:
            return {
                'success': False,
                'message': 'No measuring tools detected',
                'debug_frame': debug_frame
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
                'debug_frame': debug_frame
            }
        
        # Estimate volume
        fill_percentage = self.estimate_volume(measurement_type, best_detection['bbox'])
        
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