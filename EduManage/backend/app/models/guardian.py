from .. import db
from datetime import datetime

class Guardian(db.Model):
    __tablename__ = 'guardians'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    relationship = db.Column(db.String(50), nullable=False)  # father, mother, guardian, etc.
    occupation = db.Column(db.String(100))
    emergency_contact = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Note: children relationship is defined in Student model via backref
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'relationship': self.relationship,
            'occupation': self.occupation,
            'emergency_contact': self.emergency_contact,
            'is_active': self.is_active,
            'children_count': len(self.children) if self.children else 0
        }
