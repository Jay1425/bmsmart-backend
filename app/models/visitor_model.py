"""
Visitor model for BMSmart backend.
"""
from datetime import datetime
from app.extensions import db


class Visitor(db.Model):
    """Visitor model representing visitors in the system."""
    
    __tablename__ = 'visitors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    flat_number = db.Column(db.String(50), nullable=True)
    vehicle_number = db.Column(db.String(50), nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)
    reason = db.Column(db.String(500), nullable=True)
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'), nullable=False)
    entry_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    exit_time = db.Column(db.DateTime, nullable=True)
    
    # Security approval fields
    approval_status = db.Column(db.String(20), default='pending', nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approval_time = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """Convert Visitor object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'flat_number': self.flat_number,
            'vehicle_number': self.vehicle_number,
            'photo_url': self.photo_url,
            'reason': self.reason,
            'building_id': self.building_id,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'approval_status': self.approval_status,
            'approved_by': self.approved_by,
            'approval_time': self.approval_time.isoformat() if self.approval_time else None
        }
    
    def __repr__(self):
        return f'<Visitor {self.name} - {self.phone}>'
