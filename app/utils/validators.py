# app/utils/validators.py
import re
from typing import Dict, List, Optional, Tuple

class Validators:
    @staticmethod
    def validate_coordinates(lat: float, lng: float) -> bool:
        """Validate latitude and longitude"""
        return -90 <= lat <= 90 and -180 <= lng <= 180
    
    @staticmethod
    def validate_business_type(business_type: str) -> bool:
        """Validate business type"""
        valid_types = ['food_truck', 'retail', 'service', 'entertainment']
        return business_type.lower() in valid_types
    
    @staticmethod
    def validate_radius(radius: int) -> bool:
        """Validate search radius"""
        return 100 <= radius <= 10000  # 100m to 10km
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """Sanitize user input"""
        if not input_string:
            return ""
        
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>"\']', '', input_string)
        return sanitized.strip()
    
    @staticmethod
    def validate_api_response(response_data: Dict) -> bool:
        """Validate Foursquare API response structure"""
        if not isinstance(response_data, dict):
            return False
        
        # Check for error in response
        if 'error' in response_data:
            return False
        
        # Check for results
        if 'results' in response_data:
            return isinstance(response_data['results'], list)
        
        return True