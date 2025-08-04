from .. import db
from datetime import datetime

class Guardian(db.Model):
    __tablename__ = 'guardians'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    relationship = db.Column(db.String(50))  # Father, Mother, Guardian
    occupation = db.Column(db.String(100))
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(20))
    is_primary = db.Column(db.Boolean, default=False)  # Primary guardian
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='guardian', lazy='dynamic')
    notifications = db.relationship('Notification', backref='guardian', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'relationship': self.relationship,
            'occupation': self.occupation,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'is_primary': self.is_primary,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'students_count': self.students.count()
        }
