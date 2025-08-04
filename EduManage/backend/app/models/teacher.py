from .. import db
from datetime import datetime

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    employee_id = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    subjects = db.Column(db.String(200))  # Comma-separated subjects
    qualification = db.Column(db.String(100))
    experience_years = db.Column(db.Integer)
    joining_date = db.Column(db.Date)
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    grades_entered = db.relationship('Grade', backref='teacher', lazy='dynamic')
    attendance_marked = db.relationship('Attendance', backref='teacher', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'employee_id': self.employee_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'subjects': self.subjects,
            'qualification': self.qualification,
            'experience_years': self.experience_years,
            'joining_date': self.joining_date.isoformat() if self.joining_date else None,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
