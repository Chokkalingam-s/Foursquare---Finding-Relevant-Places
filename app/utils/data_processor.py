# app/utils/data_processor.py
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from geopy.distance import geodesic
import re
from collections import Counter

class DataProcessor:
    def __init__(self):
        self.business_categories = {
            'food_truck': ['food', 'restaurant', 'cafe', 'truck'],
            'retail': ['shop', 'store', 'boutique', 'market'],
            'service': ['salon', 'repair', 'cleaning', 'consultation'],
            'entertainment': ['music', 'art', 'performance', 'event']
        }
    
    def calculate_distance(self, loc1: Tuple[float, float], 
                          loc2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates in meters"""
        return geodesic(loc1, loc2).meters
    
    def analyze_competition_density(self, target_location: Tuple[float, float],
                                  businesses: List[Dict], 
                                  business_type: str) -> Dict:
        """Analyze competition density around a target location"""
        relevant_businesses = []
        
        for business in businesses:
            if self._is_competitor(business, business_type):
                business_location = (
                    business.get('geocodes', {}).get('main', {}).get('latitude', 0),
                    business.get('geocodes', {}).get('main', {}).get('longitude', 0)
                )
                distance = self.calculate_distance(target_location, business_location)
                
                if distance <= 500:  # Within 500m radius
                    relevant_businesses.append({
                        'business': business,
                        'distance': distance
                    })
        
        # Calculate density metrics
        total_competitors = len(relevant_businesses)
        avg_rating = np.mean([b['business'].get('rating', 0) for b in relevant_businesses if b['business'].get('rating')])
        
        # Competition density score (lower is better for new business)
        density_score = max(0, 100 - (total_competitors * 10))
        
        return {
            'total_competitors': total_competitors,
            'average_competitor_rating': avg_rating if not np.isnan(avg_rating) else 0,
            'density_score': density_score,
            'nearby_competitors': relevant_businesses[:5]  # Top 5 closest
        }
    
    def _is_competitor(self, business: Dict, business_type: str) -> bool:
        """Check if a business is a competitor for the given business type"""
        categories = [cat.get('name', '').lower() for cat in business.get('categories', [])]
        name = business.get('name', '').lower()
        
        keywords = self.business_categories.get(business_type, [])
        
        for keyword in keywords:
            if any(keyword in category for category in categories) or keyword in name:
                return True
        
        return False
    
    def calculate_foot_traffic_score(self, businesses: List[Dict], 
                                   target_location: Tuple[float, float]) -> float:
        """Calculate foot traffic score based on nearby popular venues"""
        traffic_score = 0
        
        for business in businesses:
            business_location = (
                business.get('geocodes', {}).get('main', {}).get('latitude', 0),
                business.get('geocodes', {}).get('main', {}).get('longitude', 0)
            )
            distance = self.calculate_distance(target_location, business_location)
            
            if distance <= 200:  # Very close
                popularity = business.get('popularity', 0)
                traffic_score += popularity * 1.5
            elif distance <= 500:  # Close
                popularity = business.get('popularity', 0)
                traffic_score += popularity * 1.0
            elif distance <= 1000:  # Nearby
                popularity = business.get('popularity', 0)
                traffic_score += popularity * 0.5
        
        # Normalize score to 0-100
        return min(100, traffic_score / 10)
    
    def identify_category_gaps(self, businesses: List[Dict], 
                              target_business_type: str) -> List[str]:
        """Identify underserved business categories in the area"""
        present_categories = set()
        
        for business in businesses:
            categories = [cat.get('name', '') for cat in business.get('categories', [])]
            present_categories.update(categories)
        
        # Define essential categories for different areas
        essential_categories = {
            'food_truck': ['Coffee Shop', 'Fast Food', 'Grocery Store', 'Bakery'],
            'retail': ['Clothing Store', 'Electronics Store', 'Bookstore', 'Pharmacy'],
            'service': ['Hair Salon', 'Laundry', 'Bank', 'Post Office'],
            'entertainment': ['Cinema', 'Bar', 'Gym', 'Park']
        }
        
        gaps = []
        target_essentials = essential_categories.get(target_business_type, [])
        
        for category in target_essentials:
            if not any(category.lower() in present_cat.lower() for present_cat in present_categories):
                gaps.append(category)
        
        return gaps
    
    def analyze_demographic_patterns(self, businesses: List[Dict]) -> Dict:
        """Analyze demographic patterns from business types"""
        category_counts = Counter()
        price_levels = []
        
        for business in businesses:
            categories = [cat.get('name', '') for cat in business.get('categories', [])]
            category_counts.update(categories)
            
            if business.get('price'):
                price_levels.append(business['price'])
        
        # Infer demographics
        demographics = {
            'affluence_indicator': np.mean(price_levels) if price_levels else 2,
            'family_friendly': self._count_family_venues(category_counts),
            'young_professional': self._count_professional_venues(category_counts),
            'tourist_area': self._count_tourist_venues(category_counts),
            'dominant_categories': category_counts.most_common(5)
        }
        
        return demographics
    
    def _count_family_venues(self, category_counts: Counter) -> int:
        """Count family-friendly venue indicators"""
        family_keywords = ['park', 'playground', 'school', 'family', 'kids']
        count = 0
        for category, freq in category_counts.items():
            if any(keyword in category.lower() for keyword in family_keywords):
                count += freq
        return count
    
    def _count_professional_venues(self, category_counts: Counter) -> int:
        """Count young professional venue indicators"""
        professional_keywords = ['office', 'coworking', 'coffee', 'gym', 'bar']
        count = 0
        for category, freq in category_counts.items():
            if any(keyword in category.lower() for keyword in professional_keywords):
                count += freq
        return count
    
    def _count_tourist_venues(self, category_counts: Counter) -> int:
        """Count tourist venue indicators"""
        tourist_keywords = ['museum', 'tourist', 'hotel', 'attraction', 'landmark']
        count = 0
        for category, freq in category_counts.items():
            if any(keyword in category.lower() for keyword in tourist_keywords):
                count += freq
        return count
    
    def extract_location_coordinates(self, location_string: str) -> Optional[Tuple[float, float]]:
        """Extract lat, lng from location string or address"""
        # Simple regex to extract coordinates if provided
        coord_pattern = r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)'
        match = re.search(coord_pattern, location_string)
        
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            return (lat, lng)
        
        return None
