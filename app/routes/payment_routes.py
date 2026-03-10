"""
Payment routes for BMSmart backend.
"""
from flask import Blueprint, request, jsonify, current_app
import razorpay
import hmac
import hashlib
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.payment_model import Payment
from app.models.user_model import User

payment_bp = Blueprint('payments', __name__, url_prefix='/payments')


@payment_bp.route('/create', methods=['POST'])
def create_payment():
    """Create a new payment."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'amount', 'purpose']
        if not data or not all(data.get(field) for field in required_fields):
            return jsonify({'error': 'user_id, amount, and purpose are required'}), 400
        
        # Create new payment
        payment = Payment(
            user_id=data['user_id'],
            amount=data['amount'],
            purpose=data['purpose'],
            status=data.get('status', 'pending')
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'message': 'Payment created successfully',
            'payment': payment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payment_bp.route('', methods=['GET'])
def get_payments():
    """Get all payments."""
    try:
        payments = Payment.query.all()
        return jsonify({
            'payments': [payment.to_dict() for payment in payments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/user/<int:user_id>', methods=['GET'])
def get_payments_by_user(user_id):
    """Get all payments for a specific user."""
    try:
        payments = Payment.query.filter_by(user_id=user_id).all()
        return jsonify({
            'payments': [payment.to_dict() for payment in payments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/create-order', methods=['POST'])
@jwt_required()
def create_razorpay_order():
    """Create a Razorpay order for payment."""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('amount') or not data.get('purpose'):
            return jsonify({'error': 'Amount and purpose are required'}), 400
        
        # Verify user exists
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Convert amount to paise (Razorpay uses smallest currency unit)
        amount_in_paise = int(float(data['amount']) * 100)
        
        # Initialize Razorpay client
        razorpay_client = razorpay.Client(
            auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET'])
        )
        
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': 1
        })
        
        # Create payment record in database
        payment = Payment(
            user_id=current_user_id,
            amount=data['amount'],
            purpose=data['purpose'],
            status='pending',
            razorpay_order_id=razorpay_order['id']
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'message': 'Razorpay order created successfully',
            'order_id': razorpay_order['id'],
            'amount': data['amount'],
            'currency': 'INR',
            'payment_id': payment.id,
            'razorpay_key': current_app.config['RAZORPAY_KEY_ID']
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_payment():
    """Verify Razorpay payment signature and update payment status."""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
        if not data or not all(data.get(field) for field in required_fields):
            return jsonify({'error': 'razorpay_order_id, razorpay_payment_id, and razorpay_signature are required'}), 400
        
        # Find payment record
        payment = Payment.query.filter_by(
            razorpay_order_id=data['razorpay_order_id'],
            user_id=current_user_id
        ).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Verify signature
        razorpay_secret = current_app.config['RAZORPAY_KEY_SECRET']
        
        # Create signature
        message = f"{data['razorpay_order_id']}|{data['razorpay_payment_id']}"
        generated_signature = hmac.new(
            razorpay_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        if generated_signature != data['razorpay_signature']:
            payment.status = 'failed'
            db.session.commit()
            return jsonify({'error': 'Invalid signature', 'status': 'failed'}), 400
        
        # Signature is valid - update payment
        payment.razorpay_payment_id = data['razorpay_payment_id']
        payment.razorpay_signature = data['razorpay_signature']
        payment.status = 'paid'
        payment.payment_method = data.get('payment_method', 'unknown')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment verified successfully',
            'status': 'paid',
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
