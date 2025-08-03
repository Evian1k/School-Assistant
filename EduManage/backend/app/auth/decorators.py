from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from ..models.user import User
from ..models.student import Student
from ..models.guardian import Guardian
from ..models.teacher import Teacher

def role_required(*allowed_roles):
    """
    Decorator to restrict access based on user roles
    Usage: @role_required('admin', 'teacher')
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_data = get_jwt_identity()
            if not current_user_data or 'role' not in current_user_data:
                return jsonify({'msg': 'Invalid token'}), 401
            
            if current_user_data['role'] not in allowed_roles:
                return jsonify({'msg': 'Access forbidden: insufficient privileges'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Get current user from JWT token"""
    try:
        verify_jwt_in_request()
        current_user_data = get_jwt_identity()
        if current_user_data and 'id' in current_user_data:
            return User.query.get(current_user_data['id'])
        return None
    except:
        return None

def student_access_only():
    """Decorator to ensure only students can access their own data"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_data = get_jwt_identity()
            if not current_user_data:
                return jsonify({'msg': 'Invalid token'}), 401
            
            user_role = current_user_data.get('role')
            user_id = current_user_data.get('id')
            
            # Allow admin to access any student data
            if user_role == 'admin':
                return f(*args, **kwargs)
            
            # For students, ensure they only access their own data
            if user_role == 'student':
                student = Student.query.filter_by(user_id=user_id).first()
                if not student:
                    return jsonify({'msg': 'Student profile not found'}), 404
                
                # Add student_id to kwargs for route functions to use
                kwargs['current_student_id'] = student.id
                return f(*args, **kwargs)
            
            return jsonify({'msg': 'Access forbidden'}), 403
        return decorated_function
    return decorator

def guardian_access_only():
    """Decorator to ensure guardians can only access their children's data"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_data = get_jwt_identity()
            if not current_user_data:
                return jsonify({'msg': 'Invalid token'}), 401
            
            user_role = current_user_data.get('role')
            user_id = current_user_data.get('id')
            
            # Allow admin to access any data
            if user_role == 'admin':
                return f(*args, **kwargs)
            
            # For guardians, ensure they only access their children's data
            if user_role == 'parent':
                guardian = Guardian.query.filter_by(user_id=user_id).first()
                if not guardian:
                    return jsonify({'msg': 'Guardian profile not found'}), 404
                
                # Add guardian info to kwargs
                kwargs['current_guardian_id'] = guardian.id
                kwargs['accessible_student_ids'] = [child.id for child in guardian.children]
                return f(*args, **kwargs)
            
            return jsonify({'msg': 'Access forbidden'}), 403
        return decorated_function
    return decorator

def teacher_class_access():
    """Decorator to ensure teachers can only access students in their assigned classes"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_data = get_jwt_identity()
            if not current_user_data:
                return jsonify({'msg': 'Invalid token'}), 401
            
            user_role = current_user_data.get('role')
            user_id = current_user_data.get('id')
            
            # Allow admin to access any data
            if user_role == 'admin':
                return f(*args, **kwargs)
            
            # For teachers, ensure they only access students in their classes
            if user_role == 'teacher':
                teacher = Teacher.query.filter_by(user_id=user_id).first()
                if not teacher:
                    return jsonify({'msg': 'Teacher profile not found'}), 404
                
                # Add teacher info to kwargs
                kwargs['current_teacher_id'] = teacher.id
                kwargs['teacher_classes'] = teacher.classes_assigned
                return f(*args, **kwargs)
            
            return jsonify({'msg': 'Access forbidden'}), 403
        return decorated_function
    return decorator

def validate_student_access(student_id, current_user_data, **kwargs):
    """
    Validate if current user can access specific student data
    Returns True if access is allowed, False otherwise
    """
    user_role = current_user_data.get('role')
    user_id = current_user_data.get('id')
    
    # Admin can access all
    if user_role == 'admin':
        return True
    
    # Student can only access their own data
    if user_role == 'student':
        student = Student.query.filter_by(user_id=user_id).first()
        return student and student.id == student_id
    
    # Parent can only access their children's data
    if user_role == 'parent':
        guardian = Guardian.query.filter_by(user_id=user_id).first()
        if guardian:
            child_ids = [child.id for child in guardian.children]
            return student_id in child_ids
    
    # Teacher can access students in their classes
    if user_role == 'teacher':
        teacher = Teacher.query.filter_by(user_id=user_id).first()
        if teacher:
            student = Student.query.get(student_id)
            if student and teacher.classes_assigned:
                import json
                try:
                    assigned_classes = json.loads(teacher.classes_assigned)
                    return student.class_name in assigned_classes
                except:
                    return False
    
    return False