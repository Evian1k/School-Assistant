from .. import db
from datetime import datetime

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # report_card, certificate, id_card, photo, medical
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # File size in bytes
    mime_type = db.Column(db.String(100))
    academic_year = db.Column(db.String(10))
    term = db.Column(db.String(20))
    is_public = db.Column(db.Boolean, default=False)  # Whether accessible by student/parent
    access_level = db.Column(db.String(20), default='private')  # private, student_only, parent_access, public
    description = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='documents', lazy=True)
    uploader = db.relationship('User', foreign_keys=[uploaded_by], lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'uploaded_by': self.uploaded_by,
            'document_type': self.document_type,
            'title': self.title,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'academic_year': self.academic_year,
            'term': self.term,
            'is_public': self.is_public,
            'access_level': self.access_level,
            'description': self.description,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None
        }
