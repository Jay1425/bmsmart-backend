"""
Notification routes for BMSmart backend.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user_model import User
from app.models.notification_model import Notification

notification_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@notification_bp.route('/register-device', methods=['POST'])
@jwt_required()
def register_device():
    """
    Register or update FCM device token for authenticated user.
    
    Request Body:
        {
            "device_token": "firebase_device_token_string"
        }
    
    Returns:
        JSON response with success message
    """
    try:
        # Get current user from JWT token
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get device token from request
        data = request.get_json()
        if not data or not data.get('device_token'):
            return jsonify({'error': 'device_token is required'}), 400
        
        # Update user's device token
        user.device_token = data['device_token']
        db.session.commit()
        
        return jsonify({
            'message': 'Device token registered successfully',
            'user_id': user.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_notifications():
    """
    Get all notifications for the authenticated user.
    
    Query Parameters:
        unread_only (optional): Set to 'true' to get only unread notifications
        limit (optional): Maximum number of notifications to return (default: 50)
    
    Returns:
        JSON response with list of notifications
    """
    try:
        # Get current user from JWT token
        current_user_id = int(get_jwt_identity())
        
        # Build query
        query = Notification.query.filter_by(user_id=current_user_id)
        
        # Filter by read status if requested
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        if unread_only:
            query = query.filter_by(is_read=False)
        
        # Apply limit
        limit = request.args.get('limit', 50, type=int)
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'notifications': [notification.to_dict() for notification in notifications],
            'total': len(notifications)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/read/<int:notification_id>', methods=['POST'])
@jwt_required()
def mark_notification_as_read(notification_id):
    """
    Mark a notification as read.
    
    Args:
        notification_id: ID of the notification to mark as read
    
    Returns:
        JSON response with success message
    """
    try:
        # Get current user from JWT token
        current_user_id = int(get_jwt_identity())
        
        # Get notification
        notification = Notification.query.get(notification_id)
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        # Verify notification belongs to current user
        if notification.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized access to notification'}), 403
        
        # Mark as read
        notification.is_read = True
        db.session.commit()
        
        return jsonify({
            'message': 'Notification marked as read',
            'notification': notification.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_notifications_as_read():
    """
    Mark all notifications as read for the authenticated user.
    
    Returns:
        JSON response with count of notifications marked as read
    """
    try:
        # Get current user from JWT token
        current_user_id = int(get_jwt_identity())
        
        # Update all unread notifications for this user
        unread_notifications = Notification.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).all()
        
        count = len(unread_notifications)
        for notification in unread_notifications:
            notification.is_read = True
        
        db.session.commit()
        
        return jsonify({
            'message': f'{count} notification(s) marked as read',
            'count': count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
