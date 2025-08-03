from .. import db

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    class_name = db.Column(db.String(50))
    guardian_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # Add more fields as needed
