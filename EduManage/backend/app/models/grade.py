from .. import db
from datetime import datetime

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    assignment_type = db.Column(db.String(50), nullable=False)  # exam, quiz, assignment, project
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False, default=100)
    percentage = db.Column(db.Float)  # Auto-calculated
    grade_letter = db.Column(db.String(5))  # A, B, C, D, F
    term = db.Column(db.String(20), nullable=False)  # Term 1, Term 2, Final
    academic_year = db.Column(db.String(10), nullable=False)  # 2024-2025
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Teacher
    date_recorded = db.Column(db.Date, default=datetime.utcnow().date)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recorded_by_user = db.relationship('User', foreign_keys=[recorded_by], lazy=True)
    
    def calculate_percentage(self):
        """Calculate percentage and grade letter"""
        if self.max_score > 0:
            self.percentage = round((self.score / self.max_score) * 100, 2)
            # Grade letter calculation
            if self.percentage >= 90:
                self.grade_letter = 'A'
            elif self.percentage >= 80:
                self.grade_letter = 'B'
            elif self.percentage >= 70:
                self.grade_letter = 'C'
            elif self.percentage >= 60:
                self.grade_letter = 'D'
            else:
                self.grade_letter = 'F'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'subject': self.subject,
            'assignment_type': self.assignment_type,
            'score': self.score,
            'max_score': self.max_score,
            'percentage': self.percentage,
            'grade_letter': self.grade_letter,
            'term': self.term,
            'academic_year': self.academic_year,
            'recorded_by': self.recorded_by,
            'date_recorded': self.date_recorded.isoformat() if self.date_recorded else None,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
