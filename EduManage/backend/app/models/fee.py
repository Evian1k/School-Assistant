from .. import db

class Fee(db.Model):
    __tablename__ = 'fees'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    due_date = db.Column(db.Date)
    # Add more fields as needed
