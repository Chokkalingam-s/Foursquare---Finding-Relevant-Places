# app/ml/traffic_predictor.py
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class TrafficPredictor:
    def __init__(self):
        # Business type traffic patterns (hourly weights 0-23)
        self.traffic_patterns = {
            'food_truck': {
                'weekday': [0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.6, 0.8, 0.7, 0.6, 0.9, 1.0, 0.8, 0.6, 0.4, 0.3, 0.7, 0.9, 0.8, 0.6, 0.4, 0.2, 0.1],
                'weekend': [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.3, 0.5, 0.7, 0.8, 0.9, 1.0, 0.9, 0.8, 0.7, 0.6, 0.7, 0.8, 0.7, 0.5, 0.3, 0.2, 0.1]
            },
            'retail': {
                'weekday': [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.3, 0.5, 0.7, 0.8, 0.9, 1.0, 0.9, 0.8, 0.7, 0.8, 0.9, 0.7, 0.5, 0.3, 0.2, 0.1, 0.1],
                'weekend': [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.1]
            }
        }
    
    def predict_hourly_traffic(self, business_type: str, date: datetime = None) -> List[float]:
        """Predict hourly traffic for a specific date"""
        if date is None:
            date = datetime.now()
        
        is_weekend = date.weekday() >= 5
        day_type = 'weekend' if is_weekend else 'weekday'
        
        pattern = self.traffic_patterns.get(business_type, self.traffic_patterns['retail'])
        return pattern[day_type]
    
    def get_peak_hours(self, business_type: str) -> Dict:
        """Get peak hours for business type"""
        weekday_pattern = self.traffic_patterns.get(business_type, self.traffic_patterns['retail'])['weekday']
        weekend_pattern = self.traffic_patterns.get(business_type, self.traffic_patterns['retail'])['weekend']
        
        weekday_peaks = [i for i, val in enumerate(weekday_pattern) if val > 0.7]
        weekend_peaks = [i for i, val in enumerate(weekend_pattern) if val > 0.7]
        
        return {
            'weekday_peaks': [f"{hour:02d}:00" for hour in weekday_peaks],
            'weekend_peaks': [f"{hour:02d}:00" for hour in weekend_peaks]
        }