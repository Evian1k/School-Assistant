from .. import db
from datetime import datetime

class Fee(db.Model):
    __tablename__ = 'fees'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    fee_type = db.Column(db.String(50), nullable=False)  # Tuition, Library, Transport, etc.
    amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, paid, partial, overdue
    due_date = db.Column(db.Date, nullable=False)
    paid_date = db.Column(db.Date)
    academic_year = db.Column(db.String(10), nullable=False)
    term = db.Column(db.String(20))  # First Term, Second Term, etc.
    payment_method = db.Column(db.String(50))  # Cash, Bank Transfer, Online
    receipt_number = db.Column(db.String(50))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_balance(self):
        return self.amount - self.paid_amount

    def is_overdue(self):
        if self.due_date and datetime.now().date() > self.due_date:
            return self.status != 'paid'
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'fee_type': self.fee_type,
            'amount': self.amount,
            'paid_amount': self.paid_amount,
            'balance': self.get_balance(),
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'academic_year': self.academic_year,
            'term': self.term,
            'payment_method': self.payment_method,
            'receipt_number': self.receipt_number,
            'remarks': self.remarks,
            'is_overdue': self.is_overdue(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
