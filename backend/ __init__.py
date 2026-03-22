from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from backend.config import Config
from backend.models import db
from backend.routes import register_blueprints
from backend.events.sse import sse_bp
import os

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app, supports_credentials=True)
    jwt = JWTManager(app)
    
    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Create tables if not exist (for development only)
    with app.app_context():
        from backend.models import User, Family, Task, Expense, Event, Child, Notification
        db.create_all()
    
    # Register blueprints
    register_blueprints(app)
    
    # Register SSE blueprint
    app.register_blueprint(sse_bp, url_prefix='/api/events')
    
    # Serve frontend
    @app.route('/')
    def serve_index():
        return app.send_static_file('index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        return app.send_static_file(path)
    
    return app