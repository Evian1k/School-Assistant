from .. import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    student_id = db.Column(db.String(20), unique=True)  # School ID
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    class_name = db.Column(db.String(50))
    section = db.Column(db.String(10))
    admission_date = db.Column(db.Date, default=datetime.utcnow().date)
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(20))
    blood_group = db.Column(db.String(5))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    guardian_id = db.Column(db.Integer, db.ForeignKey('guardians.id'))
    grades = db.relationship('Grade', backref='student', lazy='dynamic')
    attendance_records = db.relationship('Attendance', backref='student', lazy='dynamic')
    fees = db.relationship('Fee', backref='student', lazy='dynamic')
    documents = db.relationship('Document', backref='student', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'class_name': self.class_name,
            'section': self.section,
            'admission_date': self.admission_date.isoformat() if self.admission_date else None,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'blood_group': self.blood_group,
            'is_active': self.is_active,
            'guardian_id': self.guardian_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
