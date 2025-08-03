from flask import Blueprint, request, jsonify
from ..models.fee import Fee
from ..models.student import Student
from ..models.user import User
from .. import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..auth.decorators import role_required, validate_student_access
from datetime import datetime, date
import uuid

fee_bp = Blueprint('fees', __name__)

@fee_bp.route('/', methods=['POST'])
@role_required('admin')
def create_fee():
    """Create a new fee record (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_id', 'fee_type', 'amount', 'due_date', 'term', 'academic_year']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'msg': f'Missing required field: {field}'}), 400
        
        # Check if student exists
        student = Student.query.get(data['student_id'])
        if not student:
            return jsonify({'msg': 'Student not found'}), 404
        
        # Create fee record
        fee = Fee(
            student_id=data['student_id'],
            fee_type=data['fee_type'],
            amount=float(data['amount']),
            discount=float(data.get('discount', 0)),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
            term=data['term'],
            academic_year=data['academic_year'],
            remarks=data.get('remarks', '')
        )
        
        # Calculate final amount
        fee.calculate_final_amount()
        
        db.session.add(fee)
        db.session.commit()
        
        return jsonify({
            'msg': 'Fee created successfully',
            'fee': fee.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error creating fee: {str(e)}'}), 500

@fee_bp.route('/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_fees(student_id):
    """Get fee records for a specific student"""
    try:
        current_user_data = get_jwt_identity()
        
        # Validate access to this student's fees
        if not validate_student_access(student_id, current_user_data):
            return jsonify({'msg': 'Access forbidden: cannot view this student\'s fees'}), 403
        
        # Get query parameters
        status = request.args.get('status')  # pending, paid, overdue
        academic_year = request.args.get('academic_year')
        term = request.args.get('term')
        
        # Build query
        query = Fee.query.filter_by(student_id=student_id)
        
        if status:
            query = query.filter_by(status=status)
        if academic_year:
            query = query.filter_by(academic_year=academic_year)
        if term:
            query = query.filter_by(term=term)
        
        fees = query.order_by(Fee.due_date.desc()).all()
        
        return jsonify([fee.to_dict() for fee in fees])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving fees: {str(e)}'}), 500

@fee_bp.route('/my-fees', methods=['GET'])
@jwt_required()
def get_my_fees():
    """Get current student's own fee records"""
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
        status = request.args.get('status')
        academic_year = request.args.get('academic_year')
        term = request.args.get('term')
        
        # Build query
        query = Fee.query.filter_by(student_id=student.id)
        
        if status:
            query = query.filter_by(status=status)
        if academic_year:
            query = query.filter_by(academic_year=academic_year)
        if term:
            query = query.filter_by(term=term)
        
        fees = query.order_by(Fee.due_date.desc()).all()
        
        return jsonify([fee.to_dict() for fee in fees])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving fees: {str(e)}'}), 500

@fee_bp.route('/<int:fee_id>/pay', methods=['POST'])
@role_required('admin')
def process_payment(fee_id):
    """Process fee payment (admin only)"""
    try:
        fee = Fee.query.get(fee_id)
        if not fee:
            return jsonify({'msg': 'Fee record not found'}), 404
        
        data = request.get_json()
        current_user_data = get_jwt_identity()
        
        # Validate required fields
        required_fields = ['payment_method']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'msg': f'Missing required field: {field}'}), 400
        
        # Update fee record
        fee.status = 'paid'
        fee.paid_date = datetime.utcnow().date()
        fee.payment_method = data['payment_method']
        fee.transaction_id = data.get('transaction_id', str(uuid.uuid4())[:12])
        fee.receipt_number = data.get('receipt_number', f'REC-{fee.id}-{int(datetime.now().timestamp())}')
        fee.processed_by = current_user_data['id']
        fee.remarks = data.get('remarks', fee.remarks)
        
        db.session.commit()
        
        return jsonify({
            'msg': 'Payment processed successfully',
            'fee': fee.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error processing payment: {str(e)}'}), 500

@fee_bp.route('/student/<int:student_id>/summary', methods=['GET'])
@jwt_required()
def get_fee_summary(student_id):
    """Get fee summary for a student"""
    try:
        current_user_data = get_jwt_identity()
        
        # Validate access to this student's fees
        if not validate_student_access(student_id, current_user_data):
            return jsonify({'msg': 'Access forbidden: cannot view this student\'s fees'}), 403
        
        # Get query parameters
        academic_year = request.args.get('academic_year')
        
        # Build query
        query = Fee.query.filter_by(student_id=student_id)
        if academic_year:
            query = query.filter_by(academic_year=academic_year)
        
        fees = query.all()
        
        # Calculate summary
        total_fees = sum(fee.final_amount for fee in fees)
        paid_fees = sum(fee.final_amount for fee in fees if fee.status == 'paid')
        pending_fees = sum(fee.final_amount for fee in fees if fee.status == 'pending')
        overdue_fees = sum(fee.final_amount for fee in fees if fee.is_overdue())
        
        summary = {
            'student_id': student_id,
            'total_fees': total_fees,
            'paid_fees': paid_fees,
            'pending_fees': pending_fees,
            'overdue_fees': overdue_fees,
            'balance': total_fees - paid_fees,
            'fee_count': len(fees),
            'paid_count': len([f for f in fees if f.status == 'paid']),
            'pending_count': len([f for f in fees if f.status == 'pending']),
            'overdue_count': len([f for f in fees if f.is_overdue()])
        }
        
        return jsonify(summary)
    except Exception as e:
        return jsonify({'msg': f'Error calculating fee summary: {str(e)}'}), 500

@fee_bp.route('/overdue', methods=['GET'])
@role_required('admin')
def get_overdue_fees():
    """Get all overdue fees (admin only)"""
    try:
        current_date = datetime.utcnow().date()
        overdue_fees = Fee.query.filter(
            Fee.status == 'pending',
            Fee.due_date < current_date
        ).order_by(Fee.due_date.asc()).all()
        
        return jsonify([fee.to_dict() for fee in overdue_fees])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving overdue fees: {str(e)}'}), 500

@fee_bp.route('/bulk-create', methods=['POST'])
@role_required('admin')
def bulk_create_fees():
    """Create fees for multiple students (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_ids', 'fee_type', 'amount', 'due_date', 'term', 'academic_year']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'msg': f'Missing required field: {field}'}), 400
        
        student_ids = data['student_ids']
        if not isinstance(student_ids, list):
            return jsonify({'msg': 'student_ids must be a list'}), 400
        
        results = []
        for student_id in student_ids:
            try:
                # Check if student exists
                student = Student.query.get(student_id)
                if not student:
                    results.append({
                        'student_id': student_id,
                        'status': 'error',
                        'message': 'Student not found'
                    })
                    continue
                
                # Create fee record
                fee = Fee(
                    student_id=student_id,
                    fee_type=data['fee_type'],
                    amount=float(data['amount']),
                    discount=float(data.get('discount', 0)),
                    due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
                    term=data['term'],
                    academic_year=data['academic_year'],
                    remarks=data.get('remarks', '')
                )
                
                # Calculate final amount
                fee.calculate_final_amount()
                
                db.session.add(fee)
                
                results.append({
                    'student_id': student_id,
                    'status': 'success',
                    'message': 'Fee created successfully'
                })
                
            except Exception as e:
                results.append({
                    'student_id': student_id,
                    'status': 'error',
                    'message': str(e)
                })
        
        db.session.commit()
        
        return jsonify({
            'msg': 'Bulk fee creation completed',
            'results': results
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error creating bulk fees: {str(e)}'}), 500

@fee_bp.route('/<int:fee_id>', methods=['PATCH'])
@role_required('admin')
def update_fee(fee_id):
    """Update fee record (admin only)"""
    try:
        fee = Fee.query.get(fee_id)
        if not fee:
            return jsonify({'msg': 'Fee record not found'}), 404
        
        data = request.get_json()
        
        # Update fee fields
        updatable_fields = ['fee_type', 'amount', 'discount', 'due_date', 'status', 'remarks']
        for field in updatable_fields:
            if field in data:
                if field == 'due_date':
                    setattr(fee, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                elif field in ['amount', 'discount']:
                    setattr(fee, field, float(data[field]))
                else:
                    setattr(fee, field, data[field])
        
        # Recalculate final amount if amount or discount changed
        if 'amount' in data or 'discount' in data:
            fee.calculate_final_amount()
        
        db.session.commit()
        
        return jsonify({
            'msg': 'Fee updated successfully',
            'fee': fee.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error updating fee: {str(e)}'}), 500

@fee_bp.route('/<int:fee_id>', methods=['DELETE'])
@role_required('admin')
def delete_fee(fee_id):
    """Delete fee record (admin only)"""
    try:
        fee = Fee.query.get(fee_id)
        if not fee:
            return jsonify({'msg': 'Fee record not found'}), 404
        
        db.session.delete(fee)
        db.session.commit()
        
        return jsonify({'msg': 'Fee deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error deleting fee: {str(e)}'}), 500