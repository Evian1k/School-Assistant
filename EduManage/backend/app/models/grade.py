from .. import db

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    subject = db.Column(db.String(100))
    score = db.Column(db.Float)
    term = db.Column(db.String(20))
    # Add more fields as needed
