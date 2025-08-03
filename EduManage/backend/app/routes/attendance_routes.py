from flask import Blueprint, request, jsonify
from ..models.attendance import Attendance
from ..models.student import Student
from ..models.user import User
from .. import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..auth.decorators import role_required, validate_student_access
from datetime import datetime, date

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/mark', methods=['POST'])
@role_required('admin', 'teacher')
def mark_attendance():
    """Mark attendance for students (admin/teacher only)"""
    try:
        data = request.get_json()
        current_user_data = get_jwt_identity()
        user_id = current_user_data.get('id')
        
        # Validate required fields
        required_fields = ['student_id', 'date', 'status']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'msg': f'Missing required field: {field}'}), 400
        
        student_id = data['student_id']
        attendance_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        status = data['status']
        
        # Validate status
        if status not in ['present', 'absent', 'late', 'excused']:
            return jsonify({'msg': 'Invalid status. Must be: present, absent, late, or excused'}), 400
        
        # Check if student exists
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'msg': 'Student not found'}), 404
        
        # For teachers, validate they can mark attendance for this student
        if current_user_data.get('role') == 'teacher':
            if not validate_student_access(student_id, current_user_data):
                return jsonify({'msg': 'Access forbidden: student not in your assigned classes'}), 403
        
        # Check if attendance already marked for this date
        existing_attendance = Attendance.query.filter_by(
            student_id=student_id,
            date=attendance_date
        ).first()
        
        if existing_attendance:
            # Update existing attendance
            existing_attendance.status = status
            existing_attendance.marked_by = user_id
            existing_attendance.time_in = data.get('time_in')
            existing_attendance.time_out = data.get('time_out')
            existing_attendance.remarks = data.get('remarks', '')
            attendance_record = existing_attendance
        else:
            # Create new attendance record
            attendance_record = Attendance(
                student_id=student_id,
                date=attendance_date,
                status=status,
                marked_by=user_id,
                time_in=data.get('time_in'),
                time_out=data.get('time_out'),
                remarks=data.get('remarks', '')
            )
            db.session.add(attendance_record)
        
        db.session.commit()
        
        return jsonify({
            'msg': 'Attendance marked successfully',
            'attendance': attendance_record.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error marking attendance: {str(e)}'}), 500

@attendance_bp.route('/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_attendance(student_id):
    """Get attendance records for a specific student"""
    try:
        current_user_data = get_jwt_identity()
        
        # Validate access to this student's attendance
        if not validate_student_access(student_id, current_user_data):
            return jsonify({'msg': 'Access forbidden: cannot view this student\'s attendance'}), 403
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Attendance.query.filter_by(student_id=student_id)
        
        if start_date:
            query = query.filter(Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        attendance_records = query.order_by(Attendance.date.desc()).all()
        
        return jsonify([record.to_dict() for record in attendance_records])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving attendance: {str(e)}'}), 500

@attendance_bp.route('/student/<int:student_id>/summary', methods=['GET'])
@jwt_required()
def get_attendance_summary(student_id):
    """Get attendance summary for a student"""
    try:
        current_user_data = get_jwt_identity()
        
        # Validate access to this student's attendance
        if not validate_student_access(student_id, current_user_data):
            return jsonify({'msg': 'Access forbidden: cannot view this student\'s attendance'}), 403
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Attendance.query.filter_by(student_id=student_id)
        
        if start_date:
            query = query.filter(Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        attendance_records = query.all()
        
        # Calculate summary
        total_days = len(attendance_records)
        present_days = len([r for r in attendance_records if r.status == 'present'])
        absent_days = len([r for r in attendance_records if r.status == 'absent'])
        late_days = len([r for r in attendance_records if r.status == 'late'])
        excused_days = len([r for r in attendance_records if r.status == 'excused'])
        
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        summary = {
            'student_id': student_id,
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'excused_days': excused_days,
            'attendance_percentage': round(attendance_percentage, 2)
        }
        
        return jsonify(summary)
    except Exception as e:
        return jsonify({'msg': f'Error calculating attendance summary: {str(e)}'}), 500

@attendance_bp.route('/class/<class_name>/date/<date_str>', methods=['GET'])
@role_required('admin', 'teacher')
def get_class_attendance_by_date(class_name, date_str):
    """Get attendance for all students in a class on a specific date"""
    try:
        current_user_data = get_jwt_identity()
        
        # For teachers, validate they can access this class
        if current_user_data.get('role') == 'teacher':
            from ..models.teacher import Teacher
            teacher = Teacher.query.filter_by(user_id=current_user_data['id']).first()
            if teacher and teacher.classes_assigned:
                import json
                try:
                    assigned_classes = json.loads(teacher.classes_assigned)
                    if class_name not in assigned_classes:
                        return jsonify({'msg': 'Access forbidden: class not assigned to you'}), 403
                except:
                    return jsonify({'msg': 'Error validating class assignment'}), 500
        
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get all students in the class
        students = Student.query.filter_by(class_name=class_name, is_active=True).all()
        
        # Get attendance records for this date
        attendance_records = Attendance.query.filter_by(date=attendance_date).all()
        attendance_dict = {record.student_id: record for record in attendance_records}
        
        result = []
        for student in students:
            attendance_record = attendance_dict.get(student.id)
            student_data = student.to_dict()
            student_data['attendance'] = attendance_record.to_dict() if attendance_record else None
            result.append(student_data)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'msg': f'Error retrieving class attendance: {str(e)}'}), 500

@attendance_bp.route('/my-attendance', methods=['GET'])
@jwt_required()
def get_my_attendance():
    """Get current student's own attendance records"""
    try:
        current_user_data = get_jwt_identity()
        user_role = current_user_data.get('role')
        
        if user_role != 'student':
            return jsonify({'msg': 'Access forbidden: not a student account'}), 403
        
        # Find student profile
        student = Student.query.filter_by(user_id=current_user_data['id']).first()
        if not student:
            return jsonify({'msg': 'Student profile not found'}), 404
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Attendance.query.filter_by(student_id=student.id)
        
        if start_date:
            query = query.filter(Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        attendance_records = query.order_by(Attendance.date.desc()).all()
        
        return jsonify([record.to_dict() for record in attendance_records])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving attendance: {str(e)}'}), 500

@attendance_bp.route('/bulk-mark', methods=['POST'])
@role_required('admin', 'teacher')
def bulk_mark_attendance():
    """Mark attendance for multiple students at once"""
    try:
        data = request.get_json()
        current_user_data = get_jwt_identity()
        user_id = current_user_data.get('id')
        
        # Validate required fields
        if not data.get('attendance_records') or not isinstance(data['attendance_records'], list):
            return jsonify({'msg': 'Missing or invalid attendance_records field'}), 400
        
        attendance_date = data.get('date')
        if not attendance_date:
            return jsonify({'msg': 'Missing date field'}), 400
        
        attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        
        results = []
        for record in data['attendance_records']:
            try:
                student_id = record.get('student_id')
                status = record.get('status')
                
                if not student_id or not status:
                    results.append({
                        'student_id': student_id,
                        'status': 'error',
                        'message': 'Missing student_id or status'
                    })
                    continue
                
                # Validate status
                if status not in ['present', 'absent', 'late', 'excused']:
                    results.append({
                        'student_id': student_id,
                        'status': 'error',
                        'message': 'Invalid status'
                    })
                    continue
                
                # For teachers, validate access
                if current_user_data.get('role') == 'teacher':
                    if not validate_student_access(student_id, current_user_data):
                        results.append({
                            'student_id': student_id,
                            'status': 'error',
                            'message': 'Access forbidden'
                        })
                        continue
                
                # Check if attendance already exists
                existing = Attendance.query.filter_by(
                    student_id=student_id,
                    date=attendance_date
                ).first()
                
                if existing:
                    existing.status = status
                    existing.marked_by = user_id
                    existing.remarks = record.get('remarks', '')
                else:
                    new_attendance = Attendance(
                        student_id=student_id,
                        date=attendance_date,
                        status=status,
                        marked_by=user_id,
                        remarks=record.get('remarks', '')
                    )
                    db.session.add(new_attendance)
                
                results.append({
                    'student_id': student_id,
                    'status': 'success',
                    'message': 'Attendance marked successfully'
                })
                
            except Exception as e:
                results.append({
                    'student_id': record.get('student_id'),
                    'status': 'error',
                    'message': str(e)
                })
        
        db.session.commit()
        
        return jsonify({
            'msg': 'Bulk attendance marking completed',
            'results': results
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error marking bulk attendance: {str(e)}'}), 500