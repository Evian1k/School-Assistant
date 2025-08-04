from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.notification import Notification
from ..models.user import User
from ..models.student import Student
from ..models.guardian import Guardian
from .. import db
from datetime import datetime

notification_bp = Blueprint('notifications', __name__)

def get_current_user_role():
    current_user = get_jwt_identity()
    return current_user.get('role')

def get_current_user_id():
    current_user = get_jwt_identity()
    return current_user.get('id')

@notification_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        user_id = get_current_user_id()
        user_role = get_current_user_role()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        notification_type = request.args.get('type')
        is_read = request.args.get('read')
        
        query = Notification.query.filter_by(recipient_id=user_id)
        
        # Filter by type
        if notification_type:
            query = query.filter_by(notification_type=notification_type)
        
        # Filter by read status
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            query = query.filter_by(is_read=is_read_bool)
        
        # Paginate results
        notifications = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'notifications': [notification.to_dict() for notification in notifications.items],
            'total': notifications.total,
            'pages': notifications.pages,
            'current_page': page,
            'has_next': notifications.has_next,
            'has_prev': notifications.has_prev
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/<int:notification_id>', methods=['GET'])
@jwt_required()
def get_notification(notification_id):
    try:
        user_id = get_current_user_id()
        
        notification = Notification.query.filter_by(
            id=notification_id, 
            recipient_id=user_id
        ).first()
        
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        # Mark as read
        notification.is_read = True
        db.session.commit()
        
        return jsonify(notification.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(notification_id):
    try:
        user_id = get_current_user_id()
        
        notification = Notification.query.filter_by(
            id=notification_id, 
            recipient_id=user_id
        ).first()
        
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'message': 'Notification marked as read'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_as_read():
    try:
        user_id = get_current_user_id()
        
        Notification.query.filter_by(
            recipient_id=user_id,
            is_read=False
        ).update({'is_read': True})
        
        db.session.commit()
        
        return jsonify({'message': 'All notifications marked as read'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/send', methods=['POST'])
@jwt_required()
def send_notification():
    try:
        user_role = get_current_user_role()
        if user_role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['recipient_id', 'title', 'message', 'notification_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if recipient exists
        recipient = User.query.get(data['recipient_id'])
        if not recipient:
            return jsonify({'error': 'Recipient not found'}), 404
        
        notification = Notification(
            recipient_id=data['recipient_id'],
            recipient_type=recipient.role,
            title=data['title'],
            message=data['message'],
            notification_type=data['notification_type'],
            priority=data.get('priority', 'normal')
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Notification sent successfully',
            'notification': notification.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/bulk-send', methods=['POST'])
@jwt_required()
def send_bulk_notifications():
    try:
        user_role = get_current_user_role()
        if user_role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['recipient_type', 'title', 'message', 'notification_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        recipient_type = data['recipient_type']
        valid_types = ['student', 'guardian', 'teacher', 'admin']
        
        if recipient_type not in valid_types:
            return jsonify({'error': 'Invalid recipient type'}), 400
        
        # Get all users of the specified type
        users = User.query.filter_by(role=recipient_type, is_active=True).all()
        
        notifications = []
        for user in users:
            notification = Notification(
                recipient_id=user.id,
                recipient_type=user.role,
                title=data['title'],
                message=data['message'],
                notification_type=data['notification_type'],
                priority=data.get('priority', 'normal')
            )
            notifications.append(notification)
        
        db.session.add_all(notifications)
        db.session.commit()
        
        return jsonify({
            'message': f'Bulk notification sent to {len(notifications)} recipients',
            'sent_count': len(notifications)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/fee-reminder', methods=['POST'])
@jwt_required()
def send_fee_reminder():
    try:
        user_role = get_current_user_role()
        if user_role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        student_id = data.get('student_id')
        
        if student_id:
            # Send to specific student's guardian
            student = Student.query.get(student_id)
            if not student or not student.guardian:
                return jsonify({'error': 'Student or guardian not found'}), 404
            
            guardian = student.guardian
            notification = Notification(
                recipient_id=guardian.user_id,
                recipient_type='guardian',
                title='Fee Reminder',
                message=f'Dear {guardian.name}, please note that fee payment for {student.name} is due. Please make the payment at your earliest convenience.',
                notification_type='fee_reminder',
                priority='high'
            )
            
            db.session.add(notification)
            db.session.commit()
            
            return jsonify({
                'message': 'Fee reminder sent successfully',
                'notification': notification.to_dict()
            }), 201
        
        else:
            # Send to all guardians with pending fees
            # This is a simplified version - in real implementation, you'd check for actual pending fees
            guardians = Guardian.query.filter_by(is_active=True).all()
            
            notifications = []
            for guardian in guardians:
                notification = Notification(
                    recipient_id=guardian.user_id,
                    recipient_type='guardian',
                    title='Fee Reminder',
                    message='Dear parent, please note that fee payment is due. Please make the payment at your earliest convenience.',
                    notification_type='fee_reminder',
                    priority='high'
                )
                notifications.append(notification)
            
            db.session.add_all(notifications)
            db.session.commit()
            
            return jsonify({
                'message': f'Fee reminders sent to {len(notifications)} guardians',
                'sent_count': len(notifications)
            }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/attendance-alert', methods=['POST'])
@jwt_required()
def send_attendance_alert():
    try:
        user_role = get_current_user_role()
        if user_role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        student_id = data.get('student_id')
        date = data.get('date')
        status = data.get('status')
        
        if not all([student_id, date, status]):
            return jsonify({'error': 'Student ID, date, and status are required'}), 400
        
        student = Student.query.get(student_id)
        if not student or not student.guardian:
            return jsonify({'error': 'Student or guardian not found'}), 404
        
        guardian = student.guardian
        
        if status == 'absent':
            title = 'Absence Alert'
            message = f'Dear {guardian.name}, {student.name} was absent on {date}. Please contact the school if this was unexpected.'
            priority = 'high'
        else:
            title = 'Attendance Update'
            message = f'Dear {guardian.name}, {student.name} was present on {date}.'
            priority = 'normal'
        
        notification = Notification(
            recipient_id=guardian.user_id,
            recipient_type='guardian',
            title=title,
            message=message,
            notification_type='attendance',
            priority=priority
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Attendance alert sent successfully',
            'notification': notification.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_notification_stats():
    try:
        user_id = get_current_user_id()
        
        total_notifications = Notification.query.filter_by(recipient_id=user_id).count()
        unread_notifications = Notification.query.filter_by(
            recipient_id=user_id, 
            is_read=False
        ).count()
        
        # Notifications by type
        type_stats = db.session.query(
            Notification.notification_type,
            db.func.count(Notification.id)
        ).filter_by(recipient_id=user_id).group_by(Notification.notification_type).all()
        
        stats = {
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'read_notifications': total_notifications - unread_notifications,
            'by_type': dict(type_stats)
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500