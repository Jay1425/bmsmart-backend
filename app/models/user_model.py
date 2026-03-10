"""
User model for BMSmart backend.
"""
from datetime import datetime
from app.extensions import db


class User(db.Model):
    """User model representing users in the system."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='resident')  # admin/resident/security
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'), nullable=False)
    flat_number = db.Column(db.String(20), nullable=True)  # Apartment/flat number (e.g., "A-402", "B-101")
    device_token = db.Column(db.String(500), nullable=True)  # FCM device token for push notifications
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    payments = db.relationship('Payment', backref='user', lazy=True, cascade='all, delete-orphan')
    complaints = db.relationship('Complaint', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_password=False):
        """Convert User object to dictionary."""
        user_dict = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'building_id': self.building_id,
            'flat_number': self.flat_number,
            'device_token': self.device_token,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_password:
            user_dict['password'] = self.password
        return user_dict
    
    def __repr__(self):
        return f'<User {self.name} ({self.email})>'
