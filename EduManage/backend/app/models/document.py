from .. import db

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_name = db.Column(db.String(255))
    file_url = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime)
