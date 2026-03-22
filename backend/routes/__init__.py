# backend/routes/__init__.py
from backend.routes.auth import auth_bp
from backend.routes.tasks import tasks_bp
from backend.routes.expenses import expenses_bp
from backend.routes.events import events_bp
from backend.routes.children import children_bp
from backend.routes.notifications import notifications_bp
from backend.routes.settings import settings_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(expenses_bp, url_prefix='/api/expenses')
    app.register_blueprint(events_bp, url_prefix='/api/events')
    app.register_blueprint(children_bp, url_prefix='/api/children')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')