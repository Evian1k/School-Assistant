from flask import Blueprint, request, jsonify
from ..models.student import Student
from ..models.user import User
from ..models.guardian import Guardian
from .. import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..auth.decorators import role_required, validate_student_access

student_bp = Blueprint('students', __name__)

@student_bp.route('/', methods=['GET'])
@role_required('admin', 'teacher')
def get_students():
    """Get all students (admin/teacher only)"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        if user_role == 'admin':
            # Admin can see all students
            students = Student.query.filter_by(is_active=True).all()
        elif user_role == 'teacher':
            # Teacher can only see students in their assigned classes
            from ..models.teacher import Teacher
            teacher = Teacher.query.filter_by(user_id=current_user_data['id']).first()
            if not teacher or not teacher.classes_assigned:
                return jsonify([])
            
            import json
            try:
                assigned_classes = json.loads(teacher.classes_assigned)
                students = Student.query.filter(
                    Student.class_name.in_(assigned_classes),
                    Student.is_active == True
                ).all()
            except:
                students = []
        
        return jsonify([student.to_dict() for student in students])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving students: {str(e)}'}), 500

@student_bp.route('/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    """Get specific student data with role-based access control"""
    try:
        current_user_data = get_jwt_identity()
        
        # Validate access to this student
        if not validate_student_access(student_id, current_user_data):
            return jsonify({'msg': 'Access forbidden: cannot view this student data'}), 403
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'msg': 'Student not found'}), 404
        
        return jsonify(student.to_dict())
    except Exception as e:
        return jsonify({'msg': f'Error retrieving student: {str(e)}'}), 500

@student_bp.route('/', methods=['POST'])
@role_required('admin')
def add_student():
    """Add new student (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'class_name', 'grade_level', 'student_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'msg': f'Missing required field: {field}'}), 400
        
        # Check if email already exists
        if Student.query.filter_by(email=data['email']).first():
            return jsonify({'msg': 'Email already exists'}), 400
        
        # Check if student_id already exists
        if Student.query.filter_by(student_id=data['student_id']).first():
            return jsonify({'msg': 'Student ID already exists'}), 400
        
        # Create user account for student
        user = User(
            email=data['email'],
            name=data['name'],
            role='student',
            phone=data.get('phone', '')
        )
        user.set_password(data.get('password', 'student123'))  # Default password
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create student profile
        student = Student(
            user_id=user.id,
            student_id=data['student_id'],
            name=data['name'],
            email=data['email'],
            class_name=data['class_name'],
            grade_level=data['grade_level'],
            date_of_birth=data.get('date_of_birth'),
            guardian_id=data.get('guardian_id')
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'msg': 'Student added successfully',
            'student': student.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error adding student: {str(e)}'}), 500

@student_bp.route('/<int:student_id>', methods=['PATCH'])
@role_required('admin')
def update_student(student_id):
    """Update student information (admin only)"""
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'msg': 'Student not found'}), 404
        
        data = request.get_json()
        
        # Update student fields
        updatable_fields = ['name', 'email', 'class_name', 'grade_level', 'date_of_birth', 'guardian_id']
        for field in updatable_fields:
            if field in data:
                setattr(student, field, data[field])
        
        # Update associated user account
        if 'name' in data or 'email' in data:
            user = User.query.get(student.user_id)
            if user:
                if 'name' in data:
                    user.name = data['name']
                if 'email' in data:
                    user.email = data['email']
        
        db.session.commit()
        return jsonify({
            'msg': 'Student updated successfully',
            'student': student.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error updating student: {str(e)}'}), 500

@student_bp.route('/<int:student_id>', methods=['DELETE'])
@role_required('admin')
def delete_student(student_id):
    """Soft delete student (admin only)"""
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'msg': 'Student not found'}), 404
        
        # Soft delete - set is_active to False
        student.is_active = False
        
        # Also deactivate the user account
        user = User.query.get(student.user_id)
        if user:
            user.is_active = False
        
        db.session.commit()
        return jsonify({'msg': 'Student deactivated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error deleting student: {str(e)}'}), 500

@student_bp.route('/my-profile', methods=['GET'])
@jwt_required()
def get_my_profile():
    """Get current student's own profile"""
    try:
        current_user_data = get_jwt_identity()
        user_id = current_user_data.get('id')
        user_role = current_user_data.get('role')
        
        if user_role != 'student':
            return jsonify({'msg': 'Access forbidden: not a student account'}), 403
        
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'msg': 'Student profile not found'}), 404
        
        return jsonify(student.to_dict())
    except Exception as e:
        return jsonify({'msg': f'Error retrieving profile: {str(e)}'}), 500

@student_bp.route('/by-guardian/<int:guardian_id>', methods=['GET'])
@role_required('admin', 'parent')
def get_students_by_guardian(guardian_id):
    """Get students belonging to a specific guardian"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        # If parent, ensure they can only access their own children
        if user_role == 'parent':
            guardian = Guardian.query.filter_by(user_id=current_user_data['id']).first()
            if not guardian or guardian.id != guardian_id:
                return jsonify({'msg': 'Access forbidden: not your children'}), 403
        
        students = Student.query.filter_by(guardian_id=guardian_id, is_active=True).all()
        return jsonify([student.to_dict() for student in students])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving students: {str(e)}'}), 500
