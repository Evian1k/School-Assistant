from .. import db
from datetime import datetime

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, default=100.0)
    grade_letter = db.Column(db.String(2))  # A, B, C, D, F
    term = db.Column(db.String(20), nullable=False)  # First Term, Second Term, etc.
    academic_year = db.Column(db.String(10), nullable=False)  # 2023-2024
    exam_type = db.Column(db.String(50))  # Mid-term, Final, Assignment
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_grade_letter(self):
        percentage = (self.score / self.max_score) * 100
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'teacher_id': self.teacher_id,
            'subject': self.subject,
            'score': self.score,
            'max_score': self.max_score,
            'grade_letter': self.grade_letter or self.calculate_grade_letter(),
            'term': self.term,
            'academic_year': self.academic_year,
            'exam_type': self.exam_type,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
