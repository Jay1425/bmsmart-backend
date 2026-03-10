"""
Routes package for BMSmart backend.
"""
from app.routes.auth_routes import auth_bp
from app.routes.building_routes import building_bp
from app.routes.user_routes import user_bp
from app.routes.visitor_routes import visitor_bp
from app.routes.visitor_form_routes import visitor_form_bp
from app.routes.payment_routes import payment_bp
from app.routes.complaint_routes import complaint_bp
from app.routes.analytics_routes import analytics_bp
from app.routes.security_routes import security_bp
from app.routes.notification_routes import notification_bp
from app.routes.ai_routes import ai_bp

__all__ = ['auth_bp', 'building_bp', 'user_bp', 'visitor_bp', 'visitor_form_bp', 'payment_bp', 'complaint_bp', 'analytics_bp', 'security_bp', 'notification_bp', 'ai_bp']
