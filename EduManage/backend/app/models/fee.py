from .. import db
from datetime import datetime

class Fee(db.Model):
    __tablename__ = 'fees'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    fee_type = db.Column(db.String(50), nullable=False)  # tuition, transport, lunch, activity, etc.
    amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, nullable=False)  # amount - discount
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue, partial
    due_date = db.Column(db.Date, nullable=False)
    paid_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))  # cash, bank_transfer, online, cheque
    transaction_id = db.Column(db.String(100))  # Payment gateway transaction ID
    receipt_number = db.Column(db.String(50), unique=True)
    term = db.Column(db.String(20), nullable=False)  # Term 1, Term 2, Annual
    academic_year = db.Column(db.String(10), nullable=False)  # 2024-2025
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Admin/cashier who processed
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    processed_by_user = db.relationship('User', foreign_keys=[processed_by], lazy=True)
    
    def calculate_final_amount(self):
        """Calculate final amount after discount"""
        self.final_amount = self.amount - self.discount
    
    def is_overdue(self):
        """Check if fee is overdue"""
        if self.status == 'pending' and self.due_date < datetime.utcnow().date():
            return True
        return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'fee_type': self.fee_type,
            'amount': self.amount,
            'discount': self.discount,
            'final_amount': self.final_amount,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'receipt_number': self.receipt_number,
            'term': self.term,
            'academic_year': self.academic_year,
            'processed_by': self.processed_by,
            'remarks': self.remarks,
            'is_overdue': self.is_overdue(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
