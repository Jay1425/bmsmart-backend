"""
AI-powered Visitor Analytics Routes for BMSmart backend.

Provides intelligent visitor behavior analysis endpoints for security monitoring.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.visitor_ai_service import VisitorAIService
from app.models.building_model import Building

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')


@ai_bp.route('/frequent-visitors/<int:building_id>', methods=['GET'])
@jwt_required()
def get_frequent_visitors(building_id):
    """
    Get list of frequent visitors for a building.
    
    Detects visitors who have entered the building more than 5 times in the last 7 days.
    
    Args:
        building_id: ID of the building to analyze
    
    Query Parameters:
        days (optional): Number of days to look back (default: 7)
        threshold (optional): Minimum visit count to be considered frequent (default: 5)
    
    Returns:
        JSON response with list of frequent visitors
    """
    try:
        # Check if building exists
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Building not found'}), 404
        
        # Get query parameters
        days = request.args.get('days', 7, type=int)
        threshold = request.args.get('threshold', 5, type=int)
        
        # Get frequent visitors
        frequent_visitors = VisitorAIService.detect_frequent_visitors(
            building_id=building_id,
            days=days,
            threshold=threshold
        )
        
        return jsonify({
            'building_id': building_id,
            'building_name': building.name,
            'analysis_period_days': days,
            'threshold': threshold,
            'frequent_visitors': frequent_visitors,
            'total_count': len(frequent_visitors)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/late-night-visitors/<int:building_id>', methods=['GET'])
@jwt_required()
def get_late_night_visitors(building_id):
    """
    Get list of late-night visitors for a building.
    
    Detects visitors who entered between 12 AM and 5 AM.
    
    Args:
        building_id: ID of the building to analyze
    
    Query Parameters:
        days (optional): Number of days to look back (default: 30)
    
    Returns:
        JSON response with list of late-night visitor entries
    """
    try:
        # Check if building exists
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Building not found'}), 404
        
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        
        # Get late night visitors
        late_night_visitors = VisitorAIService.detect_late_night_visitors(
            building_id=building_id,
            days=days
        )
        
        return jsonify({
            'building_id': building_id,
            'building_name': building.name,
            'analysis_period_days': days,
            'late_night_visitors': late_night_visitors,
            'total_count': len(late_night_visitors)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/visitor-risk/<phone>', methods=['GET'])
@jwt_required()
def get_visitor_risk(phone):
    """
    Calculate risk score for a visitor based on behavior patterns.
    
    Risk factors include:
    - Frequent visits (>5 in last 7 days)
    - Late night entries (12 AM - 5 AM)
    - No flat number specified
    - Rejected approvals
    
    Args:
        phone: Phone number of the visitor to analyze
    
    Query Parameters:
        building_id (optional): Limit analysis to specific building
    
    Returns:
        JSON response with risk score (0-100) and risk level
    """
    try:
        # Get query parameters
        building_id = request.args.get('building_id', type=int)
        
        # Calculate risk score
        risk_analysis = VisitorAIService.calculate_visitor_risk_score(
            phone=phone,
            building_id=building_id
        )
        
        return jsonify(risk_analysis), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/building-analytics/<int:building_id>', methods=['GET'])
@jwt_required()
def get_building_analytics(building_id):
    """
    Get comprehensive analytics summary for a building.
    
    Provides overview of visitor patterns, late night activity, approval rates, etc.
    
    Args:
        building_id: ID of the building to analyze
    
    Query Parameters:
        days (optional): Number of days to look back (default: 30)
    
    Returns:
        JSON response with analytics summary
    """
    try:
        # Check if building exists
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Building not found'}), 404
        
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        
        # Get analytics summary
        analytics = VisitorAIService.get_building_analytics_summary(
            building_id=building_id,
            days=days
        )
        
        # Add building name
        analytics['building_name'] = building.name
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/high-risk-visitors/<int:building_id>', methods=['GET'])
@jwt_required()
def get_high_risk_visitors(building_id):
    """
    Get list of high-risk visitors for a building.
    
    Identifies visitors with risk score >= 70.
    
    Args:
        building_id: ID of the building to analyze
    
    Query Parameters:
        days (optional): Number of days to look back (default: 30)
        min_risk_score (optional): Minimum risk score to include (default: 70)
    
    Returns:
        JSON response with list of high-risk visitors
    """
    try:
        # Check if building exists
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Building not found'}), 404
        
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        min_risk_score = request.args.get('min_risk_score', 70, type=int)
        
        # Get frequent visitors first (potential high-risk candidates)
        frequent_visitors = VisitorAIService.detect_frequent_visitors(
            building_id=building_id,
            days=days,
            threshold=1  # Get all visitors
        )
        
        # Calculate risk score for each
        high_risk_visitors = []
        for visitor in frequent_visitors:
            risk_analysis = VisitorAIService.calculate_visitor_risk_score(
                phone=visitor['phone'],
                building_id=building_id
            )
            
            if risk_analysis['risk_score'] >= min_risk_score:
                high_risk_visitors.append(risk_analysis)
        
        # Sort by risk score (highest first)
        high_risk_visitors.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return jsonify({
            'building_id': building_id,
            'building_name': building.name,
            'analysis_period_days': days,
            'min_risk_score': min_risk_score,
            'high_risk_visitors': high_risk_visitors,
            'total_count': len(high_risk_visitors)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
