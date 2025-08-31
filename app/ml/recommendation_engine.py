# app/ml/recommendation_engine.py
import numpy as np
from typing import Dict, List, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pickle
import os
from flask import current_app

class RecommendationEngine:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = None
        self.model_path = current_app.config.get('RECOMMENDATION_MODEL_PATH')
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.scaler = model_data['scaler']
            except Exception as e:
                current_app.logger.error(f"Failed to load model: {str(e)}")
                self._create_default_model()
        else:
            self._create_default_model()
    
    def _create_default_model(self):
        """Create a default clustering model"""
        # Generate synthetic training data for different location types
        synthetic_data = self._generate_synthetic_training_data()
        
        # Train clustering model
        features = np.array(synthetic_data)
        self.scaler.fit(features)
        scaled_features = self.scaler.transform(features)
        
        self.model = KMeans(n_clusters=5, random_state=42)
        self.model.fit(scaled_features)
        
        # Save model
        self._save_model()
    
    def _generate_synthetic_training_data(self) -> List[List[float]]:
        """Generate synthetic training data for different location scenarios"""
        # Features: [foot_traffic, competition_density, demographic_match, category_gaps_count]
        data = [
            # High-potential locations
            [90, 80, 85, 3], [85, 75, 90, 2], [88, 85, 80, 4],
            # Medium-potential locations  
            [60, 60, 65, 2], [55, 70, 60, 1], [65, 55, 70, 2],
            # Low-potential locations
            [30, 20, 40, 0], [25, 30, 35, 1], [35, 25, 30, 0],
            # High-competition areas
            [80, 30, 70, 1], [75, 25, 65, 0], [85, 20, 75, 2],
            # Tourist areas
            [95, 50, 60, 3], [90, 45, 55, 4], [85, 55, 65, 2]
        ]
        return data
    
    def predict_location_cluster(self, foot_traffic: float, competition_density: float,
                               demographic_match: float, category_gaps_count: int) -> Dict:
        """Predict which cluster/type a location belongs to"""
        if not self.model:
            return {'cluster': 0, 'confidence': 0.5}
        
        features = np.array([[foot_traffic, competition_density, demographic_match, category_gaps_count]])
        scaled_features = self.scaler.transform(features)
        
        cluster = self.model.predict(scaled_features)[0]
        
        # Calculate confidence based on distance to cluster center
        distances = self.model.transform(scaled_features)[0]
        min_distance = min(distances)
        confidence = max(0, 1 - (min_distance / np.max(distances)))
        
        cluster_descriptions = {
            0: "High-Potential Location",
            1: "Medium-Potential Location", 
            2: "Low-Potential Location",
            3: "High-Competition Area",
            4: "Tourist/Event Area"
        }
        
        return {
            'cluster': int(cluster),
            'cluster_description': cluster_descriptions.get(cluster, "Unknown"),
            'confidence': float(confidence)
        }
    
    def _save_model(self):
        """Save the trained model"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler
                }, f)
        except Exception as e:
            current_app.logger.error(f"Failed to save model: {str(e)}")
