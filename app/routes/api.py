# app/routes/api.py
from flask import Blueprint, request, jsonify, current_app
from app.services.ai_service import AIService
from app.services.foursquare_service import FoursquareService
from app.utils.validators import Validators
import time

api = Blueprint('api', __name__)

@api.route('/analyze', methods=['POST'])
def analyze_location():
    """API endpoint to analyze a location"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        location = data.get('location')
        business_type = data.get('business_type')
        target_demographics = data.get('target_demographics', [])
        
        # Validate inputs
        if not location or not business_type:
            return jsonify({'error': 'Location and business_type are required'}), 400
        
        if not Validators.validate_business_type(business_type):
            return jsonify({'error': 'Invalid business type'}), 400
        
        # Sanitize inputs
        location = Validators.sanitize_input(location)
        business_type = Validators.sanitize_input(business_type)
        
        # Perform analysis
        ai_service = AIService()
        result = ai_service.analyze_location(location, business_type, target_demographics)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Analysis API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/search', methods=['POST'])
def search_places():
    """API endpoint to search places"""
    try:
        data = request.get_json()
        
        query = data.get('query', '')
        location = data.get('location')
        radius = data.get('radius', 1000)
        
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        if not Validators.validate_radius(radius):
            return jsonify({'error': 'Invalid radius (100-10000m)'}), 400
        
        foursquare_service = FoursquareService()
        result = foursquare_service.search_places(query, location, radius)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Search API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/place/<place_id>', methods=['GET'])
def get_place_details(place_id):
    """API endpoint to get place details"""
    try:
        foursquare_service = FoursquareService()
        result = foursquare_service.get_place_details(place_id)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Place details API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'app_name': current_app.config['APP_NAME'],
        'version': current_app.config['APP_VERSION']
    })

@api.route('/analytics', methods=['POST'])
def save_analytics():
    """Save analytics event"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        event_type = data.get('event_type')
        event_data = data.get('data', {})
        
        from app.utils.file_manager import FileManager
        file_manager = FileManager()
        
        success = file_manager.save_analytics_data(event_type, event_data)
        
        if success:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'error': 'Failed to save analytics'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Analytics API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/analysis/<analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """Get saved analysis by ID"""
    try:
        from app.utils.file_manager import FileManager
        file_manager = FileManager()
        
        analysis = file_manager.get_user_analysis(analysis_id)
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        return jsonify(analysis)
        
    except Exception as e:
        current_app.logger.error(f"Get analysis API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500