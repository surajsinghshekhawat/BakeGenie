import torch
import torchvision
from torchvision.models.detection import FasterRCNN
from torchvision.models.detection.rpn import AnchorGenerator
from torchvision.transforms import functional as F
from PIL import Image
import numpy as np
import cv2
import os
import logging

logger = logging.getLogger(__name__)

class RCNNMeasurementSystem:
    def __init__(self, checkpoint_path=None):
        self.model = self._load_model(checkpoint_path)
        self.category_mapping = {
            1: 'objects',
            2: 'big_cup',
            3: 'bowl',
            4: 'ingredient',
            5: 'small cup',
            6: 'smallspoon',
            7: 'tablespoon',
            8: 'teaspoon'
        }
        
        # Container database with dimensions
        self.container_database = {
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

    def _load_model(self, checkpoint_path):
        """Load the trained RCNN model or create a new one if checkpoint not found"""
        try:
            # Create model with MobileNetV2 backbone
            backbone = torchvision.models.mobilenet_v2(weights='DEFAULT').features
            backbone.out_channels = 1280

            # Create anchor generator
            anchor_generator = AnchorGenerator(
                sizes=((32, 64, 128, 256, 512),),
                aspect_ratios=((0.5, 1.0, 2.0),)
            )

            # Define ROI Pooler
            roi_pooler = torchvision.ops.MultiScaleRoIAlign(
                featmap_names=['0'],
                output_size=7,
                sampling_ratio=2
            )

            # Create the model
            model = FasterRCNN(
                backbone,
                num_classes=9,  # Background + 8 classes
                rpn_anchor_generator=anchor_generator,
                box_roi_pool=roi_pooler
            )

            # Try to load checkpoint if provided
            if checkpoint_path and os.path.exists(checkpoint_path):
                logger.info(f"Loading checkpoint from {checkpoint_path}")
                checkpoint = torch.load(checkpoint_path, map_location=torch.device('cpu'))
                model.load_state_dict(checkpoint['model_state_dict'])
            else:
                logger.warning(f"No checkpoint found at {checkpoint_path}. Using untrained model.")
            
            model.eval()
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def calculate_fill_level(self, roi, container_type, image_path):
        """Calculate fill level using basic thresholding"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY_INV, 11, 2)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                logger.warning("No contours found in image")
                return 0.0
            
            # Get the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Get the bounding box
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Get container info
            container_info = self.container_database[container_type]
            
            # Calculate fill level based on container shape
            if container_info['shape'] == 'cylinder':
                # For cylindrical containers, use the height of the filled area
                fill_height = h
                container_height = roi.shape[0]
                fill_percentage = (fill_height / container_height) * 100
            else:  # hemisphere
                # For hemispherical containers, use area ratio
                total_area = roi.shape[0] * roi.shape[1]
                fill_area = cv2.contourArea(largest_contour)
                fill_percentage = (fill_area / total_area) * 100
            
            # Ensure fill percentage is between 0 and 100
            fill_percentage = max(0.0, min(100.0, fill_percentage))
            
            # Save debug visualization
            debug_img = roi.copy()
            # Draw the contour in green
            cv2.drawContours(debug_img, [largest_contour], -1, (0, 255, 0), 2)
            # Draw the bounding box in blue
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # Add text showing fill percentage and dimensions
            cv2.putText(debug_img, f"Fill: {fill_percentage:.1f}%", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(debug_img, f"Size: {w}x{h}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Save the debug image
            debug_path = os.path.join('static', 'uploads', f'fill_debug_{os.path.basename(image_path)}')
            cv2.imwrite(debug_path, debug_img)
            
            logger.info(f"Fill level calculated: {fill_percentage:.1f}% for {container_type}")
            logger.info(f"Container dimensions: {w}x{h}, ROI size: {roi.shape}")
            return fill_percentage
            
        except Exception as e:
            logger.error(f"Error in calculate_fill_level: {str(e)}")
            return 0.0

    def calculate_volume(self, container_type, fill_level):
        """Calculate volume based on container type and fill level"""
        try:
            container_info = self.container_database[container_type]
            
            if container_info['shape'] == 'cylinder':
                radius = container_info['diameter_cm'] / 2
                height = container_info['height_cm']
                volume = np.pi * radius * radius * height * (fill_level / 100)
            else:  # hemisphere
                radius = container_info['diameter_cm'] / 2
                height = container_info['height_cm']
                if fill_level <= 50:
                    h = height * (fill_level / 100)
                    volume = (np.pi * h * h * (3 * radius - h)) / 3
                else:
                    h = height * (1 - fill_level / 100)
                    empty_volume = (np.pi * h * h * (3 * radius - h)) / 3
                    total_volume = (2/3) * np.pi * radius * radius * radius
                    volume = total_volume - empty_volume
            
            return volume
        except Exception as e:
            logger.error(f"Error in calculate_volume: {str(e)}")
            return 0.0

    def process_image(self, image_path, container_type, confidence_threshold=0.5):
        """Process an image and return measurements"""
        try:
            # Load and transform image
            image = Image.open(image_path).convert("RGB")
            image_tensor = F.to_tensor(image)
            
            # Make prediction
            with torch.no_grad():
                prediction = self.model([image_tensor])
            
            # Get predictions above threshold
            boxes = prediction[0]['boxes'].cpu().numpy()
            scores = prediction[0]['scores'].cpu().numpy()
            labels = prediction[0]['labels'].cpu().numpy()
            
            # Filter by confidence
            mask = scores > confidence_threshold
            boxes = boxes[mask]
            scores = scores[mask]
            labels = labels[mask]
            
            if len(boxes) == 0:
                logger.warning("No containers detected in image")
                return None
            
            # Get the best prediction
            best_idx = np.argmax(scores)
            box = boxes[best_idx]
            score = scores[best_idx]
            label = labels[best_idx]
            
            # Convert PIL image to numpy array for OpenCV processing
            image_np = np.array(image)
            
            # Calculate fill level
            x1, y1, x2, y2 = map(int, box)
            roi = image_np[y1:y2, x1:x2]
            
            # Ensure ROI is not empty
            if roi.size == 0:
                logger.error("Empty ROI detected")
                return None
                
            fill_level = self.calculate_fill_level(roi, container_type, image_path)
            
            # Calculate volume
            volume = self.calculate_volume(container_type, fill_level)
            
            # Save debug image with bounding box
            debug_image = image_np.copy()
            cv2.rectangle(debug_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            debug_path = os.path.join('static', 'uploads', f'debug_{os.path.basename(image_path)}')
            cv2.imwrite(debug_path, cv2.cvtColor(debug_image, cv2.COLOR_RGB2BGR))
            
            logger.info(f"Processed image: fill_level={fill_level:.1f}%, volume={volume:.1f}ml")
            
            return {
                'fill_level': fill_level,
                'volume_ml': volume,
                'confidence': score,
                'container_type': self.category_mapping[label],
                'box': box,
                'debug_image': f'/static/uploads/debug_{os.path.basename(image_path)}'
            }
        except Exception as e:
            logger.error(f"Error in process_image: {str(e)}")
            return None

    def get_measurement(self, image_path, container_type):
        """Get measurement for a specific container type"""
        try:
            result = self.process_image(image_path, container_type)
            
            if result is None:
                return {
                    'error': 'No container detected in image'
                }
            
            return {
                'fill_level': f"{result['fill_level']:.1f}%",
                'volume': f"{result['volume_ml']:.1f}ml",
                'confidence': f"{result['confidence']:.2f}",
                'container_type': result['container_type']
            }
        except Exception as e:
            logger.error(f"Error in get_measurement: {str(e)}")
            return {
                'error': f'Error processing measurement: {str(e)}'
            }

    def process_measurement(self, image_path, container_type, ingredient_type=None):
        """Process measurement for real-time detection"""
        try:
            # Process the image
            result = self.process_image(image_path, container_type)
            
            if result is None:
                return {
                    'success': False,
                    'message': 'No container detected in image'
                }
            
            # Format the result
            response = {
                'success': True,
                'fill_level': result['fill_level'],  # Remove formatting here
                'volume': f"{result['volume_ml']:.1f}ml",
                'confidence': f"{result['confidence']:.2f}",
                'container_type': result['container_type'],
                'debug_image': result['debug_image']
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error in process_measurement: {str(e)}")
            return {
                'success': False,
                'message': f'Error processing measurement: {str(e)}'
            } 