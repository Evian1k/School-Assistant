from flask import Blueprint, request, jsonify
from ..models.grade import Grade
from ..models.student import Student
from ..models.user import User
from .. import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..auth.decorators import role_required, validate_student_access
from datetime import datetime, date

grade_bp = Blueprint('grades', __name__)

@grade_bp.route('/', methods=['POST'])
@role_required('admin', 'teacher')
def create_grade():
    """Create a new grade record (admin/teacher only)"""
    try:
        data = request.get_json()
        current_user_data = get_jwt_identity()
        
        # Validate required fields
        required_fields = ['student_id', 'subject', 'assignment_type', 'score', 'max_score', 'term', 'academic_year']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'msg': f'Missing required field: {field}'}), 400
        
        student_id = data['student_id']
        
        # For teachers, validate they can grade this student
        if current_user_data.get('role') == 'teacher':
            if not validate_student_access(student_id, current_user_data):
                return jsonify({'msg': 'Access forbidden: student not in your assigned classes'}), 403
        
        # Check if student exists
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'msg': 'Student not found'}), 404
        
        # Create grade record
        grade = Grade(
            student_id=student_id,
            subject=data['subject'],
            assignment_type=data['assignment_type'],
            score=float(data['score']),
            max_score=float(data['max_score']),
            term=data['term'],
            academic_year=data['academic_year'],
            recorded_by=current_user_data['id'],
            date_recorded=datetime.strptime(data.get('date_recorded', str(date.today())), '%Y-%m-%d').date(),
            remarks=data.get('remarks', '')
        )
        
        # Calculate percentage and grade letter
        grade.calculate_percentage()
        
        db.session.add(grade)
        db.session.commit()
        
        return jsonify({
            'msg': 'Grade recorded successfully',
            'grade': grade.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error creating grade: {str(e)}'}), 500

@grade_bp.route('/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_grades(student_id):
    """Get grades for a specific student"""
    try:
        current_user_data = get_jwt_identity()
        
        # Validate access to this student's grades
        if not validate_student_access(student_id, current_user_data):
            return jsonify({'msg': 'Access forbidden: cannot view this student\'s grades'}), 403
        
        # Get query parameters
        subject = request.args.get('subject')
        term = request.args.get('term')
        academic_year = request.args.get('academic_year')
        assignment_type = request.args.get('assignment_type')
        
        # Build query
        query = Grade.query.filter_by(student_id=student_id)
        
        if subject:
            query = query.filter_by(subject=subject)
        if term:
            query = query.filter_by(term=term)
        if academic_year:
            query = query.filter_by(academic_year=academic_year)
        if assignment_type:
            query = query.filter_by(assignment_type=assignment_type)
        
        grades = query.order_by(Grade.date_recorded.desc()).all()
        
        return jsonify([grade.to_dict() for grade in grades])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving grades: {str(e)}'}), 500

@grade_bp.route('/my-grades', methods=['GET'])
@jwt_required()
def get_my_grades():
    """Get current student's own grades"""
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
        subject = request.args.get('subject')
        term = request.args.get('term')
        academic_year = request.args.get('academic_year')
        
        # Build query
        query = Grade.query.filter_by(student_id=student.id)
        
        if subject:
            query = query.filter_by(subject=subject)
        if term:
            query = query.filter_by(term=term)
        if academic_year:
            query = query.filter_by(academic_year=academic_year)
        
        grades = query.order_by(Grade.date_recorded.desc()).all()
        
        return jsonify([grade.to_dict() for grade in grades])
    except Exception as e:
        return jsonify({'msg': f'Error retrieving grades: {str(e)}'}), 500

@grade_bp.route('/student/<int:student_id>/summary', methods=['GET'])
@jwt_required()
def get_grade_summary(student_id):
    """Get grade summary for a student"""
    try:
        current_user_data = get_jwt_identity()
        
        # Validate access to this student's grades
        if not validate_student_access(student_id, current_user_data):
            return jsonify({'msg': 'Access forbidden: cannot view this student\'s grades'}), 403
        
        # Get query parameters
        academic_year = request.args.get('academic_year')
        term = request.args.get('term')
        
        # Build query
        query = Grade.query.filter_by(student_id=student_id)
        if academic_year:
            query = query.filter_by(academic_year=academic_year)
        if term:
            query = query.filter_by(term=term)
        
        grades = query.all()
        
        # Calculate summary by subject
        subject_summaries = {}
        for grade in grades:
            subject = grade.subject
            if subject not in subject_summaries:
                subject_summaries[subject] = {
                    'subject': subject,
                    'total_score': 0,
                    'total_max': 0,
                    'count': 0,
                    'grades': []
                }
            
            subject_summaries[subject]['total_score'] += grade.score
            subject_summaries[subject]['total_max'] += grade.max_score
            subject_summaries[subject]['count'] += 1
            subject_summaries[subject]['grades'].append({
                'assignment_type': grade.assignment_type,
                'score': grade.score,
                'max_score': grade.max_score,
                'percentage': grade.percentage,
                'grade_letter': grade.grade_letter,
                'date': grade.date_recorded.isoformat() if grade.date_recorded else None
            })
        
        # Calculate averages
        for subject_data in subject_summaries.values():
            if subject_data['total_max'] > 0:
                subject_data['average_percentage'] = round(
                    (subject_data['total_score'] / subject_data['total_max']) * 100, 2
                )
            else:
                subject_data['average_percentage'] = 0
            
            # Determine grade letter based on average
            avg = subject_data['average_percentage']
            if avg >= 90:
                subject_data['grade_letter'] = 'A'
            elif avg >= 80:
                subject_data['grade_letter'] = 'B'
            elif avg >= 70:
                subject_data['grade_letter'] = 'C'
            elif avg >= 60:
                subject_data['grade_letter'] = 'D'
            else:
                subject_data['grade_letter'] = 'F'
        
        # Overall summary
        total_percentage = sum(s['average_percentage'] for s in subject_summaries.values())
        overall_average = total_percentage / len(subject_summaries) if subject_summaries else 0
        
        summary = {
            'student_id': student_id,
            'overall_average': round(overall_average, 2),
            'total_subjects': len(subject_summaries),
            'total_assignments': len(grades),
            'subjects': list(subject_summaries.values())
        }
        
        return jsonify(summary)
    except Exception as e:
        return jsonify({'msg': f'Error calculating grade summary: {str(e)}'}), 500

@grade_bp.route('/<int:grade_id>', methods=['PATCH'])
@role_required('admin', 'teacher')
def update_grade(grade_id):
    """Update grade record (admin/teacher only)"""
    try:
        grade = Grade.query.get(grade_id)
        if not grade:
            return jsonify({'msg': 'Grade record not found'}), 404
        
        current_user_data = get_jwt_identity()
        
        # For teachers, validate they can update this grade
        if current_user_data.get('role') == 'teacher':
            if not validate_student_access(grade.student_id, current_user_data):
                return jsonify({'msg': 'Access forbidden: cannot update grade for this student'}), 403
        
        data = request.get_json()
        
        # Update grade fields
        updatable_fields = ['subject', 'assignment_type', 'score', 'max_score', 'term', 'academic_year', 'remarks']
        for field in updatable_fields:
            if field in data:
                if field in ['score', 'max_score']:
                    setattr(grade, field, float(data[field]))
                else:
                    setattr(grade, field, data[field])
        
        # Recalculate percentage if score or max_score changed
        if 'score' in data or 'max_score' in data:
            grade.calculate_percentage()
        
        db.session.commit()
        
        return jsonify({
            'msg': 'Grade updated successfully',
            'grade': grade.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error updating grade: {str(e)}'}), 500

@grade_bp.route('/<int:grade_id>', methods=['DELETE'])
@role_required('admin', 'teacher')
def delete_grade(grade_id):
    """Delete grade record (admin/teacher only)"""
    try:
        grade = Grade.query.get(grade_id)
        if not grade:
            return jsonify({'msg': 'Grade record not found'}), 404
        
        current_user_data = get_jwt_identity()
        
        # For teachers, validate they can delete this grade
        if current_user_data.get('role') == 'teacher':
            if not validate_student_access(grade.student_id, current_user_data):
                return jsonify({'msg': 'Access forbidden: cannot delete grade for this student'}), 403
        
        db.session.delete(grade)
        db.session.commit()
        
        return jsonify({'msg': 'Grade deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error deleting grade: {str(e)}'}), 500

@grade_bp.route('/bulk-create', methods=['POST'])
@role_required('admin', 'teacher')
def bulk_create_grades():
    """Create grades for multiple students (admin/teacher only)"""
    try:
        data = request.get_json()
        current_user_data = get_jwt_identity()
        
        # Validate required fields
        required_fields = ['grades']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'msg': f'Missing required field: {field}'}), 400
        
        grades_data = data['grades']
        if not isinstance(grades_data, list):
            return jsonify({'msg': 'grades must be a list'}), 400
        
        results = []
        for grade_data in grades_data:
            try:
                student_id = grade_data.get('student_id')
                
                # For teachers, validate access
                if current_user_data.get('role') == 'teacher':
                    if not validate_student_access(student_id, current_user_data):
                        results.append({
                            'student_id': student_id,
                            'status': 'error',
                            'message': 'Access forbidden'
                        })
                        continue
                
                # Create grade record
                grade = Grade(
                    student_id=student_id,
                    subject=grade_data['subject'],
                    assignment_type=grade_data['assignment_type'],
                    score=float(grade_data['score']),
                    max_score=float(grade_data['max_score']),
                    term=grade_data['term'],
                    academic_year=grade_data['academic_year'],
                    recorded_by=current_user_data['id'],
                    remarks=grade_data.get('remarks', '')
                )
                
                grade.calculate_percentage()
                db.session.add(grade)
                
                results.append({
                    'student_id': student_id,
                    'status': 'success',
                    'message': 'Grade created successfully'
                })
                
            except Exception as e:
                results.append({
                    'student_id': grade_data.get('student_id'),
                    'status': 'error',
                    'message': str(e)
                })
        
        db.session.commit()
        
        return jsonify({
            'msg': 'Bulk grade creation completed',
            'results': results
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error creating bulk grades: {str(e)}'}), 500

@grade_bp.route('/subjects', methods=['GET'])
@role_required('admin', 'teacher')
def get_subjects():
    """Get list of all subjects (admin/teacher only)"""
    try:
        subjects = db.session.query(Grade.subject).distinct().all()
        subject_list = [subject[0] for subject in subjects if subject[0]]
        return jsonify(sorted(subject_list))
    except Exception as e:
        return jsonify({'msg': f'Error retrieving subjects: {str(e)}'}), 500

@grade_bp.route('/class/<class_name>/grades', methods=['GET'])
@role_required('admin', 'teacher')
def get_class_grades(class_name):
    """Get grades for all students in a class"""
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
        
        # Get all students in the class
        students = Student.query.filter_by(class_name=class_name, is_active=True).all()
        student_ids = [student.id for student in students]
        
        # Get query parameters
        subject = request.args.get('subject')
        term = request.args.get('term')
        academic_year = request.args.get('academic_year')
        
        # Build grades query
        query = Grade.query.filter(Grade.student_id.in_(student_ids))
        
        if subject:
            query = query.filter_by(subject=subject)
        if term:
            query = query.filter_by(term=term)
        if academic_year:
            query = query.filter_by(academic_year=academic_year)
        
        grades = query.order_by(Grade.date_recorded.desc()).all()
        
        # Group grades by student
        student_grades = {}
        for student in students:
            student_grades[student.id] = {
                'student': student.to_dict(),
                'grades': []
            }
        
        for grade in grades:
            if grade.student_id in student_grades:
                student_grades[grade.student_id]['grades'].append(grade.to_dict())
        
        return jsonify(list(student_grades.values()))
    except Exception as e:
        return jsonify({'msg': f'Error retrieving class grades: {str(e)}'}), 500