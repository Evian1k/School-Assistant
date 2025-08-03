from flask import Blueprint, request, jsonify
from ..models.guardian import Guardian
from ..models.student import Student
from ..models.user import User
from ..models.attendance import Attendance
from ..models.grade import Grade
from ..models.fee import Fee
from .. import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..auth.decorators import role_required
from datetime import datetime, date

guardian_bp = Blueprint('guardians', __name__)

@guardian_bp.route('/', methods=['GET'])
@role_required('admin')
def get_guardians():
    """Get all guardians (admin only)"""
    try:
        guardians = Guardian.query.filter_by(is_active=True).all()
        return jsonify([guardian.to_dict() for guardian in guardians])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving guardians: {str(e)}'}), 500

@guardian_bp.route('/', methods=['POST'])
@role_required('admin')
def add_guardian():
    """Add new guardian (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'relationship']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'msg': f'Missing required field: {field}'}), 400
        
        # Check if email already exists
        if Guardian.query.filter_by(email=data['email']).first():
            return jsonify({'msg': 'Email already exists'}), 400
        
        # Create user account for guardian
        user = User(
            email=data['email'],
            name=data['name'],
            role='parent',
            phone=data['phone']
        )
        user.set_password(data.get('password', 'parent123'))  # Default password
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create guardian profile
        guardian = Guardian(
            user_id=user.id,
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            address=data.get('address', ''),
            relationship=data['relationship'],
            occupation=data.get('occupation', ''),
            emergency_contact=data.get('emergency_contact', '')
        )
        
        db.session.add(guardian)
        db.session.commit()
        
        return jsonify({
            'msg': 'Guardian added successfully',
            'guardian': guardian.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error adding guardian: {str(e)}'}), 500

@guardian_bp.route('/my-profile', methods=['GET'])
@jwt_required()
def get_my_profile():
    """Get current guardian's own profile"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        if user_role != 'parent':
            return jsonify({'msg': 'Access forbidden: not a parent account'}), 403
        
        guardian = Guardian.query.filter_by(user_id=current_user_data['id']).first()
        if not guardian:
            return jsonify({'msg': 'Guardian profile not found'}), 404
        
        return jsonify(guardian.to_dict())
    except Exception as e:
        return jsonify({'msg': f'Error retrieving profile: {str(e)}'}), 500

@guardian_bp.route('/my-children', methods=['GET'])
@jwt_required()
def get_my_children():
    """Get current guardian's children"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        if user_role != 'parent':
            return jsonify({'msg': 'Access forbidden: not a parent account'}), 403
        
        guardian = Guardian.query.filter_by(user_id=current_user_data['id']).first()
        if not guardian:
            return jsonify({'msg': 'Guardian profile not found'}), 404
        
        # Get all children linked to this guardian
        children = Student.query.filter_by(guardian_id=guardian.id, is_active=True).all()
        
        return jsonify([child.to_dict() for child in children])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving children: {str(e)}'}), 500

@guardian_bp.route('/children/<int:child_id>/attendance', methods=['GET'])
@jwt_required()
def get_child_attendance(child_id):
    """Get attendance records for a specific child"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        # Admin can access any child's data
        if user_role == 'admin':
            pass
        elif user_role == 'parent':
            # Verify this child belongs to the current guardian
            guardian = Guardian.query.filter_by(user_id=current_user_data['id']).first()
            if not guardian:
                return jsonify({'msg': 'Guardian profile not found'}), 404
            
            child = Student.query.filter_by(id=child_id, guardian_id=guardian.id).first()
            if not child:
                return jsonify({'msg': 'Access forbidden: child not found or not yours'}), 403
        else:
            return jsonify({'msg': 'Access forbidden: insufficient privileges'}), 403
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Attendance.query.filter_by(student_id=child_id)
        
        if start_date:
            query = query.filter(Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        attendance_records = query.order_by(Attendance.date.desc()).all()
        
        return jsonify([record.to_dict() for record in attendance_records])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving child attendance: {str(e)}'}), 500

@guardian_bp.route('/children/<int:child_id>/grades', methods=['GET'])
@jwt_required()
def get_child_grades(child_id):
    """Get grades for a specific child"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        # Admin can access any child's data
        if user_role == 'admin':
            pass
        elif user_role == 'parent':
            # Verify this child belongs to the current guardian
            guardian = Guardian.query.filter_by(user_id=current_user_data['id']).first()
            if not guardian:
                return jsonify({'msg': 'Guardian profile not found'}), 404
            
            child = Student.query.filter_by(id=child_id, guardian_id=guardian.id).first()
            if not child:
                return jsonify({'msg': 'Access forbidden: child not found or not yours'}), 403
        else:
            return jsonify({'msg': 'Access forbidden: insufficient privileges'}), 403
        
        # Get query parameters
        subject = request.args.get('subject')
        term = request.args.get('term')
        academic_year = request.args.get('academic_year')
        
        # Build query
        query = Grade.query.filter_by(student_id=child_id)
        
        if subject:
            query = query.filter_by(subject=subject)
        if term:
            query = query.filter_by(term=term)
        if academic_year:
            query = query.filter_by(academic_year=academic_year)
        
        grades = query.order_by(Grade.date_recorded.desc()).all()
        
        return jsonify([grade.to_dict() for grade in grades])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving child grades: {str(e)}'}), 500

@guardian_bp.route('/children/<int:child_id>/fees', methods=['GET'])
@jwt_required()
def get_child_fees(child_id):
    """Get fee records for a specific child"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        # Admin can access any child's data
        if user_role == 'admin':
            pass
        elif user_role == 'parent':
            # Verify this child belongs to the current guardian
            guardian = Guardian.query.filter_by(user_id=current_user_data['id']).first()
            if not guardian:
                return jsonify({'msg': 'Guardian profile not found'}), 404
            
            child = Student.query.filter_by(id=child_id, guardian_id=guardian.id).first()
            if not child:
                return jsonify({'msg': 'Access forbidden: child not found or not yours'}), 403
        else:
            return jsonify({'msg': 'Access forbidden: insufficient privileges'}), 403
        
        # Get query parameters
        status = request.args.get('status')
        academic_year = request.args.get('academic_year')
        term = request.args.get('term')
        
        # Build query
        query = Fee.query.filter_by(student_id=child_id)
        
        if status:
            query = query.filter_by(status=status)
        if academic_year:
            query = query.filter_by(academic_year=academic_year)
        if term:
            query = query.filter_by(term=term)
        
        fees = query.order_by(Fee.due_date.desc()).all()
        
        return jsonify([fee.to_dict() for fee in fees])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving child fees: {str(e)}'}), 500

@guardian_bp.route('/children/<int:child_id>/summary', methods=['GET'])
@jwt_required()
def get_child_summary(child_id):
    """Get comprehensive summary for a specific child"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        # Admin can access any child's data
        if user_role == 'admin':
            pass
        elif user_role == 'parent':
            # Verify this child belongs to the current guardian
            guardian = Guardian.query.filter_by(user_id=current_user_data['id']).first()
            if not guardian:
                return jsonify({'msg': 'Guardian profile not found'}), 404
            
            child = Student.query.filter_by(id=child_id, guardian_id=guardian.id).first()
            if not child:
                return jsonify({'msg': 'Access forbidden: child not found or not yours'}), 403
        else:
            return jsonify({'msg': 'Access forbidden: insufficient privileges'}), 403
        
        # Get student details
        student = Student.query.get(child_id)
        if not student:
            return jsonify({'msg': 'Student not found'}), 404
        
        summary = {
            'student': student.to_dict(),
            'attendance': {},
            'academic': {},
            'financial': {}
        }
        
        # Attendance summary (current month)
        start_of_month = date.today().replace(day=1)
        attendance_records = Attendance.query.filter(
            Attendance.student_id == child_id,
            Attendance.date >= start_of_month
        ).all()
        
        total_days = len(attendance_records)
        present_days = len([r for r in attendance_records if r.status == 'present'])
        
        summary['attendance'] = {
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': len([r for r in attendance_records if r.status == 'absent']),
            'late_days': len([r for r in attendance_records if r.status == 'late']),
            'percentage': round((present_days / total_days * 100), 2) if total_days > 0 else 0
        }
        
        # Academic summary (current academic year)
        current_year = datetime.now().year
        academic_year = f'{current_year}-{current_year + 1}'
        
        grades = Grade.query.filter_by(
            student_id=child_id,
            academic_year=academic_year
        ).all()
        
        if grades:
            total_percentage = sum(grade.percentage for grade in grades)
            average_percentage = total_percentage / len(grades)
            
            # Grade distribution
            grade_counts = {}
            for grade in grades:
                letter = grade.grade_letter
                grade_counts[letter] = grade_counts.get(letter, 0) + 1
            
            summary['academic'] = {
                'total_grades': len(grades),
                'average_percentage': round(average_percentage, 2),
                'grade_distribution': grade_counts,
                'subjects_count': len(set(grade.subject for grade in grades))
            }
        else:
            summary['academic'] = {
                'total_grades': 0,
                'average_percentage': 0,
                'grade_distribution': {},
                'subjects_count': 0
            }
        
        # Financial summary
        fees = Fee.query.filter_by(student_id=child_id).all()
        
        total_fees = sum(fee.final_amount for fee in fees)
        paid_fees = sum(fee.final_amount for fee in fees if fee.status == 'paid')
        pending_fees = sum(fee.final_amount for fee in fees if fee.status == 'pending')
        overdue_fees = sum(fee.final_amount for fee in fees if fee.is_overdue())
        
        summary['financial'] = {
            'total_fees': total_fees,
            'paid_fees': paid_fees,
            'pending_fees': pending_fees,
            'overdue_fees': overdue_fees,
            'balance': total_fees - paid_fees
        }
        
        return jsonify(summary)
    except Exception as e:
        return jsonify({'msg': f'Error retrieving child summary: {str(e)}'}), 500

@guardian_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics for current guardian"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        if user_role != 'parent':
            return jsonify({'msg': 'Access forbidden: not a parent account'}), 403
        
        guardian = Guardian.query.filter_by(user_id=current_user_data['id']).first()
        if not guardian:
            return jsonify({'msg': 'Guardian profile not found'}), 404
        
        # Get all children
        children = Student.query.filter_by(guardian_id=guardian.id, is_active=True).all()
        child_ids = [child.id for child in children]
        
        stats = {
            'total_children': len(children),
            'total_pending_fees': 0,
            'overall_attendance': 0,
            'academic_performance': 0
        }
        
        if child_ids:
            # Calculate total pending fees for all children
            pending_fees = Fee.query.filter(
                Fee.student_id.in_(child_ids),
                Fee.status == 'pending'
            ).all()
            stats['total_pending_fees'] = sum(fee.final_amount for fee in pending_fees)
            
            # Calculate overall attendance percentage (current month)
            start_of_month = date.today().replace(day=1)
            attendance_records = Attendance.query.filter(
                Attendance.student_id.in_(child_ids),
                Attendance.date >= start_of_month
            ).all()
            
            if attendance_records:
                present_count = len([r for r in attendance_records if r.status == 'present'])
                stats['overall_attendance'] = round((present_count / len(attendance_records) * 100), 2)
            
            # Calculate overall academic performance
            current_year = datetime.now().year
            academic_year = f'{current_year}-{current_year + 1}'
            
            grades = Grade.query.filter(
                Grade.student_id.in_(child_ids),
                Grade.academic_year == academic_year
            ).all()
            
            if grades:
                total_percentage = sum(grade.percentage for grade in grades)
                stats['academic_performance'] = round(total_percentage / len(grades), 2)
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'msg': f'Error retrieving dashboard stats: {str(e)}'}), 500

@guardian_bp.route('/update-profile', methods=['PATCH'])
@jwt_required()
def update_my_profile():
    """Update current guardian's own profile"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        if user_role != 'parent':
            return jsonify({'msg': 'Access forbidden: not a parent account'}), 403
        
        guardian = Guardian.query.filter_by(user_id=current_user_data['id']).first()
        if not guardian:
            return jsonify({'msg': 'Guardian profile not found'}), 404
        
        data = request.get_json()
        
        # Guardians can update certain fields
        updatable_fields = ['phone', 'address', 'occupation', 'emergency_contact']
        for field in updatable_fields:
            if field in data:
                setattr(guardian, field, data[field])
        
        # Update user account phone if provided
        if 'phone' in data:
            user = User.query.get(guardian.user_id)
            if user:
                user.phone = data['phone']
        
        db.session.commit()
        return jsonify({
            'msg': 'Profile updated successfully',
            'guardian': guardian.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error updating profile: {str(e)}'}), 500

@guardian_bp.route('/<int:guardian_id>/link-child', methods=['POST'])
@role_required('admin')
def link_child_to_guardian(guardian_id):
    """Link a child to a guardian (admin only)"""
    try:
        guardian = Guardian.query.get(guardian_id)
        if not guardian:
            return jsonify({'msg': 'Guardian not found'}), 404
        
        data = request.get_json()
        student_id = data.get('student_id')
        
        if not student_id:
            return jsonify({'msg': 'Missing student_id'}), 400
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'msg': 'Student not found'}), 404
        
        # Link the student to the guardian
        student.guardian_id = guardian_id
        db.session.commit()
        
        return jsonify({
            'msg': 'Child linked to guardian successfully',
            'student': student.to_dict(),
            'guardian': guardian.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error linking child to guardian: {str(e)}'}), 500

@guardian_bp.route('/<int:guardian_id>/unlink-child/<int:student_id>', methods=['DELETE'])
@role_required('admin')
def unlink_child_from_guardian(guardian_id, student_id):
    """Unlink a child from a guardian (admin only)"""
    try:
        student = Student.query.filter_by(id=student_id, guardian_id=guardian_id).first()
        if not student:
            return jsonify({'msg': 'Student not found or not linked to this guardian'}), 404
        
        # Remove the link
        student.guardian_id = None
        db.session.commit()
        
        return jsonify({'msg': 'Child unlinked from guardian successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error unlinking child from guardian: {str(e)}'}), 500