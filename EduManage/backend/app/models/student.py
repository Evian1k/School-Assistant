from .. import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False, index=True)  # School ID
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    grade_level = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date)
    admission_date = db.Column(db.Date, default=datetime.utcnow().date)
    guardian_id = db.Column(db.Integer, db.ForeignKey('guardians.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    guardian = db.relationship('Guardian', backref='children', lazy=True)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    grades = db.relationship('Grade', backref='student', lazy=True, cascade='all, delete-orphan')
    fees = db.relationship('Fee', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'class_name': self.class_name,
            'grade_level': self.grade_level,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'admission_date': self.admission_date.isoformat() if self.admission_date else None,
            'guardian_id': self.guardian_id,
            'is_active': self.is_active
        }
