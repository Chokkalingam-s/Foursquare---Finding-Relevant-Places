# app/routes/main.py
from flask import Blueprint, render_template, request, jsonify
from app.services.ai_service import AIService
from app.utils.validators import Validators

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@main.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')

@main.route('/analysis')
def analysis():
    """Analysis page"""
    return render_template('analysis.html')

@main.route('/recommendations')
def recommendations():
    """Recommendations page"""
    return render_template('recommendations.html')