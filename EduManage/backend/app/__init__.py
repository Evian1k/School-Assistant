from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .models import *

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)  # Enable CORS for frontend integration
    
    # Register blueprints
    from .routes.auth_routes import auth_bp
    from .routes.student_routes import student_bp
    from .routes.notification_routes import notification_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(student_bp, url_prefix='/api/v1/students')
    app.register_blueprint(notification_bp, url_prefix='/api/v1/notifications')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
