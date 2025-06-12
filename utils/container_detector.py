import torch
import torchvision
import numpy as np
import cv2
from typing import Dict, Tuple, List
import logging

logger = logging.getLogger(__name__)

class ContainerDetector:
    def __init__(self, model_path: str):
        """Initialize the container detector with a trained model"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model(model_path)
        self.model.to(self.device)
        self.model.eval()
        
        # Container database with more precise measurements
        self.container_db = {
            'teaspoon': {
                'height_cm': 2.5,
                'diameter_cm': 4.0,
                'volume_ml': 5,
                'shape': 'hemisphere',
                'aspect_ratio_range': (0.8, 1.2),
                'relative_size_range': (0.05, 0.15)
            },
            'tablespoon': {
                'height_cm': 3.0,
                'diameter_cm': 5.0,
                'volume_ml': 15,
                'shape': 'hemisphere',
                'aspect_ratio_range': (0.8, 1.2),
                'relative_size_range': (0.07, 0.20)
            },
            'small_cup': {
                'height_cm': 8.0,
                'diameter_cm': 7.0,
                'volume_ml': 250,
                'shape': 'cylinder',
                'aspect_ratio_range': (1.0, 1.5),
                'relative_size_range': (0.15, 0.30)
            },
            'large_cup': {
                'height_cm': 10.0,
                'diameter_cm': 8.0,
                'volume_ml': 350,
                'shape': 'cylinder',
                'aspect_ratio_range': (1.0, 1.5),
                'relative_size_range': (0.20, 0.35)
            }
        }
        
    def _load_model(self, model_path: str) -> torch.nn.Module:
        """Load the trained model"""
        try:
            # Create model with ResNet50 backbone for better feature extraction
            backbone = torchvision.models.resnet50(pretrained=True)
            backbone.out_channels = 2048
            
            # Create anchor generator with more precise scales
            anchor_generator = torchvision.models.detection.rpn.AnchorGenerator(
                sizes=((32, 64, 128, 256, 512),),
                aspect_ratios=((0.5, 1.0, 2.0),)
            )
            
            # Create ROI Pooler with better feature extraction
            roi_pooler = torchvision.ops.MultiScaleRoIAlign(
                featmap_names=['0'],
                output_size=7,
                sampling_ratio=2
            )
            
            # Create the model
            model = torchvision.models.detection.FasterRCNN(
                backbone,
                num_classes=2,  # Background + container
                rpn_anchor_generator=anchor_generator,
                box_roi_pool=roi_pooler,
                box_score_thresh=0.7,  # Higher confidence threshold
                box_nms_thresh=0.5     # Stricter NMS
            )
            
            # Load trained weights
            checkpoint = torch.load(model_path, map_location=self.device)
            model.load_state_dict(checkpoint['model_state_dict'])
            
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
            
    def detect_containers(self, image: np.ndarray) -> List[Dict]:
        """Detect containers in the image with improved accuracy"""
        try:
            # Preprocess image
            image_tensor = self._preprocess_image(image)
            
            # Make prediction
            with torch.no_grad():
                predictions = self.model([image_tensor])
            
            # Process predictions
            boxes = predictions[0]['boxes'].cpu().numpy()
            scores = predictions[0]['scores'].cpu().numpy()
            
            # Filter predictions
            valid_predictions = []
            for box, score in zip(boxes, scores):
                if score > 0.7:  # High confidence threshold
                    # Get container type and view angle
                    container_type = self._classify_container(box, image.shape)
                    view_angle = self._detect_view_angle(box)
                    
                    # Calculate fill level
                    fill_level = self._calculate_fill_level(image, box, view_angle)
                    
                    # Calculate volume
                    volume_info = self._estimate_volume(box, fill_level, view_angle, container_type)
                    
                    valid_predictions.append({
                        'box': box,
                        'score': score,
                        'container_type': container_type,
                        'view_angle': view_angle,
                        'fill_level': fill_level,
                        'volume_info': volume_info
                    })
            
            return valid_predictions
            
        except Exception as e:
            logger.error(f"Error detecting containers: {e}")
            return []
            
    def _preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """Preprocess image for better detection"""
        # Convert to RGB if needed
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        elif image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
        # Apply adaptive histogram equalization
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        enhanced = cv2.merge((cl,a,b))
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        
        # Convert to tensor
        image_tensor = torch.from_numpy(enhanced).permute(2, 0, 1).float() / 255.0
        return image_tensor
        
    def _classify_container(self, box: np.ndarray, image_shape: Tuple[int, int, int]) -> str:
        """Classify container type with improved accuracy"""
        height, width = image_shape[:2]
        box_height = box[3] - box[1]
        box_width = box[2] - box[0]
        
        # Calculate relative size and aspect ratio
        relative_size = (box_height * box_width) / (height * width)
        aspect_ratio = box_width / box_height
        
        # Find best matching container
        best_match = None
        min_diff = float('inf')
        
        for container_type, info in self.container_db.items():
            # Check if aspect ratio is within range
            if not (info['aspect_ratio_range'][0] <= aspect_ratio <= info['aspect_ratio_range'][1]):
                continue
                
            # Check if relative size is within range
            if not (info['relative_size_range'][0] <= relative_size <= info['relative_size_range'][1]):
                continue
                
            # Calculate difference score
            aspect_diff = abs(aspect_ratio - 1.0)  # Ideal aspect ratio is 1.0
            size_diff = abs(relative_size - sum(info['relative_size_range'])/2)
            total_diff = aspect_diff + size_diff
            
            if total_diff < min_diff:
                min_diff = total_diff
                best_match = container_type
                
        return best_match if best_match else 'unknown'
        
    def _detect_view_angle(self, box: np.ndarray) -> str:
        """Detect view angle with improved accuracy"""
        box_height = box[3] - box[1]
        box_width = box[2] - box[0]
        aspect_ratio = box_width / box_height
        
        if 0.9 <= aspect_ratio <= 1.1:
            return "top"
        elif aspect_ratio > 1.5:
            return "side"
        else:
            return "angle"
            
    def _calculate_fill_level(self, image: np.ndarray, box: np.ndarray, view_angle: str) -> float:
        """Calculate fill level with improved accuracy"""
        # Extract ROI
        x1, y1, x2, y2 = map(int, box)
        roi = image[y1:y2, x1:x2]
        
        # Convert to HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        if view_angle == "top":
            # For top view, use color-based segmentation
            # Create mask for the ingredient (assuming it's darker than the container)
            lower_bound = np.array([0, 0, 0])
            upper_bound = np.array([180, 255, 150])
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            
            # Calculate fill level
            total_pixels = mask.size
            filled_pixels = np.sum(mask > 0)
            fill_level = (filled_pixels / total_pixels) * 100
            
        else:  # side or angle view
            # Apply edge detection
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find the largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Calculate fill level
                container_height = roi.shape[0]
                fill_line_position = y + h/2
                fill_level = (1 - (fill_line_position / container_height)) * 100
            else:
                # Fallback to color-based segmentation
                mask = cv2.inRange(hsv, lower_bound, upper_bound)
                if np.any(mask > 0):
                    highest_point = np.min(np.where(mask > 0)[0])
                    fill_level = (1 - (highest_point / mask.shape[0])) * 100
                else:
                    fill_level = 0
                    
        # Adjust for potential overestimation
        if fill_level > 90:
            fill_level = 100
        elif fill_level < 10:
            fill_level = 0
            
        return fill_level
        
    def _estimate_volume(self, box: np.ndarray, fill_level: float, 
                        view_angle: str, container_type: str) -> Dict:
        """Estimate volume with improved accuracy"""
        container_info = self.container_db.get(container_type)
        if not container_info:
            return {
                'volume_ml': None,
                'confidence': 0.0,
                'is_absolute': False
            }
            
        # Get container dimensions
        height_cm = container_info['height_cm']
        diameter_cm = container_info['diameter_cm']
        shape = container_info['shape']
        max_volume_ml = container_info['volume_ml']
        
        # Calculate volume based on shape
        if shape == 'cylinder':
            radius_cm = diameter_cm / 2
            base_area = np.pi * radius_cm * radius_cm
            volume_ml = base_area * height_cm * (fill_level / 100)
        else:  # hemisphere
            radius_cm = diameter_cm / 2
            if fill_level <= 50:
                h = height_cm * (fill_level / 100)
                volume_ml = (np.pi * h * h * (3 * radius_cm - h)) / 3
            else:
                h = height_cm * (1 - fill_level / 100)
                empty_volume = (np.pi * h * h * (3 * radius_cm - h)) / 3
                total_volume = (2/3) * np.pi * radius_cm * radius_cm * radius_cm
                volume_ml = total_volume - empty_volume
                
        # Calculate confidence
        if view_angle == "top":
            confidence = 0.9
        elif view_angle == "side":
            confidence = 0.7
        else:
            confidence = 0.5
            
        # Adjust confidence based on fill level
        if fill_level < 10 or fill_level > 90:
            confidence *= 0.8
            
        return {
            'volume_ml': volume_ml,
            'max_volume_ml': max_volume_ml,
            'confidence': confidence,
            'is_absolute': True
        } 