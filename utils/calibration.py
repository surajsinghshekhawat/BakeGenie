import numpy as np
import cv2
import json
import os
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class MeasurementCalibrator:
    def __init__(self):
        self.calibration_data = {}
        self.calibration_file = 'data/calibration.json'
        self.load_calibration()
        
    def load_calibration(self):
        """Load existing calibration data"""
        try:
            if os.path.exists(self.calibration_file):
                with open(self.calibration_file, 'r') as f:
                    self.calibration_data = json.load(f)
                logger.info("Loaded calibration data")
        except Exception as e:
            logger.error(f"Error loading calibration data: {e}")
            self.calibration_data = {}
    
    def save_calibration(self):
        """Save calibration data to file"""
        try:
            os.makedirs(os.path.dirname(self.calibration_file), exist_ok=True)
            with open(self.calibration_file, 'w') as f:
                json.dump(self.calibration_data, f, indent=2)
            logger.info("Saved calibration data")
        except Exception as e:
            logger.error(f"Error saving calibration data: {e}")
    
    def calibrate_container(self, container_type: str, measurements: List[Dict[str, float]]):
        """Calibrate a specific container type with known measurements"""
        try:
            # Sort measurements by volume
            measurements.sort(key=lambda x: x['volume'])
            
            # Extract calibration points
            volumes = [m['volume'] for m in measurements]
            heights = [m['pixel_height'] for m in measurements]
            
            # Generate calibration curve (polynomial fit)
            coeffs = np.polyfit(heights, volumes, 2)
            
            # Store calibration data
            self.calibration_data[container_type] = {
                'coefficients': coeffs.tolist(),
                'min_height': min(heights),
                'max_height': max(heights),
                'min_volume': min(volumes),
                'max_volume': max(volumes)
            }
            
            self.save_calibration()
            return True
        except Exception as e:
            logger.error(f"Error calibrating container {container_type}: {e}")
            return False
    
    def get_calibrated_volume(self, container_type: str, pixel_height: float) -> float:
        """Get calibrated volume for a given pixel height"""
        try:
            if container_type not in self.calibration_data:
                logger.warning(f"No calibration data for {container_type}")
                return None
            
            cal_data = self.calibration_data[container_type]
            coeffs = np.array(cal_data['coefficients'])
            
            # Calculate volume using polynomial
            volume = np.polyval(coeffs, pixel_height)
            
            # Clamp to valid range
            volume = max(cal_data['min_volume'], min(volume, cal_data['max_volume']))
            
            return volume
        except Exception as e:
            logger.error(f"Error getting calibrated volume: {e}")
            return None
    
    def validate_measurement(self, volume: float, container_type: str) -> Tuple[bool, str]:
        """Validate if a measurement is within expected ranges"""
        try:
            if container_type not in self.calibration_data:
                return False, f"No calibration data for {container_type}"
            
            cal_data = self.calibration_data[container_type]
            
            if not (cal_data['min_volume'] <= volume <= cal_data['max_volume']):
                return False, f"Volume {volume} outside calibrated range"
            
            return True, "Valid measurement"
        except Exception as e:
            logger.error(f"Error validating measurement: {e}")
            return False, str(e)

# Global calibrator instance
calibrator = MeasurementCalibrator() 