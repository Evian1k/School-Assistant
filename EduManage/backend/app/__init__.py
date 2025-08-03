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
    
    # Enable CORS for frontend communication
    CORS(app, origins=['http://localhost:3000', 'http://localhost:5173'], supports_credentials=True)
    
    # Register blueprints
    from .routes.auth_routes import auth_bp
    from .routes.student_routes import student_bp
    from .routes.attendance_routes import attendance_bp
    from .routes.fee_routes import fee_bp
    from .routes.grade_routes import grade_bp
    from .routes.teacher_routes import teacher_bp
    from .routes.admin_routes import admin_bp
    from .routes.guardian_routes import guardian_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(student_bp, url_prefix='/api/v1/students')
    app.register_blueprint(attendance_bp, url_prefix='/api/v1/attendance')
    app.register_blueprint(fee_bp, url_prefix='/api/v1/fees')
    app.register_blueprint(grade_bp, url_prefix='/api/v1/grades')
    app.register_blueprint(teacher_bp, url_prefix='/api/v1/teachers')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(guardian_bp, url_prefix='/api/v1/guardians')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
