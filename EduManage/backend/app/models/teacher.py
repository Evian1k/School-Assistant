from .. import db
from datetime import datetime

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    teacher_id = db.Column(db.String(20), unique=True, nullable=False, index=True)  # Employee ID
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    subjects = db.Column(db.Text)  # JSON string of subjects taught
    classes_assigned = db.Column(db.Text)  # JSON string of classes
    qualification = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    hire_date = db.Column(db.Date, default=datetime.utcnow().date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'teacher_id': self.teacher_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'subjects': self.subjects,
            'classes_assigned': self.classes_assigned,
            'qualification': self.qualification,
            'experience_years': self.experience_years,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'is_active': self.is_active
        }
