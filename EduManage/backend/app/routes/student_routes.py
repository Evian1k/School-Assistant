from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.student import Student
from ..models.grade import Grade
from ..models.attendance import Attendance
from ..models.fee import Fee
from ..models.document import Document
from ..models.user import User
from ..models.guardian import Guardian
from .. import db
from datetime import datetime, date
from sqlalchemy import and_, or_

student_bp = Blueprint('students', __name__)

def get_current_user_role():
    current_user = get_jwt_identity()
    return current_user.get('role')

def get_current_user_id():
    current_user = get_jwt_identity()
    return current_user.get('id')

def can_access_student(student_id, user_role, user_id):
    """Check if user can access student data based on role"""
    if user_role == 'admin':
        return True
    elif user_role == 'teacher':
        # Teachers can access students in their classes
        return True  # Simplified for now
    elif user_role == 'student':
        # Students can only access their own data
        student = Student.query.filter_by(user_id=user_id).first()
        return student and student.id == student_id
    elif user_role == 'guardian':
        # Guardians can access their children's data
        guardian = Guardian.query.filter_by(user_id=user_id).first()
        if guardian:
            return guardian.students.filter_by(id=student_id).first() is not None
    return False

@student_bp.route('/', methods=['GET'])
@jwt_required()
def get_students():
    try:
        user_role = get_current_user_role()
        user_id = get_current_user_id()
        
        if user_role == 'admin':
            # Admin can see all students
            students = Student.query.filter_by(is_active=True).all()
        elif user_role == 'teacher':
            # Teachers can see students in their classes
            students = Student.query.filter_by(is_active=True).all()
        elif user_role == 'guardian':
            # Guardians can only see their children
            guardian = Guardian.query.filter_by(user_id=user_id).first()
            if guardian:
                students = guardian.students.filter_by(is_active=True).all()
            else:
                students = []
        elif user_role == 'student':
            # Students can only see themselves
            student = Student.query.filter_by(user_id=user_id, is_active=True).first()
            students = [student] if student else []
        else:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify([student.to_dict() for student in students])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    try:
        user_role = get_current_user_role()
        user_id = get_current_user_id()
        
        if not can_access_student(student_id, user_role, user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        return jsonify(student.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/', methods=['POST'])
@jwt_required()
def add_student():
    try:
        user_role = get_current_user_role()
        if user_role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'class_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if student with email already exists
        if Student.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Student with this email already exists'}), 400
        
        # Create user account for student
        user = User(
            email=data['email'],
            name=data['name'],
            role='student',
            phone=data.get('phone', '')
        )
        user.set_password('Student123!')  # Default password
        db.session.add(user)
        db.session.flush()
        
        # Create student profile
        student = Student(
            user_id=user.id,
            name=data['name'],
            email=data['email'],
            student_id=f"STU{user.id:06d}",
            class_name=data['class_name'],
            section=data.get('section'),
            guardian_id=data.get('guardian_id'),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            gender=data.get('gender'),
            address=data.get('address'),
            emergency_contact=data.get('emergency_contact'),
            blood_group=data.get('blood_group')
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'message': 'Student added successfully',
            'student': student.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    try:
        user_role = get_current_user_role()
        user_id = get_current_user_id()
        
        if user_role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if data.get('name'):
            student.name = data['name']
        if data.get('class_name'):
            student.class_name = data['class_name']
        if data.get('section'):
            student.section = data['section']
        if data.get('guardian_id'):
            student.guardian_id = data['guardian_id']
        if data.get('date_of_birth'):
            student.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        if data.get('gender'):
            student.gender = data['gender']
        if data.get('address'):
            student.address = data['address']
        if data.get('emergency_contact'):
            student.emergency_contact = data['emergency_contact']
        if data.get('blood_group'):
            student.blood_group = data['blood_group']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Student updated successfully',
            'student': student.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    try:
        user_role = get_current_user_role()
        if user_role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Soft delete - mark as inactive
        student.is_active = False
        if student.user:
            student.user.is_active = False
        
        db.session.commit()
        
        return jsonify({'message': 'Student deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Grades routes
@student_bp.route('/<int:student_id>/grades', methods=['GET'])
@jwt_required()
def get_student_grades(student_id):
    try:
        user_role = get_current_user_role()
        user_id = get_current_user_id()
        
        if not can_access_student(student_id, user_role, user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        grades = Grade.query.filter_by(student_id=student_id).all()
        return jsonify([grade.to_dict() for grade in grades])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>/grades', methods=['POST'])
@jwt_required()
def add_student_grade(student_id):
    try:
        user_role = get_current_user_role()
        if user_role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['subject', 'score', 'term', 'academic_year']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        grade = Grade(
            student_id=student_id,
            teacher_id=user_id,
            subject=data['subject'],
            score=data['score'],
            max_score=data.get('max_score', 100.0),
            term=data['term'],
            academic_year=data['academic_year'],
            exam_type=data.get('exam_type'),
            remarks=data.get('remarks')
        )
        
        db.session.add(grade)
        db.session.commit()
        
        return jsonify({
            'message': 'Grade added successfully',
            'grade': grade.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Attendance routes
@student_bp.route('/<int:student_id>/attendance', methods=['GET'])
@jwt_required()
def get_student_attendance(student_id):
    try:
        user_role = get_current_user_role()
        user_id = get_current_user_id()
        
        if not can_access_student(student_id, user_role, user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Attendance.query.filter_by(student_id=student_id)
        
        if start_date:
            query = query.filter(Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        attendance_records = query.order_by(Attendance.date.desc()).all()
        return jsonify([record.to_dict() for record in attendance_records])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>/attendance', methods=['POST'])
@jwt_required()
def mark_attendance(student_id):
    try:
        user_role = get_current_user_role()
        if user_role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['date', 'status']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if attendance already exists for this date
        existing_attendance = Attendance.query.filter_by(
            student_id=student_id,
            date=datetime.strptime(data['date'], '%Y-%m-%d').date()
        ).first()
        
        if existing_attendance:
            return jsonify({'error': 'Attendance already marked for this date'}), 400
        
        attendance = Attendance(
            student_id=student_id,
            teacher_id=user_id,
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            status=data['status'],
            time_in=datetime.strptime(data['time_in'], '%H:%M').time() if data.get('time_in') else None,
            time_out=datetime.strptime(data['time_out'], '%H:%M').time() if data.get('time_out') else None,
            remarks=data.get('remarks')
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'message': 'Attendance marked successfully',
            'attendance': attendance.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Fees routes
@student_bp.route('/<int:student_id>/fees', methods=['GET'])
@jwt_required()
def get_student_fees(student_id):
    try:
        user_role = get_current_user_role()
        user_id = get_current_user_id()
        
        if not can_access_student(student_id, user_role, user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        fees = Fee.query.filter_by(student_id=student_id).order_by(Fee.due_date.desc()).all()
        return jsonify([fee.to_dict() for fee in fees])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>/fees', methods=['POST'])
@jwt_required()
def add_student_fee(student_id):
    try:
        user_role = get_current_user_role()
        if user_role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['fee_type', 'amount', 'due_date', 'academic_year']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        fee = Fee(
            student_id=student_id,
            fee_type=data['fee_type'],
            amount=data['amount'],
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
            academic_year=data['academic_year'],
            term=data.get('term'),
            remarks=data.get('remarks')
        )
        
        db.session.add(fee)
        db.session.commit()
        
        return jsonify({
            'message': 'Fee added successfully',
            'fee': fee.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Documents routes
@student_bp.route('/<int:student_id>/documents', methods=['GET'])
@jwt_required()
def get_student_documents(student_id):
    try:
        user_role = get_current_user_role()
        user_id = get_current_user_id()
        
        if not can_access_student(student_id, user_role, user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        documents = Document.query.filter_by(student_id=student_id).order_by(Document.created_at.desc()).all()
        return jsonify([doc.to_dict() for doc in documents])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dashboard statistics
@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    try:
        user_role = get_current_user_role()
        user_id = get_current_user_id()
        
        if user_role == 'admin':
            # Admin dashboard - all students
            total_students = Student.query.filter_by(is_active=True).count()
            total_guardians = Guardian.query.filter_by(is_active=True).count()
            total_teachers = Teacher.query.filter_by(is_active=True).count()
            
            # Recent activities
            recent_students = Student.query.filter_by(is_active=True).order_by(Student.created_at.desc()).limit(5).all()
            
            stats = {
                'total_students': total_students,
                'total_guardians': total_guardians,
                'total_teachers': total_teachers,
                'recent_students': [student.to_dict() for student in recent_students]
            }
            
        elif user_role == 'guardian':
            # Guardian dashboard - their children
            guardian = Guardian.query.filter_by(user_id=user_id).first()
            if guardian:
                children = guardian.students.filter_by(is_active=True).all()
                stats = {
                    'children_count': len(children),
                    'children': [child.to_dict() for child in children]
                }
            else:
                stats = {'children_count': 0, 'children': []}
                
        elif user_role == 'student':
            # Student dashboard - personal info
            student = Student.query.filter_by(user_id=user_id, is_active=True).first()
            if student:
                grades = Grade.query.filter_by(student_id=student.id).all()
                attendance = Attendance.query.filter_by(student_id=student.id).all()
                fees = Fee.query.filter_by(student_id=student.id).all()
                
                stats = {
                    'student': student.to_dict(),
                    'grades_count': len(grades),
                    'attendance_count': len(attendance),
                    'pending_fees': len([f for f in fees if f.status == 'pending']),
                    'recent_grades': [grade.to_dict() for grade in grades[-5:]]
                }
            else:
                stats = {}
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
