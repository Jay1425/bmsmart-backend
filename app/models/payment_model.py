"""
Payment model for BMSmart backend.
"""
from datetime import datetime
from app.extensions import db


class Payment(db.Model):
    """Payment model representing payments in the system."""
    
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending/paid/failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Razorpay fields
    razorpay_order_id = db.Column(db.String(255), nullable=True)
    razorpay_payment_id = db.Column(db.String(255), nullable=True)
    razorpay_signature = db.Column(db.String(255), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)  # card/upi/netbanking
    
    def to_dict(self):
        """Convert Payment object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'purpose': self.purpose,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'razorpay_order_id': self.razorpay_order_id,
            'razorpay_payment_id': self.razorpay_payment_id,
            'payment_method': self.payment_method
        }
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.amount} ({self.status})>'
