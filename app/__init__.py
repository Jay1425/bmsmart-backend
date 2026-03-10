"""
Flask application factory for BMSmart backend.
"""
from flask import Flask
from app.config import config
from app.extensions import db, cors, jwt


def create_app(config_name='default'):
    """
    Flask application factory.
    
    Args:
        config_name (str): Configuration name ('development', 'production', 'testing', 'default')
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration from config.py
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    cors.init_app(app, origins=app.config.get('CORS_ORIGINS', '*'))
    jwt.init_app(app)
    
    # Register blueprints
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
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(building_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(visitor_bp)
    app.register_blueprint(visitor_form_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(complaint_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(ai_bp)
    
    # Create database tables
    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        from app.models import Building, User, Visitor, Payment, Complaint, Notification
        db.create_all()
    
    # Initialize Firebase Cloud Messaging
    from app.services.notification_service import NotificationService
    firebase_credentials_path = app.config.get('FIREBASE_CREDENTIALS_PATH')
    NotificationService.initialize(firebase_credentials_path)
    
    return app
