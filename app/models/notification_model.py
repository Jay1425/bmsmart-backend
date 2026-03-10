"""
Notification model for BMSmart backend.
"""
from datetime import datetime
from app.extensions import db


class Notification(db.Model):
    """Notification model representing push notifications in the system."""
    
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='notifications', lazy=True)
    visitor = db.relationship('Visitor', backref='notifications', lazy=True)
    
    def to_dict(self):
        """Convert Notification object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'visitor_id': self.visitor_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_read': self.is_read
        }
    
    def __repr__(self):
        return f'<Notification {self.title} for User {self.user_id}>'
