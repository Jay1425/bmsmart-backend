"""
Visitor routes for BMSmart backend.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.extensions import db
from app.models.visitor_model import Visitor
from app.models.building_model import Building
from app.models.user_model import User
from app.models.notification_model import Notification
from app.services.notification_service import NotificationService

visitor_bp = Blueprint('visitors', __name__, url_prefix='/visitors')


@visitor_bp.route('/entry', methods=['POST'])
def visitor_entry():
    """Record a visitor entry."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'phone', 'building_id']
        if not data or not all(data.get(field) for field in required_fields):
            return jsonify({'error': 'Name, phone, and building_id are required'}), 400
        
        # Check if building exists
        building = Building.query.get(data['building_id'])
        if not building:
            return jsonify({'error': 'Building not found'}), 404
        
        # Rate limiting: Prevent spam entries
        # Same phone + building cannot create more than 1 entry within 5 minutes
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        recent_entry = Visitor.query.filter(
            Visitor.phone == data['phone'],
            Visitor.building_id == data['building_id'],
            Visitor.entry_time >= five_minutes_ago
        ).first()
        
        if recent_entry:
            return jsonify({
                'error': 'Duplicate entry detected. Please wait at least 5 minutes before creating another entry.',
                'previous_entry_time': recent_entry.entry_time.isoformat()
            }), 429  # 429 Too Many Requests
        
        # Create new visitor entry (entry_time is set automatically by default)
        visitor = Visitor(
            name=data['name'],
            phone=data['phone'],
            flat_number=data.get('flat_number'),
            vehicle_number=data.get('vehicle_number'),
            photo_url=data.get('photo_url'),
            reason=data.get('reason'),
            building_id=data['building_id']
        )
        
        db.session.add(visitor)
        db.session.commit()
        
        # Send notification to resident if flat_number is provided
        notification_sent = False
        resident_notified = False
        if visitor.flat_number:
            # Find the specific resident with matching flat_number and building_id
            resident = User.query.filter_by(
                building_id=visitor.building_id,
                flat_number=visitor.flat_number,
                role='resident'
            ).first()
            
            if resident:
                try:
                    # Create notification in database
                    notification = Notification(
                        user_id=resident.id,
                        title="Visitor Arrived",
                        message=f"{visitor.name} is waiting at the gate for {visitor.flat_number}",
                        visitor_id=visitor.id
                    )
                    db.session.add(notification)
                    db.session.commit()
                    resident_notified = True
                    
                    # Send push notification if device token is available
                    if resident.device_token:
                        result = NotificationService.send_visitor_arrival_notification(
                            device_token=resident.device_token,
                            visitor_name=visitor.name,
                            flat_number=visitor.flat_number
                        )
                        if result.get('success'):
                            notification_sent = True
                
                except Exception as e:
                    # Log notification error but don't fail the visitor entry
                    print(f"Failed to send notification to resident {resident.id}: {str(e)}")
                    db.session.rollback()
            else:
                # No resident found for this flat_number - log warning but continue
                print(f"Warning: No resident found for flat {visitor.flat_number} in building {visitor.building_id}")
        
        return jsonify({
            'message': 'Visitor entry recorded successfully',
            'visitor': visitor.to_dict(),
            'notification_sent': notification_sent,
            'resident_notified': resident_notified
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@visitor_bp.route('/exit/<int:visitor_id>', methods=['POST'])
def visitor_exit(visitor_id):
    """Record a visitor exit."""
    try:
        visitor = Visitor.query.get(visitor_id)
        if not visitor:
            return jsonify({'error': 'Visitor not found'}), 404
        
        if visitor.exit_time:
            return jsonify({'error': 'Visitor has already exited'}), 400
        
        # Set exit time to current timestamp
        visitor.exit_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Visitor exit recorded successfully',
            'visitor': visitor.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@visitor_bp.route('', methods=['GET'])
def get_visitors():
    """Get all visitors."""
    try:
        visitors = Visitor.query.all()
        return jsonify({
            'visitors': [visitor.to_dict() for visitor in visitors]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visitor_bp.route('/building/<int:building_id>', methods=['GET'])
def get_visitors_by_building(building_id):
    """Get all visitors for a specific building."""
    try:
        visitors = Visitor.query.filter_by(building_id=building_id).all()
        return jsonify({
            'visitors': [visitor.to_dict() for visitor in visitors]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
