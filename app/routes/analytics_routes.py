"""
Analytics routes for BMSmart backend.
"""
from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from app.extensions import db
from app.models.visitor_model import Visitor
from app.models.building_model import Building

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/visitors/<int:building_id>', methods=['GET'])
def get_visitor_analytics(building_id):
    """Get visitor analytics for a building."""
    try:
        # Check if building exists
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Building not found'}), 404
        
        # Get current time and calculate date boundaries
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        week_start = today_start - timedelta(days=now.weekday())  # Monday of current week
        
        # Count visitors today
        visitors_today = Visitor.query.filter(
            Visitor.building_id == building_id,
            Visitor.entry_time >= today_start
        ).count()
        
        # Count visitors this week
        visitors_this_week = Visitor.query.filter(
            Visitor.building_id == building_id,
            Visitor.entry_time >= week_start
        ).count()
        
        # Count visitors currently inside (no exit_time)
        visitors_inside = Visitor.query.filter(
            Visitor.building_id == building_id,
            Visitor.exit_time == None
        ).count()
        
        return jsonify({
            'today': visitors_today,
            'this_week': visitors_this_week,
            'inside': visitors_inside
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
