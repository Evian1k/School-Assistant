from .. import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # present/absent
