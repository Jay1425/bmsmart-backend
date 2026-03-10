"""
AI-powered Visitor Behavior Analytics Service for BMSmart.

This service provides intelligent analysis of visitor patterns to detect:
- Frequent visitors (potential security risks)
- Late-night visitors (unusual activity)
- Risk scoring based on behavior patterns
"""
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from app.extensions import db
from app.models.visitor_model import Visitor


class VisitorAIService:
    """Service class for AI-powered visitor behavior analytics."""
    
    @staticmethod
    def detect_frequent_visitors(building_id, days=7, threshold=5):
        """
        Detect visitors who entered the building frequently in the last N days.
        
        Args:
            building_id (int): Building ID to analyze
            days (int): Number of days to look back (default: 7)
            threshold (int): Minimum visit count to be considered frequent (default: 5)
        
        Returns:
            list: List of frequent visitors with their visit counts
        """
        # Calculate date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days)
        
        # Query to group visitors by phone and count visits
        frequent_visitors = db.session.query(
            Visitor.name,
            Visitor.phone,
            func.count(Visitor.id).label('visit_count'),
            func.max(Visitor.entry_time).label('last_visit'),
            func.min(Visitor.entry_time).label('first_visit')
        ).filter(
            Visitor.building_id == building_id,
            Visitor.entry_time >= date_threshold
        ).group_by(
            Visitor.phone,
            Visitor.name
        ).having(
            func.count(Visitor.id) >= threshold
        ).order_by(
            func.count(Visitor.id).desc()
        ).all()
        
        # Format results
        result = []
        for visitor in frequent_visitors:
            result.append({
                'name': visitor.name,
                'phone': visitor.phone,
                'visits_last_week': visitor.visit_count,
                'last_visit': visitor.last_visit.isoformat() if visitor.last_visit else None,
                'first_visit': visitor.first_visit.isoformat() if visitor.first_visit else None
            })
        
        return result
    
    @staticmethod
    def detect_late_night_visitors(building_id, days=30):
        """
        Detect visitors who entered the building late at night (12 AM - 5 AM).
        
        Args:
            building_id (int): Building ID to analyze
            days (int): Number of days to look back (default: 30)
        
        Returns:
            list: List of late-night visitor entries
        """
        # Calculate date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days)
        
        # Query for late night entries (hour between 0 and 5)
        late_night_visitors = Visitor.query.filter(
            Visitor.building_id == building_id,
            Visitor.entry_time >= date_threshold
        ).all()
        
        # Filter by time (12 AM - 5 AM)
        result = []
        for visitor in late_night_visitors:
            entry_hour = visitor.entry_time.hour
            if 0 <= entry_hour < 5:  # Midnight to 5 AM
                result.append({
                    'id': visitor.id,
                    'name': visitor.name,
                    'phone': visitor.phone,
                    'flat_number': visitor.flat_number,
                    'entry_time': visitor.entry_time.isoformat(),
                    'entry_hour': entry_hour,
                    'reason': visitor.reason,
                    'approval_status': visitor.approval_status
                })
        
        # Sort by entry time (most recent first)
        result.sort(key=lambda x: x['entry_time'], reverse=True)
        
        return result
    
    @staticmethod
    def calculate_visitor_risk_score(phone, building_id=None):
        """
        Calculate risk score for a visitor based on behavior patterns.
        
        Risk factors:
        - Frequent visits (>5 in last 7 days): +30 points
        - Late night entries: +20 points per entry
        - No flat number specified: +15 points per entry
        - Rejected approvals: +25 points per rejection
        
        Args:
            phone (str): Visitor phone number
            building_id (int, optional): Limit analysis to specific building
        
        Returns:
            dict: Risk score and analysis details
        """
        risk_score = 0
        risk_factors = []
        
        # Base query
        query = Visitor.query.filter_by(phone=phone)
        if building_id:
            query = query.filter_by(building_id=building_id)
        
        # Get all visits for this phone number
        all_visits = query.all()
        total_visits = len(all_visits)
        
        if total_visits == 0:
            return {
                'phone': phone,
                'risk_score': 0,
                'risk_level': 'none',
                'total_visits': 0,
                'risk_factors': ['No visit history found']
            }
        
        # Factor 1: Frequent visits in last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_visits = [v for v in all_visits if v.entry_time >= seven_days_ago]
        recent_visit_count = len(recent_visits)
        
        if recent_visit_count > 5:
            risk_score += 30
            risk_factors.append(f'Frequent visitor: {recent_visit_count} visits in last 7 days')
        
        # Factor 2: Late night entries (12 AM - 5 AM)
        late_night_count = 0
        for visit in all_visits:
            if 0 <= visit.entry_time.hour < 5:
                late_night_count += 1
        
        if late_night_count > 0:
            risk_score += (late_night_count * 20)
            risk_factors.append(f'Late night entries: {late_night_count} times')
        
        # Factor 3: No flat number specified
        no_flat_count = sum(1 for v in all_visits if not v.flat_number)
        if no_flat_count > 0:
            risk_score += (no_flat_count * 15)
            risk_factors.append(f'No flat number specified: {no_flat_count} times')
        
        # Factor 4: Rejected approvals
        rejected_count = sum(1 for v in all_visits if v.approval_status == 'rejected')
        if rejected_count > 0:
            risk_score += (rejected_count * 25)
            risk_factors.append(f'Rejected approvals: {rejected_count} times')
        
        # Cap risk score at 100
        risk_score = min(risk_score, 100)
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = 'high'
        elif risk_score >= 40:
            risk_level = 'medium'
        elif risk_score >= 20:
            risk_level = 'low'
        else:
            risk_level = 'minimal'
        
        # Get visitor name from most recent visit
        most_recent = max(all_visits, key=lambda v: v.entry_time)
        
        return {
            'phone': phone,
            'name': most_recent.name,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'total_visits': total_visits,
            'recent_visits_7_days': recent_visit_count,
            'late_night_entries': late_night_count,
            'no_flat_entries': no_flat_count,
            'rejected_approvals': rejected_count,
            'risk_factors': risk_factors if risk_factors else ['No risk factors detected'],
            'last_visit': most_recent.entry_time.isoformat(),
            'buildings_visited': list(set(v.building_id for v in all_visits))
        }
    
    @staticmethod
    def get_building_analytics_summary(building_id, days=30):
        """
        Get comprehensive analytics summary for a building.
        
        Args:
            building_id (int): Building ID to analyze
            days (int): Number of days to look back (default: 30)
        
        Returns:
            dict: Analytics summary with various metrics
        """
        date_threshold = datetime.utcnow() - timedelta(days=days)
        
        # Get all visitors in time period
        visitors = Visitor.query.filter(
            Visitor.building_id == building_id,
            Visitor.entry_time >= date_threshold
        ).all()
        
        total_visits = len(visitors)
        unique_visitors = len(set(v.phone for v in visitors))
        
        # Count late night visits
        late_night = sum(1 for v in visitors if 0 <= v.entry_time.hour < 5)
        
        # Count visitors without flat numbers
        no_flat = sum(1 for v in visitors if not v.flat_number)
        
        # Count by approval status
        pending = sum(1 for v in visitors if v.approval_status == 'pending')
        approved = sum(1 for v in visitors if v.approval_status == 'approved')
        rejected = sum(1 for v in visitors if v.approval_status == 'rejected')
        
        # Average visits per day
        avg_visits_per_day = total_visits / days if days > 0 else 0
        
        return {
            'building_id': building_id,
            'analysis_period_days': days,
            'total_visits': total_visits,
            'unique_visitors': unique_visitors,
            'avg_visits_per_day': round(avg_visits_per_day, 2),
            'late_night_visits': late_night,
            'late_night_percentage': round((late_night / total_visits * 100), 2) if total_visits > 0 else 0,
            'no_flat_number': no_flat,
            'no_flat_percentage': round((no_flat / total_visits * 100), 2) if total_visits > 0 else 0,
            'pending_approvals': pending,
            'approved_visits': approved,
            'rejected_visits': rejected,
            'rejection_rate': round((rejected / total_visits * 100), 2) if total_visits > 0 else 0
        }
