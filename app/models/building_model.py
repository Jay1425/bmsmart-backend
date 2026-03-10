"""
Building model for BMSmart backend.
"""
from datetime import datetime
from app.extensions import db


class Building(db.Model):
    """Building model representing a building in the system."""
    
    __tablename__ = 'buildings'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    users = db.relationship('User', backref='building', lazy=True, cascade='all, delete-orphan')
    visitors = db.relationship('Visitor', backref='building', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert Building object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Building {self.name}>'
