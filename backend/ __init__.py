import logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from backend.config import Config
from backend.models import db
from backend.routes import register_blueprints
from backend.events.sse import sse_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Initialize extensions
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app, supports_credentials=True)
    JWTManager(app)
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    
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
    
    logger.info("Application initialized successfully")
    
    return app