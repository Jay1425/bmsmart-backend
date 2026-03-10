"""
Complaint routes for BMSmart backend.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.complaint_model import Complaint

complaint_bp = Blueprint('complaints', __name__, url_prefix='/complaints')


@complaint_bp.route('/create', methods=['POST'])
@jwt_required()
def create_complaint():
    """Create a new complaint. (JWT Protected)"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description']
        if not data or not all(data.get(field) for field in required_fields):
            return jsonify({'error': 'title and description are required'}), 400
        
        # Create new complaint using logged-in user's ID
        complaint = Complaint(
            user_id=current_user_id,
            title=data['title'],
            description=data['description'],
            status=data.get('status', 'open')
        )
        
        db.session.add(complaint)
        db.session.commit()
        
        return jsonify({
            'message': 'Complaint created successfully',
            'complaint': complaint.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@complaint_bp.route('', methods=['GET'])
@jwt_required()
def get_complaints():
    """Get all complaints. (JWT Protected)"""
    try:
        complaints = Complaint.query.all()
        return jsonify({
            'complaints': [complaint.to_dict() for complaint in complaints]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@complaint_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_complaints_by_user(user_id):
    """Get all complaints for a specific user. (JWT Protected)"""
    try:
        complaints = Complaint.query.filter_by(user_id=user_id).all()
        return jsonify({
            'complaints': [complaint.to_dict() for complaint in complaints]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
