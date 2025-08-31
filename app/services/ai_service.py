# app/services/ai_service.py
import json
import numpy as np
import time
from typing import Dict, List, Tuple, Optional
from flask import current_app
from app.models.location import Location, Business
from app.models.recommendation import BusinessRecommendation, LocationInsight
from app.services.foursquare_service import FoursquareService
from app.ml.sentiment_analyzer import SentimentAnalyzer
from app.ml.recommendation_engine import RecommendationEngine
from app.utils.data_processor import DataProcessor
from app.utils.file_manager import FileManager

class AIService:
    def __init__(self):
        self.foursquare_service = FoursquareService()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.recommendation_engine = RecommendationEngine()
        self.data_processor = DataProcessor()
        self.file_manager = FileManager()
    
    def analyze_location(self, location: str, business_type: str, 
                        target_demographics: List[str] = None) -> Dict:
        """Main function to analyze a location for business potential"""
        try:
            # Extract coordinates or search for location
            coords = self.data_processor.extract_location_coordinates(location)
            if not coords:
                # Search for location using Foursquare
                search_result = self.foursquare_service.search_places("", location, limit=1)
                if search_result.get('results'):
                    first_result = search_result['results'][0]
                    geocodes = first_result.get('geocodes', {}).get('main', {})
                    coords = (geocodes.get('latitude'), geocodes.get('longitude'))
            
            if not coords:
                return {'error': 'Could not determine location coordinates'}
            
            # Get comprehensive area data
            area_data = self._get_comprehensive_area_data(coords, business_type)
            
            # Generate insights
            insights = self._generate_location_insights(coords, area_data, business_type, target_demographics)
            
            # Create recommendation
            recommendation = self._create_business_recommendation(coords, insights, business_type)
            
            # Save analysis
            analysis_id = f"analysis_{int(time.time())}"
            analysis_data = {
                'location': location,
                'coordinates': coords,
                'business_type': business_type,
                'target_demographics': target_demographics,
                'recommendation': recommendation.to_dict(),
                'raw_data': area_data
            }
            
            self.file_manager.save_user_analysis(analysis_id, analysis_data)
            
            # Log analytics
            self.file_manager.save_analytics_data('location_analysis', {
                'business_type': business_type,
                'location': location,
                'success': True
            })
            
            return {
                'analysis_id': analysis_id,
                'recommendation': recommendation.to_dict(),
                'success': True
            }
            
        except Exception as e:
            current_app.logger.error(f"Analysis error: {str(e)}")
            return {'error': f'Analysis failed: {str(e)}'}
    
    def _get_comprehensive_area_data(self, coords: Tuple[float, float], 
                                   business_type: str) -> Dict:
        """Gather comprehensive data about the area"""
        lat, lng = coords
        
        # Get nearby businesses
        nearby_data = self.foursquare_service.search_nearby_categories(lat, lng, radius=1000)
        businesses = nearby_data.get('results', [])
        
        # Get specific competitor data
        competitor_query = self._get_competitor_query(business_type)
        competitor_data = self.foursquare_service.search_places(
            competitor_query, f"{lat},{lng}", radius=1000, limit=30
        )
        competitors = competitor_data.get('results', [])
        
        # Get area attractions and amenities
        attraction_data = self.foursquare_service.search_places(
            "popular attractions restaurants", f"{lat},{lng}", radius=1000, limit=20
        )
        attractions = attraction_data.get('results', [])
        
        return {
            'all_businesses': businesses,
            'competitors': competitors,
            'attractions': attractions,
            'total_venues': len(businesses)
        }
    
    def _get_competitor_query(self, business_type: str) -> str:
        """Get search query for competitors based on business type"""
        queries = {
            'food_truck': 'food truck restaurant fast food',
            'retail': 'shop store boutique retail',
            'service': 'salon service repair',
            'entertainment': 'entertainment music art event'
        }
        return queries.get(business_type, 'business')
    
    def _generate_location_insights(self, coords: Tuple[float, float], 
                                  area_data: Dict, business_type: str,
                                  target_demographics: List[str]) -> LocationInsight:
        """Generate comprehensive location insights"""
        lat, lng = coords
        businesses = area_data['all_businesses']
        competitors = area_data['competitors']
        attractions = area_data['attractions']
        
        # Calculate metrics
        foot_traffic_score = self.data_processor.calculate_foot_traffic_score(businesses, coords)
        competition_analysis = self.data_processor.analyze_competition_density(coords, competitors, business_type)
        demographic_analysis = self.data_processor.analyze_demographic_patterns(businesses)
        category_gaps = self.data_processor.identify_category_gaps(businesses, business_type)
        
        # Calculate demographic match
        demographic_match = self._calculate_demographic_match(demographic_analysis, target_demographics or [])
        
        # Generate optimal hours prediction
        optimal_hours = self._predict_optimal_hours(businesses, business_type)
        
        # Identify nearby attractions
        nearby_attractions = [attr.get('name', '') for attr in attractions[:5]]
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(competition_analysis, demographic_analysis, foot_traffic_score)
        
        location = Location(lat, lng, f"{lat}, {lng}", "Unknown", "Unknown", "Unknown")
        
        return LocationInsight(
            location=location,
            foot_traffic_score=foot_traffic_score,
            competition_density=competition_analysis['density_score'],
            demographic_match=demographic_match,
            optimal_hours=optimal_hours,
            category_gaps=category_gaps,
            nearby_attractions=nearby_attractions,
            risk_factors=risk_factors
        )
    
    def _calculate_demographic_match(self, demographic_analysis: Dict, 
                                   target_demographics: List[str]) -> float:
        """Calculate how well the area matches target demographics"""
        if not target_demographics:
            return 70.0  # Default neutral score
        
        score = 0
        total_weight = 0
        
        for demographic in target_demographics:
            weight = 25
            if demographic.lower() in ['families', 'family']:
                score += demographic_analysis.get('family_friendly', 0) * weight
            elif demographic.lower() in ['professionals', 'young_professional']:
                score += demographic_analysis.get('young_professional', 0) * weight
            elif demographic.lower() in ['tourists', 'tourist']:
                score += demographic_analysis.get('tourist_area', 0) * weight
            else:
                score += 50 * weight  # Default score
            
            total_weight += weight
        
        return min(100, score / total_weight if total_weight > 0 else 50)
    
    def _predict_optimal_hours(self, businesses: List[Dict], business_type: str) -> List[str]:
        """Predict optimal operating hours based on area patterns"""
        # Analyze operating hours of similar businesses
        similar_businesses = [b for b in businesses if self.data_processor._is_competitor(b, business_type)]
        
        if business_type == 'food_truck':
            return ['11:00-14:00', '17:00-21:00']  # Lunch and dinner
        elif business_type == 'retail':
            return ['09:00-18:00']  # Standard retail hours
        elif business_type == 'service':
            return ['09:00-17:00']  # Business hours
        elif business_type == 'entertainment':
            return ['18:00-23:00']  # Evening hours
        
        return ['09:00-17:00']  # Default
    
    def _identify_risk_factors(self, competition_analysis: Dict, 
                             demographic_analysis: Dict, foot_traffic_score: float) -> List[str]:
        """Identify potential risk factors for the location"""
        risks = []
        
        if competition_analysis['total_competitors'] > 5:
            risks.append("High competition density")
        
        if foot_traffic_score < 30:
            risks.append("Low foot traffic area")
        
        if competition_analysis['average_competitor_rating'] > 4.5:
            risks.append("High-quality established competitors")
        
        if demographic_analysis['affluence_indicator'] < 2:
            risks.append("Lower-income area may affect pricing")
        
        return risks
    
    def _create_business_recommendation(self, coords: Tuple[float, float], 
                                     insights: LocationInsight, 
                                     business_type: str) -> BusinessRecommendation:
        """Create final business recommendation"""
        # Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(insights)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(insights, business_type)
        
        # Estimate revenue potential
        revenue_potential = self._estimate_revenue_potential(insights, business_type)
        
        # Generate setup requirements
        setup_requirements = self._generate_setup_requirements(insights, business_type)
        
        # Recommend duration
        recommended_duration = self._recommend_duration(confidence_score, insights)
        
        return BusinessRecommendation(
            location=insights.location,
            confidence_score=confidence_score,
            insights=insights,
            reasoning=reasoning,
            estimated_revenue_potential=revenue_potential,
            setup_requirements=setup_requirements,
            recommended_duration=recommended_duration
        )
    
    def _calculate_confidence_score(self, insights: LocationInsight) -> float:
        """Calculate overall confidence score"""
        weights = {
            'foot_traffic': 0.3,
            'competition': 0.25,
            'demographic': 0.25,
            'category_gaps': 0.2
        }
        
        score = (
            insights.foot_traffic_score * weights['foot_traffic'] +
            insights.competition_density * weights['competition'] +
            insights.demographic_match * weights['demographic'] +
            (len(insights.category_gaps) * 10) * weights['category_gaps']
        )
        
        return min(100, max(0, score))
    
    def _generate_reasoning(self, insights: LocationInsight, business_type: str) -> str:
        """Generate human-readable reasoning for the recommendation"""
        reasons = []
        
        if insights.foot_traffic_score > 70:
            reasons.append("High foot traffic from nearby popular venues")
        elif insights.foot_traffic_score < 30:
            reasons.append("Low foot traffic may require strong marketing")
        
        if insights.competition_density > 70:
            reasons.append("Low competition provides market opportunity")
        elif insights.competition_density < 30:
            reasons.append("High competition requires strong differentiation")
        
        if insights.category_gaps:
            reasons.append(f"Market gaps identified: {', '.join(insights.category_gaps[:3])}")
        
        if insights.nearby_attractions:
            reasons.append(f"Benefit from proximity to: {', '.join(insights.nearby_attractions[:2])}")
        
        return ". ".join(reasons) if reasons else "Standard market conditions observed"
    
    def _estimate_revenue_potential(self, insights: LocationInsight, business_type: str) -> str:
        """Estimate revenue potential category"""
        confidence = self._calculate_confidence_score(insights)
        
        if confidence > 80:
            return "High ($2000-5000/week)"
        elif confidence > 60:
            return "Medium-High ($1000-2000/week)"
        elif confidence > 40:
            return "Medium ($500-1000/week)"
        else:
            return "Low-Medium ($200-500/week)"
    
    def _generate_setup_requirements(self, insights: LocationInsight, business_type: str) -> List[str]:
        """Generate setup requirements based on analysis"""
        requirements = []
        
        if business_type == 'food_truck':
            requirements.extend([
                "Food service permits and licenses",
                "Mobile kitchen equipment",
                "Generator or power source"
            ])
        
        if insights.competition_density < 50:
            requirements.append("Strong branding to stand out from competition")
        
        if insights.foot_traffic_score < 50:
            requirements.append("Marketing strategy for customer acquisition")
        
        if len(insights.risk_factors) > 2:
            requirements.append("Risk mitigation strategy")
        
        return requirements
    
    def _recommend_duration(self, confidence_score: float, insights: LocationInsight) -> str:
        """Recommend operating duration"""
        if confidence_score > 70:
            return "2-4 weeks for market validation, potential for longer"
        elif confidence_score > 50:
            return "1-2 weeks with careful monitoring"
        else:
            return "3-5 days trial period recommended"