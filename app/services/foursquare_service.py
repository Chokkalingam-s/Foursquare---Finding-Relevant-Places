# app/services/foursquare_service.py
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from flask import current_app
from app.utils.file_manager import FileManager
from app.utils.data_processor import DataProcessor

class FoursquareService:
    def __init__(self):
        self.api_key = current_app.config['FOURSQUARE_API_KEY']
        self.base_url = current_app.config['FOURSQUARE_BASE_URL']
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.file_manager = FileManager()
        self.data_processor = DataProcessor()
    
    def search_places(self, query: str, location: str, radius: int = 1000, 
                     categories: List[str] = None, limit: int = 50) -> Dict:
        """Search for places using Foursquare Places API"""
        cache_key = f"search_{query}_{location}_{radius}_{limit}"
        
        # Check cache first
        cached_result = self.file_manager.get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        url = f"{self.base_url}/places/search"
        params = {
            'query': query,
            'near': location,
            'radius': radius,
            'limit': limit
        }
        
        if categories:
            params['categories'] = ','.join(categories)
        
        try:
            response = requests.get(url, headers=self.headers, params=params, 
                                  timeout=current_app.config['REQUEST_TIMEOUT'])
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the result
            self.file_manager.cache_data(cache_key, data)
            
            return data
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Foursquare API error: {str(e)}")
            return {'results': [], 'error': str(e)}
    
    def get_place_details(self, place_id: str) -> Dict:
        """Get detailed information about a specific place"""
        cache_key = f"place_details_{place_id}"
        
        cached_result = self.file_manager.get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        url = f"{self.base_url}/places/{place_id}"
        
        try:
            response = requests.get(url, headers=self.headers, 
                                  timeout=current_app.config['REQUEST_TIMEOUT'])
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the result
            self.file_manager.cache_data(cache_key, data)
            
            return data
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Foursquare API error: {str(e)}")
            return {'error': str(e)}
    
    def get_place_tips(self, place_id: str) -> Dict:
        """Get tips/reviews for a specific place"""
        cache_key = f"place_tips_{place_id}"
        
        cached_result = self.file_manager.get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        url = f"{self.base_url}/places/{place_id}/tips"
        
        try:
            response = requests.get(url, headers=self.headers, 
                                  timeout=current_app.config['REQUEST_TIMEOUT'])
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the result
            self.file_manager.cache_data(cache_key, data)
            
            return data
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Foursquare API error: {str(e)}")
            return {'tips': [], 'error': str(e)}
    
    def search_nearby_categories(self, lat: float, lng: float, 
                                radius: int = 1000) -> Dict:
        """Search for various business categories in a location"""
        categories = [
            '13065',  # Food & Beverage
            '17069',  # Retail
            '10032',  # Entertainment
            '12022',  # Professional Services
            '19014'   # Transportation
        ]
        
        cache_key = f"nearby_categories_{lat}_{lng}_{radius}"
        cached_result = self.file_manager.get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        url = f"{self.base_url}/places/nearby"
        params = {
            'll': f"{lat},{lng}",
            'radius': radius,
            'categories': ','.join(categories),
            'limit': 50
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params,
                                  timeout=current_app.config['REQUEST_TIMEOUT'])
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the result
            self.file_manager.cache_data(cache_key, data)
            
            return data
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Foursquare API error: {str(e)}")
            return {'results': [], 'error': str(e)}