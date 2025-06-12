"""
RCNN-based measurement detection system for precise ingredient measurement
"""

import torch
import torchvision
import cv2
import numpy as np
from PIL import Image
import logging
from typing import Dict, Tuple, Optional, List
import json
import os
from database.ingredients_db import get_ingredient_by_name, get_measurement_by_name

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Container database
CONTAINER_DATABASE = {
    'teaspoon': {
        'height_cm': 2.5,
        'diameter_cm': 4.0,
        'volume_ml': 5,
        'shape': 'hemisphere'
    },
    'tablespoon': {
        'height_cm': 3.0,
        'diameter_cm': 5.0,
        'volume_ml': 15,
        'shape': 'hemisphere'
    },
    'small_bowl': {
        'height_cm': 6.0,
        'diameter_cm': 12.0,
        'volume_ml': 500,
        'shape': 'hemisphere'
    },
    'small_cup': {
        'height_cm': 8.0,
        'diameter_cm': 7.0,
        'volume_ml': 250,
        'shape': 'cylinder'
    },
    'large_cup': {
        'height_cm': 10.0,
        'diameter_cm': 8.0,
        'volume_ml': 350,
        'shape': 'cylinder'
    }
}

class RCNNMeasurementSystem:
    def __init__(self, model_path: str = 'model_epoch_17_loss_0.1472.pth'):
        """Initialize the RCNN measurement system"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model(model_path)
        self.category_mapping = {
            1: 'objects',
            2: 'big_cup',
            3: 'bowl',
            4: 'ingredient',
            5: 'small_cup',
            6: 'smallspoon',
            7: 'tablespoon',
            8: 'teaspoon'
        }
        
    def _load_model(self, model_path: str) -> torch.nn.Module:
        """Load the trained FasterRCNN model"""
        try:
            # Create model with MobileNetV2 backbone
            backbone = torchvision.models.mobilenet_v2(pretrained=True)
            backbone.out_channels = 1280
            
            # Create FasterRCNN model
            anchor_generator = torchvision.models.detection.rpn.AnchorGenerator(
                sizes=((32, 64, 128, 256, 512),),
                aspect_ratios=((0.5, 1.0, 2.0),)
            )
            
            roi_pooler = torchvision.ops.MultiScaleRoIAlign(
                featmap_names=['0'],
                output_size=7,
                sampling_ratio=2
            )
            
            model = torchvision.models.detection.FasterRCNN(
                backbone=backbone,
                num_classes=9,  # 8 classes + background
                rpn_anchor_generator=anchor_generator,
                box_roi_pool=roi_pooler
            )
            
            # Load trained weights
            model.load_state_dict(torch.load(model_path, map_location=self.device))
            model.to(self.device)
            model.eval()
            
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """Preprocess image for model input"""
        # Convert to RGB if needed
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            
        # Convert to PIL Image
        image = Image.fromarray(image)
        
        # Convert to tensor and normalize
        transform = torchvision.transforms.Compose([
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        return transform(image)
    
    def detect_containers(self, image: np.ndarray) -> List[Dict]:
        """Detect containers in the image using FasterRCNN"""
        try:
            # Preprocess image
            image_tensor = self.preprocess_image(image)
            image_tensor = image_tensor.unsqueeze(0).to(self.device)
            
            # Get predictions
            with torch.no_grad():
                predictions = self.model(image_tensor)
            
            # Process predictions
            boxes = predictions[0]['boxes'].cpu().numpy()
            scores = predictions[0]['scores'].cpu().numpy()
            labels = predictions[0]['labels'].cpu().numpy()
            
            # Filter predictions by confidence
            confidence_threshold = 0.5
            mask = scores > confidence_threshold
            boxes = boxes[mask]
            scores = scores[mask]
            labels = labels[mask]
            
            # Convert to list of detections
            detections = []
            for box, score, label in zip(boxes, scores, labels):
                if label in self.category_mapping:
                    detections.append({
                        'box': box.tolist(),
                        'score': float(score),
                        'label': self.category_mapping[label]
                    })
            
            return detections
            
        except Exception as e:
            logger.error(f"Error detecting containers: {e}")
            return []
    
    def calculate_fill_level(self, image: np.ndarray, box: List[float]) -> float:
        """Calculate fill level using contour analysis"""
        try:
            # Extract ROI
            x1, y1, x2, y2 = map(int, box)
            roi = image[y1:y2, x1:x2]
            
            # Convert to grayscale
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            # Find contours
            contours, _ = cv2.findContours(
                binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            if not contours:
                return 0.0
            
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate fill level
            mask = np.zeros_like(gray)
            cv2.drawContours(mask, [largest_contour], -1, 255, -1)
            
            # Calculate fill percentage
            total_pixels = (x2 - x1) * (y2 - y1)
            filled_pixels = np.sum(mask > 0)
            fill_percentage = filled_pixels / total_pixels
            
            return fill_percentage
            
        except Exception as e:
            logger.error(f"Error calculating fill level: {e}")
            return 0.0
    
    def calculate_volume(self, container_type: str, fill_percentage: float) -> float:
        """Calculate volume based on container type and fill level"""
        try:
            if container_type not in CONTAINER_DATABASE:
                raise ValueError(f"Unknown container type: {container_type}")
            
            container = CONTAINER_DATABASE[container_type]
            max_volume = container['volume_ml']
            
            # Calculate volume based on shape
            if container['shape'] == 'hemisphere':
                # For hemisphere, volume is proportional to height^3
                volume = max_volume * (fill_percentage ** 3)
            else:  # cylinder
                # For cylinder, volume is proportional to height
                volume = max_volume * fill_percentage
            
            return volume
            
        except Exception as e:
            logger.error(f"Error calculating volume: {e}")
            return 0.0
    
    def process_measurement(self, image_path: str, container_type: str, ingredient_type: str) -> Dict:
        """Process measurement and return results"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Detect containers
            detections = self.detect_containers(image)
            if not detections:
                return {
                    'success': False,
                    'message': 'No containers detected'
                }
            
            # Find the best matching container
            best_detection = None
            for detection in detections:
                if detection['label'].lower() in container_type.lower():
                    if best_detection is None or detection['score'] > best_detection['score']:
                        best_detection = detection
            
            if best_detection is None:
                return {
                    'success': False,
                    'message': f'No {container_type} detected'
                }
            
            # Calculate fill level
            fill_percentage = self.calculate_fill_level(image, best_detection['box'])
            
            # Calculate volume
            volume = self.calculate_volume(container_type, fill_percentage)
            
            return {
                'success': True,
                'fill_level': fill_percentage,
                'volume_ml': volume,
                'confidence': best_detection['score']
            }
            
        except Exception as e:
            logger.error(f"Error processing measurement: {e}")
            return {
                'success': False,
                'message': str(e)
            } 