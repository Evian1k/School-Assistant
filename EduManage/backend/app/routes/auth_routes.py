from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models.user import User
from ..models.student import Student
from ..models.guardian import Guardian
from ..models.teacher import Teacher
from .. import db
from datetime import datetime, timedelta
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        email = data.get('email').lower().strip()
        password = data.get('password')
        name = data.get('name').strip()
        role = data.get('role').lower()
        phone = data.get('phone', '').strip()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, password_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': password_msg}), 400
        
        # Validate role
        valid_roles = ['admin', 'teacher', 'student', 'guardian']
        if role not in valid_roles:
            return jsonify({'error': 'Invalid role. Must be one of: admin, teacher, student, guardian'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Create user
        user = User(
            email=email,
            name=name,
            role=role,
            phone=phone
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create role-specific profile
        if role == 'student':
            student = Student(
                user_id=user.id,
                name=name,
                email=email,
                student_id=f"STU{user.id:06d}",
                class_name=data.get('class_name'),
                section=data.get('section'),
                guardian_id=data.get('guardian_id')
            )
            db.session.add(student)
        
        elif role == 'guardian':
            guardian = Guardian(
                user_id=user.id,
                name=name,
                email=email,
                phone=phone,
                relationship=data.get('relationship', 'Parent'),
                occupation=data.get('occupation'),
                address=data.get('address')
            )
            db.session.add(guardian)
        
        elif role == 'teacher':
            teacher = Teacher(
                user_id=user.id,
                name=name,
                email=email,
                phone=phone,
                employee_id=f"TCH{user.id:06d}",
                subjects=data.get('subjects', ''),
                qualification=data.get('qualification'),
                experience_years=data.get('experience_years', 0)
            )
            db.session.add(teacher)
        
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create access token with user info
        access_token = create_access_token(
            identity={
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'name': user.name
            },
            expires_delta=timedelta(hours=24)
        )
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict(),
            'expires_in': 24 * 60 * 60  # 24 hours in seconds
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user = get_jwt_identity()
        user = User.query.get(current_user['id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile_data = user.to_dict()
        
        # Add role-specific data
        if user.role == 'student' and user.student_profile:
            profile_data['student_data'] = user.student_profile.to_dict()
        elif user.role == 'guardian' and user.guardian_profile:
            profile_data['guardian_data'] = user.guardian_profile.to_dict()
        elif user.role == 'teacher' and user.teacher_profile:
            profile_data['teacher_data'] = user.teacher_profile.to_dict()
        
        return jsonify(profile_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user = get_jwt_identity()
        user = User.query.get(current_user['id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update basic user info
        if data.get('name'):
            user.name = data['name'].strip()
        if data.get('phone'):
            user.phone = data['phone'].strip()
        
        # Update role-specific profile
        if user.role == 'student' and user.student_profile:
            student = user.student_profile
            if data.get('class_name'):
                student.class_name = data['class_name']
            if data.get('section'):
                student.section = data['section']
            if data.get('address'):
                student.address = data['address']
        
        elif user.role == 'guardian' and user.guardian_profile:
            guardian = user.guardian_profile
            if data.get('relationship'):
                guardian.relationship = data['relationship']
            if data.get('occupation'):
                guardian.occupation = data['occupation']
            if data.get('address'):
                guardian.address = data['address']
        
        elif user.role == 'teacher' and user.teacher_profile:
            teacher = user.teacher_profile
            if data.get('subjects'):
                teacher.subjects = data['subjects']
            if data.get('qualification'):
                teacher.qualification = data['qualification']
            if data.get('experience_years'):
                teacher.experience_years = data['experience_years']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        current_user = get_jwt_identity()
        user = User.query.get(current_user['id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        is_valid, password_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': password_msg}), 400
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
