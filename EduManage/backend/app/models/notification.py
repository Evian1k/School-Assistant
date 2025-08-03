from .. import db

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String(255))
    sent_at = db.Column(db.DateTime)
    channel = db.Column(db.String(20))  # sms/email/whatsapp
