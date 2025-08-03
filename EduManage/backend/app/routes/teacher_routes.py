from flask import Blueprint, request, jsonify
from ..models.teacher import Teacher
from ..models.student import Student
from ..models.user import User
from .. import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..auth.decorators import role_required
import json

teacher_bp = Blueprint('teachers', __name__)

@teacher_bp.route('/', methods=['GET'])
@role_required('admin')
def get_teachers():
    """Get all teachers (admin only)"""
    try:
        teachers = Teacher.query.filter_by(is_active=True).all()
        return jsonify([teacher.to_dict() for teacher in teachers])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving teachers: {str(e)}'}), 500

@teacher_bp.route('/', methods=['POST'])
@role_required('admin')
def add_teacher():
    """Add new teacher (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'teacher_id', 'subjects', 'classes_assigned']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'msg': f'Missing required field: {field}'}), 400
        
        # Check if email already exists
        if Teacher.query.filter_by(email=data['email']).first():
            return jsonify({'msg': 'Email already exists'}), 400
        
        # Check if teacher_id already exists
        if Teacher.query.filter_by(teacher_id=data['teacher_id']).first():
            return jsonify({'msg': 'Teacher ID already exists'}), 400
        
        # Create user account for teacher
        user = User(
            email=data['email'],
            name=data['name'],
            role='teacher',
            phone=data['phone']
        )
        user.set_password(data.get('password', 'teacher123'))  # Default password
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create teacher profile
        teacher = Teacher(
            user_id=user.id,
            teacher_id=data['teacher_id'],
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            subjects=json.dumps(data['subjects']) if isinstance(data['subjects'], list) else data['subjects'],
            classes_assigned=json.dumps(data['classes_assigned']) if isinstance(data['classes_assigned'], list) else data['classes_assigned'],
            qualification=data.get('qualification', ''),
            experience_years=data.get('experience_years', 0)
        )
        
        db.session.add(teacher)
        db.session.commit()
        
        return jsonify({
            'msg': 'Teacher added successfully',
            'teacher': teacher.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error adding teacher: {str(e)}'}), 500

@teacher_bp.route('/<int:teacher_id>', methods=['GET'])
@role_required('admin', 'teacher')
def get_teacher(teacher_id):
    """Get specific teacher details"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({'msg': 'Teacher not found'}), 404
        
        # Teachers can only view their own profile
        if user_role == 'teacher':
            current_teacher = Teacher.query.filter_by(user_id=current_user_data['id']).first()
            if not current_teacher or current_teacher.id != teacher_id:
                return jsonify({'msg': 'Access forbidden: can only view own profile'}), 403
        
        return jsonify(teacher.to_dict())
    except Exception as e:
        return jsonify({'msg': f'Error retrieving teacher: {str(e)}'}), 500

@teacher_bp.route('/my-profile', methods=['GET'])
@jwt_required()
def get_my_profile():
    """Get current teacher's own profile"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        if user_role != 'teacher':
            return jsonify({'msg': 'Access forbidden: not a teacher account'}), 403
        
        teacher = Teacher.query.filter_by(user_id=current_user_data['id']).first()
        if not teacher:
            return jsonify({'msg': 'Teacher profile not found'}), 404
        
        return jsonify(teacher.to_dict())
    except Exception as e:
        return jsonify({'msg': f'Error retrieving profile: {str(e)}'}), 500

@teacher_bp.route('/my-classes', methods=['GET'])
@jwt_required()
def get_my_classes():
    """Get current teacher's assigned classes with student counts"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        if user_role != 'teacher':
            return jsonify({'msg': 'Access forbidden: not a teacher account'}), 403
        
        teacher = Teacher.query.filter_by(user_id=current_user_data['id']).first()
        if not teacher:
            return jsonify({'msg': 'Teacher profile not found'}), 404
        
        if not teacher.classes_assigned:
            return jsonify([])
        
        try:
            assigned_classes = json.loads(teacher.classes_assigned)
        except:
            return jsonify({'msg': 'Error parsing assigned classes'}), 500
        
        # Get student counts for each class
        class_details = []
        for class_name in assigned_classes:
            student_count = Student.query.filter_by(class_name=class_name, is_active=True).count()
            class_details.append({
                'class_name': class_name,
                'student_count': student_count
            })
        
        return jsonify(class_details)
    except Exception as e:
        return jsonify({'msg': f'Error retrieving classes: {str(e)}'}), 500

@teacher_bp.route('/my-students', methods=['GET'])
@jwt_required()
def get_my_students():
    """Get all students in teacher's assigned classes"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        if user_role != 'teacher':
            return jsonify({'msg': 'Access forbidden: not a teacher account'}), 403
        
        teacher = Teacher.query.filter_by(user_id=current_user_data['id']).first()
        if not teacher:
            return jsonify({'msg': 'Teacher profile not found'}), 404
        
        if not teacher.classes_assigned:
            return jsonify([])
        
        try:
            assigned_classes = json.loads(teacher.classes_assigned)
        except:
            return jsonify({'msg': 'Error parsing assigned classes'}), 500
        
        # Get all students in assigned classes
        students = Student.query.filter(
            Student.class_name.in_(assigned_classes),
            Student.is_active == True
        ).order_by(Student.class_name, Student.name).all()
        
        return jsonify([student.to_dict() for student in students])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving students: {str(e)}'}), 500

@teacher_bp.route('/class/<class_name>/students', methods=['GET'])
@jwt_required()
def get_class_students(class_name):
    """Get students in a specific class (teacher must be assigned to class)"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        # Admin can access any class
        if user_role == 'admin':
            students = Student.query.filter_by(class_name=class_name, is_active=True).all()
            return jsonify([student.to_dict() for student in students])
        
        if user_role != 'teacher':
            return jsonify({'msg': 'Access forbidden: not a teacher account'}), 403
        
        teacher = Teacher.query.filter_by(user_id=current_user_data['id']).first()
        if not teacher:
            return jsonify({'msg': 'Teacher profile not found'}), 404
        
        # Check if teacher is assigned to this class
        if teacher.classes_assigned:
            try:
                assigned_classes = json.loads(teacher.classes_assigned)
                if class_name not in assigned_classes:
                    return jsonify({'msg': 'Access forbidden: not assigned to this class'}), 403
            except:
                return jsonify({'msg': 'Error parsing assigned classes'}), 500
        else:
            return jsonify({'msg': 'No classes assigned to teacher'}), 403
        
        students = Student.query.filter_by(class_name=class_name, is_active=True).order_by(Student.name).all()
        return jsonify([student.to_dict() for student in students])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving class students: {str(e)}'}), 500

@teacher_bp.route('/<int:teacher_id>', methods=['PATCH'])
@role_required('admin')
def update_teacher(teacher_id):
    """Update teacher information (admin only)"""
    try:
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({'msg': 'Teacher not found'}), 404
        
        data = request.get_json()
        
        # Update teacher fields
        updatable_fields = ['name', 'email', 'phone', 'subjects', 'classes_assigned', 'qualification', 'experience_years']
        for field in updatable_fields:
            if field in data:
                if field in ['subjects', 'classes_assigned']:
                    # Convert list to JSON string
                    if isinstance(data[field], list):
                        setattr(teacher, field, json.dumps(data[field]))
                    else:
                        setattr(teacher, field, data[field])
                elif field == 'experience_years':
                    setattr(teacher, field, int(data[field]))
                else:
                    setattr(teacher, field, data[field])
        
        # Update associated user account
        if 'name' in data or 'email' in data or 'phone' in data:
            user = User.query.get(teacher.user_id)
            if user:
                if 'name' in data:
                    user.name = data['name']
                if 'email' in data:
                    user.email = data['email']
                if 'phone' in data:
                    user.phone = data['phone']
        
        db.session.commit()
        return jsonify({
            'msg': 'Teacher updated successfully',
            'teacher': teacher.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error updating teacher: {str(e)}'}), 500

@teacher_bp.route('/<int:teacher_id>', methods=['DELETE'])
@role_required('admin')
def delete_teacher(teacher_id):
    """Soft delete teacher (admin only)"""
    try:
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({'msg': 'Teacher not found'}), 404
        
        # Soft delete - set is_active to False
        teacher.is_active = False
        
        # Also deactivate the user account
        user = User.query.get(teacher.user_id)
        if user:
            user.is_active = False
        
        db.session.commit()
        return jsonify({'msg': 'Teacher deactivated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error deleting teacher: {str(e)}'}), 500

@teacher_bp.route('/my-subjects', methods=['GET'])
@jwt_required()
def get_my_subjects():
    """Get current teacher's assigned subjects"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        if user_role != 'teacher':
            return jsonify({'msg': 'Access forbidden: not a teacher account'}), 403
        
        teacher = Teacher.query.filter_by(user_id=current_user_data['id']).first()
        if not teacher:
            return jsonify({'msg': 'Teacher profile not found'}), 404
        
        if not teacher.subjects:
            return jsonify([])
        
        try:
            subjects = json.loads(teacher.subjects)
            return jsonify(subjects)
        except:
            return jsonify({'msg': 'Error parsing subjects'}), 500
    except Exception as e:
        return jsonify({'msg': f'Error retrieving subjects: {str(e)}'}), 500

@teacher_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics for current teacher"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        if user_role != 'teacher':
            return jsonify({'msg': 'Access forbidden: not a teacher account'}), 403
        
        teacher = Teacher.query.filter_by(user_id=current_user_data['id']).first()
        if not teacher:
            return jsonify({'msg': 'Teacher profile not found'}), 404
        
        stats = {
            'total_classes': 0,
            'total_students': 0,
            'total_subjects': 0
        }
        
        # Count classes
        if teacher.classes_assigned:
            try:
                assigned_classes = json.loads(teacher.classes_assigned)
                stats['total_classes'] = len(assigned_classes)
                
                # Count students in assigned classes
                stats['total_students'] = Student.query.filter(
                    Student.class_name.in_(assigned_classes),
                    Student.is_active == True
                ).count()
            except:
                pass
        
        # Count subjects
        if teacher.subjects:
            try:
                subjects = json.loads(teacher.subjects)
                stats['total_subjects'] = len(subjects)
            except:
                pass
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'msg': f'Error retrieving dashboard stats: {str(e)}'}), 500

@teacher_bp.route('/update-profile', methods=['PATCH'])
@jwt_required()
def update_my_profile():
    """Update current teacher's own profile"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        if user_role != 'teacher':
            return jsonify({'msg': 'Access forbidden: not a teacher account'}), 403
        
        teacher = Teacher.query.filter_by(user_id=current_user_data['id']).first()
        if not teacher:
            return jsonify({'msg': 'Teacher profile not found'}), 404
        
        data = request.get_json()
        
        # Teachers can only update certain fields
        updatable_fields = ['phone', 'qualification']
        for field in updatable_fields:
            if field in data:
                setattr(teacher, field, data[field])
        
        # Update user account phone if provided
        if 'phone' in data:
            user = User.query.get(teacher.user_id)
            if user:
                user.phone = data['phone']
        
        db.session.commit()
        return jsonify({
            'msg': 'Profile updated successfully',
            'teacher': teacher.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error updating profile: {str(e)}'}), 500