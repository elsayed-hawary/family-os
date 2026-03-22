import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in environment")
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY must be set in environment")
    
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=90)
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        # Use absolute path for SQLite
        base_dir = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(base_dir, "../instance/family.db")}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }