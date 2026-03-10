"""
Building routes for BMSmart backend.
"""
from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
import qrcode
from app.extensions import db
from app.models.building_model import Building

building_bp = Blueprint('buildings', __name__, url_prefix='/buildings')


@building_bp.route('/create', methods=['POST'])
def create_building():
    """Create a new building."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('name') or not data.get('address') or not data.get('city'):
            return jsonify({'error': 'Name, address, and city are required'}), 400
        
        # Create new building
        building = Building(
            name=data['name'],
            address=data['address'],
            city=data['city']
        )
        
        db.session.add(building)
        db.session.commit()
        
        return jsonify({
            'message': 'Building created successfully',
            'building': building.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@building_bp.route('', methods=['GET'])
def get_buildings():
    """Get all buildings."""
    try:
        buildings = Building.query.all()
        return jsonify({
            'buildings': [building.to_dict() for building in buildings]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@building_bp.route('/<int:building_id>/entry-url', methods=['GET'])
def get_building_entry_url(building_id):
    """Get the QR entry URL for a building."""
    try:
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Building not found'}), 404
        
        return jsonify({
            'building_id': building_id,
            'entry_url': f'/visitor/entry/{building_id}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@building_bp.route('/<int:building_id>/qr', methods=['GET'])
def generate_building_qr(building_id):
    """Generate QR code for building visitor entry."""
    try:
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Building not found'}), 404
        
        # Generate the visitor entry URL
        entry_url = f'http://localhost:5000/visitor/entry/{building_id}'
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(entry_url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
