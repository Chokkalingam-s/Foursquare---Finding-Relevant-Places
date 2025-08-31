import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FOURSQUARE_API_KEY = os.environ.get('FOURSQUARE_API_KEY')
    
    # Application Settings
    APP_NAME = os.environ.get('APP_NAME', 'Choks')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    
    # Data Storage
    DATA_DIR = os.environ.get('DATA_DIR', 'app/data')
    CACHE_DIR = os.path.join(DATA_DIR, 'cache')
    USER_DATA_DIR = os.path.join(DATA_DIR, 'user_data')
    ML_MODELS_DIR = os.path.join(DATA_DIR, 'ml_models')
    ANALYTICS_DIR = os.path.join(DATA_DIR, 'analytics')
    
    # Cache Settings
    CACHE_EXPIRY = int(os.environ.get('CACHE_EXPIRY', 3600))  # 1 hour
    
    # API Settings
    FOURSQUARE_BASE_URL = 'https://api.foursquare.com/v3'
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # ML Settings
    SENTIMENT_MODEL_PATH = os.path.join(ML_MODELS_DIR, 'sentiment_model.pkl')
    RECOMMENDATION_MODEL_PATH = os.path.join(ML_MODELS_DIR, 'recommendation_model.pkl')
    
    @staticmethod
    def init_app(app):
        # Create necessary directories
        directories = [
            Config.DATA_DIR,
            Config.CACHE_DIR,
            Config.USER_DATA_DIR,
            Config.ML_MODELS_DIR,
            Config.ANALYTICS_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
        # Create .gitkeep files
        for directory in [Config.CACHE_DIR, Config.USER_DATA_DIR]:
            gitkeep_path = os.path.join(directory, '.gitkeep')
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, 'w') as f:
                    f.write('')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
