# app/models/recommendation.py
from app.models.location import Location  # Add this line
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class LocationInsight:
    location: Location
    foot_traffic_score: float
    competition_density: float
    demographic_match: float
    optimal_hours: List[str]
    category_gaps: List[str]
    nearby_attractions: List[str]
    risk_factors: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'location': self.location.to_dict(),
            'foot_traffic_score': self.foot_traffic_score,
            'competition_density': self.competition_density,
            'demographic_match': self.demographic_match,
            'optimal_hours': self.optimal_hours,
            'category_gaps': self.category_gaps,
            'nearby_attractions': self.nearby_attractions,
            'risk_factors': self.risk_factors
        }

@dataclass
class BusinessRecommendation:
    location: Location
    confidence_score: float
    insights: LocationInsight
    reasoning: str
    estimated_revenue_potential: str
    setup_requirements: List[str]
    recommended_duration: str
    
    def to_dict(self) -> Dict:
        return {
            'location': self.location.to_dict(),
            'confidence_score': self.confidence_score,
            'insights': self.insights.to_dict(),
            'reasoning': self.reasoning,
            'estimated_revenue_potential': self.estimated_revenue_potential,
            'setup_requirements': self.setup_requirements,
            'recommended_duration': self.recommended_duration,
            'generated_at': datetime.now().isoformat()
        }