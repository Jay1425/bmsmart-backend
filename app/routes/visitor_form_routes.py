"""
Public visitor form routes for BMSmart backend.
Routes for anonymous visitors to access entry forms via QR codes.
"""
import os
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.building_model import Building
from app.models.visitor_model import Visitor

visitor_form_bp = Blueprint('visitor_form', __name__, url_prefix='/visitor')

# Configuration for file uploads
UPLOAD_FOLDER = 'app/static/uploads/visitor_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_photo(photo_file, visitor_name):
    """Save uploaded photo and return the file path."""
    if not photo_file or photo_file.filename == '':
        return None
    
    if not allowed_file(photo_file.filename):
        return None
    
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    original_filename = secure_filename(photo_file.filename)
    extension = original_filename.rsplit('.', 1)[1].lower()
    safe_name = secure_filename(visitor_name.replace(' ', '_')[:30])
    filename = f"{safe_name}_{timestamp}.{extension}"
    
    # Save file
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    photo_file.save(file_path)
    
    # Return relative path for database storage
    return f"/static/uploads/visitor_photos/{filename}"


@visitor_form_bp.route('/form/<int:building_id>', methods=['GET', 'POST'])
def visitor_form(building_id):
    """
    GET: Render visitor entry form
    POST: Process form submission and save visitor entry
    """
    # Validate building exists
    building = Building.query.get(building_id)
    if not building:
        return render_template('visitor_form.html', 
                             building={'name': 'Unknown', 'id': building_id},
                             error='Building not found'), 404
    
    if request.method == 'GET':
        # Render the form
        return render_template('visitor_form.html', building=building)
    
    # POST request - process form submission
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        flat_number = request.form.get('flat_number', '').strip()
        reason = request.form.get('reason', '').strip()
        vehicle_number = request.form.get('vehicle_number', '').strip()
        
        # Validate required fields
        if not name or not phone or not reason:
            return render_template('visitor_form.html',
                                 building=building,
                                 error='Please fill in all required fields'), 400
        
        # Handle photo upload
        photo_url = None
        if 'photo' in request.files:
            photo_file = request.files['photo']
            photo_url = save_uploaded_photo(photo_file, name)
        
        # Create new visitor entry
        visitor = Visitor(
            name=name,
            phone=phone,
            flat_number=flat_number if flat_number else None,
            reason=reason,
            vehicle_number=vehicle_number if vehicle_number else None,
            photo_url=photo_url,
            building_id=building_id
        )
        
        db.session.add(visitor)
        db.session.commit()
        
        # Redirect to success page
        return redirect(url_for('visitor_form.visitor_success', 
                              visitor_id=visitor.id,
                              building_id=building_id))
    
    except Exception as e:
        db.session.rollback()
        return render_template('visitor_form.html',
                             building=building,
                             error=f'An error occurred: {str(e)}'), 500


@visitor_form_bp.route('/success', methods=['GET'])
def visitor_success():
    """Display success page after visitor entry."""
    visitor_id = request.args.get('visitor_id', type=int)
    building_id = request.args.get('building_id', type=int)
    
    if not visitor_id or not building_id:
        return "Invalid request", 400
    
    # Get visitor and building information
    visitor = Visitor.query.get(visitor_id)
    building = Building.query.get(building_id)
    
    if not visitor or not building:
        return "Visitor or building not found", 404
    
    # Format entry time for display
    entry_time = visitor.entry_time.strftime('%B %d, %Y at %I:%M %p')
    
    return render_template('visitor_success.html',
                         visitor=visitor,
                         building=building,
                         entry_time=entry_time)
