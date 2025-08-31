# app/utils/file_manager.py
import json
import os
import time
import hashlib
from typing import Any, Optional, Dict
from flask import current_app
from datetime import datetime, timedelta

class FileManager:
    def __init__(self):
        self.cache_dir = current_app.config['CACHE_DIR']
        self.user_data_dir = current_app.config['USER_DATA_DIR']
        self.analytics_dir = current_app.config['ANALYTICS_DIR']
        self.cache_expiry = current_app.config['CACHE_EXPIRY']
    
    def _get_cache_path(self, key: str) -> str:
        """Generate cache file path from key"""
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed_key}.json")
    
    def cache_data(self, key: str, data: Any) -> bool:
        """Cache data to file system"""
        try:
            cache_path = self._get_cache_path(key)
            cache_data = {
                'data': data,
                'timestamp': time.time(),
                'key': key
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to cache data: {str(e)}")
            return False
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """Retrieve cached data if not expired"""
        try:
            cache_path = self._get_cache_path(key)
            
            if not os.path.exists(cache_path):
                return None
            
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            if time.time() - cache_data['timestamp'] > self.cache_expiry:
                os.remove(cache_path)
                return None
            
            return cache_data['data']
        except Exception as e:
            current_app.logger.error(f"Failed to retrieve cached data: {str(e)}")
            return None
    
    def save_user_analysis(self, analysis_id: str, data: Dict) -> bool:
        """Save user analysis to file system"""
        try:
            file_path = os.path.join(self.user_data_dir, f"{analysis_id}.json")
            analysis_data = {
                'analysis_id': analysis_id,
                'data': data,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            with open(file_path, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to save analysis: {str(e)}")
            return False
    
    def get_user_analysis(self, analysis_id: str) -> Optional[Dict]:
        """Retrieve user analysis"""
        try:
            file_path = os.path.join(self.user_data_dir, f"{analysis_id}.json")
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            current_app.logger.error(f"Failed to retrieve analysis: {str(e)}")
            return None
    
    def save_analytics_data(self, event_type: str, data: Dict) -> bool:
        """Save analytics events"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            file_path = os.path.join(self.analytics_dir, f"analytics_{today}.json")
            
            event_data = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'data': data
            }
            
            # Append to daily analytics file
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    analytics_data = json.load(f)
            else:
                analytics_data = {'events': []}
            
            analytics_data['events'].append(event_data)
            
            with open(file_path, 'w') as f:
                json.dump(analytics_data, f, indent=2)
            
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to save analytics: {str(e)}")
            return False
