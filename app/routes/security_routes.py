"""
Security / Gate Management routes for BMSmart backend.
Routes for security staff to monitor and manage visitors.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app.extensions import db
from app.models.visitor_model import Visitor
from app.models.building_model import Building
from app.models.user_model import User

security_bp = Blueprint('security', __name__, url_prefix='/security')


@security_bp.route('/visitors/today/<int:building_id>', methods=['GET'])
@jwt_required()
def get_today_visitors(building_id):
    """
    Get all visitors who entered today for a specific building.
    
    Args:
        building_id (int): Building ID
    
    Returns:
        JSON: List of today's visitors
    """
    try:
        # Validate building exists
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Building not found'}), 404
        
        # Get start of today (midnight)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Query visitors who entered today
        visitors = Visitor.query.filter(
            Visitor.building_id == building_id,
            Visitor.entry_time >= today_start
        ).order_by(Visitor.entry_time.desc()).all()
        
        return jsonify({
            'building_id': building_id,
            'building_name': building.name,
            'date': today_start.date().isoformat(),
            'total_count': len(visitors),
            'visitors': [visitor.to_dict() for visitor in visitors]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@security_bp.route('/visitors/inside/<int:building_id>', methods=['GET'])
@jwt_required()
def get_visitors_inside(building_id):
    """
    Get all visitors currently inside the building.
    
    Logic: Visitors with entry_time but no exit_time
    
    Args:
        building_id (int): Building ID
    
    Returns:
        JSON: List of visitors currently inside
    """
    try:
        # Validate building exists
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Building not found'}), 404
        
        # Query visitors inside (no exit_time)
        visitors = Visitor.query.filter(
            Visitor.building_id == building_id,
            Visitor.exit_time.is_(None)
        ).order_by(Visitor.entry_time.desc()).all()
        
        return jsonify({
            'building_id': building_id,
            'building_name': building.name,
            'total_count': len(visitors),
            'visitors': [visitor.to_dict() for visitor in visitors]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@security_bp.route('/visitors/recent/<int:building_id>', methods=['GET'])
@jwt_required()
def get_recent_visitors(building_id):
    """
    Get the last 20 visitor entries for a specific building.
    
    Args:
        building_id (int): Building ID
    
    Returns:
        JSON: List of recent visitors (last 20)
    """
    try:
        # Validate building exists
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Building not found'}), 404
        
        # Query last 20 visitors
        visitors = Visitor.query.filter_by(
            building_id=building_id
        ).order_by(Visitor.entry_time.desc()).limit(20).all()
        
        return jsonify({
            'building_id': building_id,
            'building_name': building.name,
            'total_count': len(visitors),
            'visitors': [visitor.to_dict() for visitor in visitors]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@security_bp.route('/visitor/approve/<int:visitor_id>', methods=['POST'])
@jwt_required()
def approve_visitor(visitor_id):
    """
    Approve a visitor entry.
    
    Args:
        visitor_id (int): Visitor ID
    
    Returns:
        JSON: Success message and updated visitor details
    """
    try:
        # Get current user from JWT (convert string to int)
        current_user_id = int(get_jwt_identity())
        
        # Find visitor
        visitor = Visitor.query.get(visitor_id)
        if not visitor:
            return jsonify({'error': 'Visitor not found'}), 404
        
        # Check if already approved or rejected
        if visitor.approval_status in ['approved', 'rejected']:
            return jsonify({
                'error': f'Visitor already {visitor.approval_status}'
            }), 400
        
        # Update approval status
        visitor.approval_status = 'approved'
        visitor.approved_by = current_user_id
        visitor.approval_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Visitor approved successfully',
            'visitor': visitor.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@security_bp.route('/visitor/reject/<int:visitor_id>', methods=['POST'])
@jwt_required()
def reject_visitor(visitor_id):
    """
    Reject a visitor entry.
    
    Args:
        visitor_id (int): Visitor ID
    
    Returns:
        JSON: Success message and updated visitor details
    """
    try:
        # Get current user from JWT (convert string to int)
        current_user_id = int(get_jwt_identity())
        
        # Find visitor
        visitor = Visitor.query.get(visitor_id)
        if not visitor:
            return jsonify({'error': 'Visitor not found'}), 404
        
        # Check if already approved or rejected
        if visitor.approval_status in ['approved', 'rejected']:
            return jsonify({
                'error': f'Visitor already {visitor.approval_status}'
            }), 400
        
        # Update approval status
        visitor.approval_status = 'rejected'
        visitor.approved_by = current_user_id
        visitor.approval_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Visitor rejected successfully',
            'visitor': visitor.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@security_bp.route('/visitor/force-exit/<int:visitor_id>', methods=['POST'])
@jwt_required()
def force_exit_visitor(visitor_id):
    """
    Force exit a visitor (if they forgot to scan exit).
    
    Args:
        visitor_id (int): Visitor ID
    
    Returns:
        JSON: Success message and updated visitor details
    """
    try:
        # Find visitor
        visitor = Visitor.query.get(visitor_id)
        if not visitor:
            return jsonify({'error': 'Visitor not found'}), 404
        
        # Check if already exited
        if visitor.exit_time:
            return jsonify({
                'error': 'Visitor has already exited',
                'exit_time': visitor.exit_time.isoformat()
            }), 400
        
        # Set exit time to current timestamp
        visitor.exit_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Visitor exit recorded successfully (forced by security)',
            'visitor': visitor.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@security_bp.route('/visitors/pending/<int:building_id>', methods=['GET'])
@jwt_required()
def get_pending_visitors(building_id):
    """
    Get all visitors with pending approval status for a specific building.
    
    Args:
        building_id (int): Building ID
    
    Returns:
        JSON: List of pending visitors
    """
    try:
        # Validate building exists
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Building not found'}), 404
        
        # Query pending visitors
        visitors = Visitor.query.filter(
            Visitor.building_id == building_id,
            Visitor.approval_status == 'pending'
        ).order_by(Visitor.entry_time.desc()).all()
        
        return jsonify({
            'building_id': building_id,
            'building_name': building.name,
            'total_count': len(visitors),
            'visitors': [visitor.to_dict() for visitor in visitors]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@security_bp.route('/visitors/stats/<int:building_id>', methods=['GET'])
@jwt_required()
def get_visitor_stats(building_id):
    """
    Get visitor statistics for a building.
    
    Args:
        building_id (int): Building ID
    
    Returns:
        JSON: Visitor statistics (total, inside, pending, approved, rejected)
    """
    try:
        # Validate building exists
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Building not found'}), 404
        
        # Get today's start time
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count visitors by status
        total_today = Visitor.query.filter(
            Visitor.building_id == building_id,
            Visitor.entry_time >= today_start
        ).count()
        
        inside = Visitor.query.filter(
            Visitor.building_id == building_id,
            Visitor.exit_time.is_(None)
        ).count()
        
        pending = Visitor.query.filter(
            Visitor.building_id == building_id,
            Visitor.approval_status == 'pending'
        ).count()
        
        approved = Visitor.query.filter(
            Visitor.building_id == building_id,
            Visitor.approval_status == 'approved'
        ).count()
        
        rejected = Visitor.query.filter(
            Visitor.building_id == building_id,
            Visitor.approval_status == 'rejected'
        ).count()
        
        return jsonify({
            'building_id': building_id,
            'building_name': building.name,
            'stats': {
                'total_today': total_today,
                'currently_inside': inside,
                'pending_approval': pending,
                'approved': approved,
                'rejected': rejected
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
