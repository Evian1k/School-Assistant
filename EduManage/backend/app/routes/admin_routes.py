from flask import Blueprint, request, jsonify
from ..models.user import User
from ..models.student import Student
from ..models.teacher import Teacher
from ..models.guardian import Guardian
from ..models.attendance import Attendance
from ..models.grade import Grade
from ..models.fee import Fee
from ..models.notification import Notification
from .. import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..auth.decorators import role_required
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard-stats', methods=['GET'])
@role_required('admin')
def get_dashboard_stats():
    """Get comprehensive dashboard statistics for admin"""
    try:
        stats = {}
        
        # User counts
        stats['total_users'] = User.query.filter_by(is_active=True).count()
        stats['total_students'] = Student.query.filter_by(is_active=True).count()
        stats['total_teachers'] = Teacher.query.filter_by(is_active=True).count()
        stats['total_guardians'] = Guardian.query.filter_by(is_active=True).count()
        
        # Financial stats
        total_fees = db.session.query(func.sum(Fee.final_amount)).filter_by(status='pending').scalar() or 0
        stats['pending_fees'] = float(total_fees)
        
        paid_fees = db.session.query(func.sum(Fee.final_amount)).filter_by(status='paid').scalar() or 0
        stats['collected_fees'] = float(paid_fees)
        
        overdue_fees = db.session.query(func.sum(Fee.final_amount)).filter(
            and_(Fee.status == 'pending', Fee.due_date < date.today())
        ).scalar() or 0
        stats['overdue_fees'] = float(overdue_fees)
        
        # Attendance stats for today
        today = date.today()
        total_students_today = stats['total_students']
        present_today = Attendance.query.filter_by(date=today, status='present').count()
        absent_today = Attendance.query.filter_by(date=today, status='absent').count()
        
        stats['attendance_today'] = {
            'total_students': total_students_today,
            'present': present_today,
            'absent': absent_today,
            'percentage': round((present_today / total_students_today * 100), 2) if total_students_today > 0 else 0
        }
        
        # Monthly stats
        start_of_month = date.today().replace(day=1)
        month_attendance = db.session.query(
            func.count(Attendance.id).label('total'),
            func.sum(func.case([(Attendance.status == 'present', 1)], else_=0)).label('present')
        ).filter(Attendance.date >= start_of_month).first()
        
        stats['monthly_attendance'] = {
            'total_records': month_attendance.total or 0,
            'present_records': month_attendance.present or 0,
            'percentage': round((month_attendance.present / month_attendance.total * 100), 2) if month_attendance.total > 0 else 0
        }
        
        # Grade distribution
        grade_distribution = db.session.query(
            Grade.grade_letter,
            func.count(Grade.id).label('count')
        ).group_by(Grade.grade_letter).all()
        
        stats['grade_distribution'] = {grade.grade_letter: grade.count for grade in grade_distribution}
        
        # Recent activities count
        stats['recent_notifications'] = Notification.query.filter(
            Notification.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'msg': f'Error retrieving dashboard stats: {str(e)}'}), 500

@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_all_users():
    """Get all users with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role_filter = request.args.get('role')
        search = request.args.get('search', '')
        
        query = User.query.filter_by(is_active=True)
        
        if role_filter:
            query = query.filter_by(role=role_filter)
        
        if search:
            query = query.filter(User.name.contains(search) | User.email.contains(search))
        
        users = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'msg': f'Error retrieving users: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['PATCH'])
@role_required('admin')
def toggle_user_status(user_id):
    """Activate or deactivate a user account"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        user.is_active = not user.is_active
        
        # Also update related profiles
        if user.role == 'student':
            student = Student.query.filter_by(user_id=user_id).first()
            if student:
                student.is_active = user.is_active
        elif user.role == 'teacher':
            teacher = Teacher.query.filter_by(user_id=user_id).first()
            if teacher:
                teacher.is_active = user.is_active
        elif user.role == 'parent':
            guardian = Guardian.query.filter_by(user_id=user_id).first()
            if guardian:
                guardian.is_active = user.is_active
        
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        return jsonify({
            'msg': f'User {status} successfully',
            'user': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error updating user status: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@role_required('admin')
def reset_user_password(user_id):
    """Reset user password to default"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        data = request.get_json()
        new_password = data.get('password', f'{user.role}123')  # Default password based on role
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'msg': 'Password reset successfully',
            'new_password': new_password
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error resetting password: {str(e)}'}), 500

@admin_bp.route('/bulk-notifications', methods=['POST'])
@role_required('admin')
def send_bulk_notifications():
    """Send notifications to multiple users"""
    try:
        data = request.get_json()
        current_user_data = get_jwt_identity()
        
        required_fields = ['title', 'message', 'notification_type', 'recipient_roles']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'msg': f'Missing required field: {field}'}), 400
        
        recipient_roles = data['recipient_roles']
        if not isinstance(recipient_roles, list):
            return jsonify({'msg': 'recipient_roles must be a list'}), 400
        
        # Get users with specified roles
        recipients = User.query.filter(
            User.role.in_(recipient_roles),
            User.is_active == True
        ).all()
        
        notifications_created = 0
        for recipient in recipients:
            notification = Notification(
                recipient_id=recipient.id,
                sender_id=current_user_data['id'],
                title=data['title'],
                message=data['message'],
                notification_type=data['notification_type'],
                priority=data.get('priority', 'normal'),
                delivery_method=data.get('delivery_method', 'in_app')
            )
            db.session.add(notification)
            notifications_created += 1
        
        db.session.commit()
        
        return jsonify({
            'msg': f'Bulk notifications sent successfully',
            'notifications_created': notifications_created,
            'recipients': len(recipients)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error sending bulk notifications: {str(e)}'}), 500

@admin_bp.route('/reports/attendance', methods=['GET'])
@role_required('admin')
def get_attendance_report():
    """Generate attendance report"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        class_name = request.args.get('class_name')
        
        if not start_date or not end_date:
            # Default to current month
            today = date.today()
            start_date = today.replace(day=1).isoformat()
            end_date = today.isoformat()
        
        query = Attendance.query.filter(
            Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
            Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date()
        )
        
        if class_name:
            # Filter by class
            student_ids = db.session.query(Student.id).filter_by(class_name=class_name).all()
            student_ids = [sid[0] for sid in student_ids]
            query = query.filter(Attendance.student_id.in_(student_ids))
        
        attendance_records = query.all()
        
        # Calculate statistics
        total_records = len(attendance_records)
        present_count = len([r for r in attendance_records if r.status == 'present'])
        absent_count = len([r for r in attendance_records if r.status == 'absent'])
        late_count = len([r for r in attendance_records if r.status == 'late'])
        
        # Group by student
        student_stats = {}
        for record in attendance_records:
            student_id = record.student_id
            if student_id not in student_stats:
                student = Student.query.get(student_id)
                student_stats[student_id] = {
                    'student': student.to_dict() if student else None,
                    'total': 0,
                    'present': 0,
                    'absent': 0,
                    'late': 0
                }
            
            student_stats[student_id]['total'] += 1
            student_stats[student_id][record.status] += 1
        
        # Calculate percentages
        for stats in student_stats.values():
            if stats['total'] > 0:
                stats['attendance_percentage'] = round((stats['present'] / stats['total']) * 100, 2)
            else:
                stats['attendance_percentage'] = 0
        
        report = {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'class_name': class_name
            },
            'summary': {
                'total_records': total_records,
                'present_count': present_count,
                'absent_count': absent_count,
                'late_count': late_count,
                'overall_percentage': round((present_count / total_records * 100), 2) if total_records > 0 else 0
            },
            'student_details': list(student_stats.values())
        }
        
        return jsonify(report)
    except Exception as e:
        return jsonify({'msg': f'Error generating attendance report: {str(e)}'}), 500

@admin_bp.route('/reports/fees', methods=['GET'])
@role_required('admin')
def get_fee_report():
    """Generate fee collection report"""
    try:
        academic_year = request.args.get('academic_year')
        term = request.args.get('term')
        status = request.args.get('status')
        
        query = Fee.query
        
        if academic_year:
            query = query.filter_by(academic_year=academic_year)
        if term:
            query = query.filter_by(term=term)
        if status:
            query = query.filter_by(status=status)
        
        fees = query.all()
        
        # Calculate totals
        total_amount = sum(fee.final_amount for fee in fees)
        paid_amount = sum(fee.final_amount for fee in fees if fee.status == 'paid')
        pending_amount = sum(fee.final_amount for fee in fees if fee.status == 'pending')
        overdue_amount = sum(fee.final_amount for fee in fees if fee.is_overdue())
        
        # Group by fee type
        fee_type_stats = {}
        for fee in fees:
            fee_type = fee.fee_type
            if fee_type not in fee_type_stats:
                fee_type_stats[fee_type] = {
                    'fee_type': fee_type,
                    'total_amount': 0,
                    'paid_amount': 0,
                    'pending_amount': 0,
                    'count': 0
                }
            
            fee_type_stats[fee_type]['total_amount'] += fee.final_amount
            fee_type_stats[fee_type]['count'] += 1
            
            if fee.status == 'paid':
                fee_type_stats[fee_type]['paid_amount'] += fee.final_amount
            else:
                fee_type_stats[fee_type]['pending_amount'] += fee.final_amount
        
        report = {
            'filters': {
                'academic_year': academic_year,
                'term': term,
                'status': status
            },
            'summary': {
                'total_fees': len(fees),
                'total_amount': total_amount,
                'paid_amount': paid_amount,
                'pending_amount': pending_amount,
                'overdue_amount': overdue_amount,
                'collection_percentage': round((paid_amount / total_amount * 100), 2) if total_amount > 0 else 0
            },
            'fee_type_breakdown': list(fee_type_stats.values())
        }
        
        return jsonify(report)
    except Exception as e:
        return jsonify({'msg': f'Error generating fee report: {str(e)}'}), 500

@admin_bp.route('/reports/academic', methods=['GET'])
@role_required('admin')
def get_academic_report():
    """Generate academic performance report"""
    try:
        academic_year = request.args.get('academic_year')
        term = request.args.get('term')
        class_name = request.args.get('class_name')
        
        query = Grade.query
        
        if academic_year:
            query = query.filter_by(academic_year=academic_year)
        if term:
            query = query.filter_by(term=term)
        
        if class_name:
            student_ids = db.session.query(Student.id).filter_by(class_name=class_name).all()
            student_ids = [sid[0] for sid in student_ids]
            query = query.filter(Grade.student_id.in_(student_ids))
        
        grades = query.all()
        
        # Calculate overall statistics
        total_grades = len(grades)
        average_percentage = sum(grade.percentage for grade in grades) / total_grades if total_grades > 0 else 0
        
        # Grade distribution
        grade_distribution = {}
        for grade in grades:
            letter = grade.grade_letter
            if letter not in grade_distribution:
                grade_distribution[letter] = 0
            grade_distribution[letter] += 1
        
        # Subject performance
        subject_stats = {}
        for grade in grades:
            subject = grade.subject
            if subject not in subject_stats:
                subject_stats[subject] = {
                    'subject': subject,
                    'total_grades': 0,
                    'total_percentage': 0,
                    'average_percentage': 0
                }
            
            subject_stats[subject]['total_grades'] += 1
            subject_stats[subject]['total_percentage'] += grade.percentage
        
        # Calculate averages
        for stats in subject_stats.values():
            if stats['total_grades'] > 0:
                stats['average_percentage'] = round(stats['total_percentage'] / stats['total_grades'], 2)
        
        report = {
            'filters': {
                'academic_year': academic_year,
                'term': term,
                'class_name': class_name
            },
            'summary': {
                'total_grades': total_grades,
                'average_percentage': round(average_percentage, 2),
                'grade_distribution': grade_distribution
            },
            'subject_performance': list(subject_stats.values())
        }
        
        return jsonify(report)
    except Exception as e:
        return jsonify({'msg': f'Error generating academic report: {str(e)}'}), 500

@admin_bp.route('/system-info', methods=['GET'])
@role_required('admin')
def get_system_info():
    """Get system information and health status"""
    try:
        # Database statistics
        db_stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_students': Student.query.count(),
            'total_teachers': Teacher.query.count(),
            'total_guardians': Guardian.query.count(),
            'total_attendance_records': Attendance.query.count(),
            'total_grades': Grade.query.count(),
            'total_fees': Fee.query.count(),
            'total_notifications': Notification.query.count()
        }
        
        # Recent activity
        recent_logins = User.query.filter(
            User.updated_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        recent_grades = Grade.query.filter(
            Grade.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        recent_attendance = Attendance.query.filter(
            Attendance.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        system_info = {
            'database_stats': db_stats,
            'recent_activity': {
                'recent_logins': recent_logins,
                'recent_grades': recent_grades,
                'recent_attendance': recent_attendance
            },
            'system_health': 'healthy',
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify(system_info)
    except Exception as e:
        return jsonify({'msg': f'Error retrieving system info: {str(e)}'}), 500

@admin_bp.route('/backup/export', methods=['GET'])
@role_required('admin')
def export_data():
    """Export system data for backup"""
    try:
        export_type = request.args.get('type', 'summary')
        
        if export_type == 'summary':
            # Export summary statistics only
            data = {
                'export_date': datetime.utcnow().isoformat(),
                'user_counts': {
                    'total_users': User.query.count(),
                    'students': Student.query.count(),
                    'teachers': Teacher.query.count(),
                    'guardians': Guardian.query.count()
                },
                'academic_data': {
                    'total_grades': Grade.query.count(),
                    'attendance_records': Attendance.query.count(),
                    'fee_records': Fee.query.count()
                }
            }
        else:
            return jsonify({'msg': 'Full data export not implemented yet'}), 501
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'msg': f'Error exporting data: {str(e)}'}), 500