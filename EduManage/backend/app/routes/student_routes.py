from flask import Blueprint, request, jsonify
from ..models.student import Student
from .. import db
from flask_jwt_extended import jwt_required

student_bp = Blueprint('students', __name__)

@student_bp.route('/', methods=['GET'])
@jwt_required()
def get_students():
    students = Student.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'email': s.email, 'class_name': s.class_name} for s in students])

@student_bp.route('/', methods=['POST'])
@jwt_required()
def add_student():
    data = request.get_json()
    student = Student(
        name=data.get('name'),
        email=data.get('email'),
        class_name=data.get('class_name'),
        guardian_id=data.get('guardian_id')
    )
    db.session.add(student)
    db.session.commit()
    return jsonify({'msg': 'Student added successfully'})
