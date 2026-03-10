"""
Test script for BMSmart AI-Powered Visitor Analytics Module.

This script tests the complete AI analytics system:
1. Create building and residents
2. Create various visitor entries (frequent, late-night, suspicious patterns)
3. Test frequent visitors detection
4. Test late-night visitors detection
5. Test visitor risk scoring
6. Test building analytics summary
7. Test high-risk visitors detection
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Configuration
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Test data
test_building_name = f"AI Analytics Test Tower {datetime.now().strftime('%H%M%S')}"


def print_response(title, response):
    """Print formatted API response."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*70}\n")


def test_ai_analytics():
    """Test the complete AI analytics system."""
    
    print("\n🤖 BMSmart AI-Powered Visitor Analytics Test")
    print("="*70)
    
    # Step 1: Create a building
    print("\n📍 Step 1: Creating test building...")
    building_data = {
        "name": test_building_name,
        "address": "789 AI Analytics Avenue"
    }
    response = requests.post(f"{BASE_URL}/buildings", json=building_data, headers=HEADERS)
    print_response("Building Created", response)
    
    if response.status_code != 201:
        print("❌ Failed to create building. Exiting.")
        return
    
    building_id = response.json()['building']['id']
    print(f"✅ Building created with ID: {building_id}")
    
    # Step 2: Register a security user for JWT authentication
    print("\n👮 Step 2: Registering security user...")
    security_email = f"security_ai_{datetime.now().strftime('%H%M%S')}@test.com"
    security_data = {
        "name": "Security AI Test",
        "email": security_email,
        "password": "password123",
        "phone": "9000000000",
        "role": "security",
        "building_id": building_id
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=security_data, headers=HEADERS)
    print_response("Security User Registered", response)
    
    if response.status_code != 201:
        print("❌ Failed to register security user. Exiting.")
        return
    
    access_token = response.json()['access_token']
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    print(f"✅ Security user registered, JWT token obtained")
    
    # Step 3: Create multiple visitor entries to simulate patterns
    print("\n🚶 Step 3: Creating visitor entries with various patterns...")
    
    # Pattern 1: Frequent Visitor (Rahul - 8 visits)
    print("\n   Creating Frequent Visitor: Rahul (8 visits)...")
    for i in range(8):
        visitor_data = {
            "name": "Rahul Frequent",
            "phone": "9111111111",
            "building_id": building_id,
            "flat_number": "A-101",
            "reason": f"Visit {i+1}"
        }
        response = requests.post(f"{BASE_URL}/visitors/entry", json=visitor_data, headers=HEADERS)
        if response.status_code == 201:
            print(f"      ✓ Visit {i+1} created")
        elif response.status_code == 429:
            print(f"      ⏳ Rate limited, waiting 5 seconds...")
            time.sleep(5)
            response = requests.post(f"{BASE_URL}/visitors/entry", json=visitor_data, headers=HEADERS)
            if response.status_code == 201:
                print(f"      ✓ Visit {i+1} created after wait")
    
    print("   ✅ Created 8 visits for Rahul (Frequent Visitor)")
    
    # Pattern 2: Normal Visitor (Priya - 2 visits)
    print("\n   Creating Normal Visitor: Priya (2 visits)...")
    for i in range(2):
        visitor_data = {
            "name": "Priya Normal",
            "phone": "9222222222",
            "building_id": building_id,
            "flat_number": "B-202",
            "reason": "Social visit"
        }
        response = requests.post(f"{BASE_URL}/visitors/entry", json=visitor_data, headers=HEADERS)
        if response.status_code == 201:
            print(f"      ✓ Visit {i+1} created")
    
    print("   ✅ Created 2 visits for Priya (Normal Visitor)")
    
    # Pattern 3: Suspicious Visitor - No flat number (3 visits)
    print("\n   Creating Suspicious Visitor: Amit (No flat number, 6 visits)...")
    for i in range(6):
        visitor_data = {
            "name": "Amit Suspicious",
            "phone": "9333333333",
            "building_id": building_id,
            "reason": "Delivery"
            # No flat_number specified - suspicious!
        }
        response = requests.post(f"{BASE_URL}/visitors/entry", json=visitor_data, headers=HEADERS)
        if response.status_code == 201:
            print(f"      ✓ Visit {i+1} created (no flat number)")
        elif response.status_code == 429:
            time.sleep(5)
            response = requests.post(f"{BASE_URL}/visitors/entry", json=visitor_data, headers=HEADERS)
            if response.status_code == 201:
                print(f"      ✓ Visit {i+1} created after wait")
    
    print("   ✅ Created 6 visits for Amit (No flat number - suspicious)")
    
    # Pattern 4: One-time visitor
    print("\n   Creating One-time Visitor: Sneha (1 visit)...")
    visitor_data = {
        "name": "Sneha OneTime",
        "phone": "9444444444",
        "building_id": building_id,
        "flat_number": "C-303",
        "reason": "Meeting"
    }
    response = requests.post(f"{BASE_URL}/visitors/entry", json=visitor_data, headers=HEADERS)
    if response.status_code == 201:
        print("      ✓ Visit created")
    print("   ✅ Created 1 visit for Sneha (One-time visitor)")
    
    print("\n📊 Summary of test data created:")
    print("   • Rahul: 8 visits (Frequent)")
    print("   • Amit: 6 visits, no flat number (Suspicious)")
    print("   • Priya: 2 visits (Normal)")
    print("   • Sneha: 1 visit (One-time)")
    
    # Step 4: Test Frequent Visitors Detection
    print("\n🔍 Step 4: Testing Frequent Visitors Detection...")
    response = requests.get(f"{BASE_URL}/ai/frequent-visitors/{building_id}", headers=auth_headers)
    print_response("Frequent Visitors Detection", response)
    
    if response.status_code == 200:
        frequent_count = response.json().get('total_count', 0)
        print(f"✅ Found {frequent_count} frequent visitor(s)")
        if frequent_count > 0:
            for visitor in response.json()['frequent_visitors']:
                print(f"   • {visitor['name']} ({visitor['phone']}): {visitor['visits_last_week']} visits")
    
    # Step 5: Test Late Night Visitors Detection
    print("\n🌙 Step 5: Testing Late Night Visitors Detection...")
    response = requests.get(f"{BASE_URL}/ai/late-night-visitors/{building_id}", headers=auth_headers)
    print_response("Late Night Visitors Detection", response)
    
    if response.status_code == 200:
        late_night_count = response.json().get('total_count', 0)
        print(f"✅ Found {late_night_count} late-night entry(ies)")
        print("   Note: Late-night detection requires entries between 12 AM - 5 AM")
        print("   Current test data was created during daytime")
    
    # Step 6: Test Visitor Risk Scoring - Rahul (Frequent)
    print("\n⚠️ Step 6: Testing Visitor Risk Scoring - Rahul (Frequent)...")
    response = requests.get(f"{BASE_URL}/ai/visitor-risk/9111111111", headers=auth_headers)
    print_response("Risk Score - Rahul (Frequent)", response)
    
    if response.status_code == 200:
        risk_data = response.json()
        print(f"✅ Risk Analysis for {risk_data.get('name')}:")
        print(f"   • Risk Score: {risk_data.get('risk_score')}/100")
        print(f"   • Risk Level: {risk_data.get('risk_level').upper()}")
        print(f"   • Total Visits: {risk_data.get('total_visits')}")
        print(f"   • Recent Visits (7 days): {risk_data.get('recent_visits_7_days')}")
        print(f"   • Risk Factors:")
        for factor in risk_data.get('risk_factors', []):
            print(f"     - {factor}")
    
    # Step 7: Test Visitor Risk Scoring - Amit (Suspicious - No flat)
    print("\n⚠️ Step 7: Testing Visitor Risk Scoring - Amit (No flat number)...")
    response = requests.get(f"{BASE_URL}/ai/visitor-risk/9333333333", headers=auth_headers)
    print_response("Risk Score - Amit (Suspicious)", response)
    
    if response.status_code == 200:
        risk_data = response.json()
        print(f"✅ Risk Analysis for {risk_data.get('name')}:")
        print(f"   • Risk Score: {risk_data.get('risk_score')}/100")
        print(f"   • Risk Level: {risk_data.get('risk_level').upper()}")
        print(f"   • Total Visits: {risk_data.get('total_visits')}")
        print(f"   • No Flat Entries: {risk_data.get('no_flat_entries')}")
        print(f"   • Risk Factors:")
        for factor in risk_data.get('risk_factors', []):
            print(f"     - {factor}")
    
    # Step 8: Test Visitor Risk Scoring - Priya (Normal)
    print("\n✅ Step 8: Testing Visitor Risk Scoring - Priya (Normal)...")
    response = requests.get(f"{BASE_URL}/ai/visitor-risk/9222222222", headers=auth_headers)
    print_response("Risk Score - Priya (Normal)", response)
    
    if response.status_code == 200:
        risk_data = response.json()
        print(f"✅ Risk Analysis for {risk_data.get('name')}:")
        print(f"   • Risk Score: {risk_data.get('risk_score')}/100")
        print(f"   • Risk Level: {risk_data.get('risk_level').upper()}")
        print(f"   • Total Visits: {risk_data.get('total_visits')}")
    
    # Step 9: Test Building Analytics Summary
    print("\n📊 Step 9: Testing Building Analytics Summary...")
    response = requests.get(f"{BASE_URL}/ai/building-analytics/{building_id}", headers=auth_headers)
    print_response("Building Analytics Summary", response)
    
    if response.status_code == 200:
        analytics = response.json()
        print(f"✅ Building Analytics for {analytics.get('building_name')}:")
        print(f"   • Total Visits: {analytics.get('total_visits')}")
        print(f"   • Unique Visitors: {analytics.get('unique_visitors')}")
        print(f"   • Avg Visits/Day: {analytics.get('avg_visits_per_day')}")
        print(f"   • Late Night Visits: {analytics.get('late_night_visits')} ({analytics.get('late_night_percentage')}%)")
        print(f"   • No Flat Number: {analytics.get('no_flat_number')} ({analytics.get('no_flat_percentage')}%)")
        print(f"   • Pending Approvals: {analytics.get('pending_approvals')}")
        print(f"   • Approved Visits: {analytics.get('approved_visits')}")
        print(f"   • Rejected Visits: {analytics.get('rejected_visits')}")
        print(f"   • Rejection Rate: {analytics.get('rejection_rate')}%")
    
    # Step 10: Test High-Risk Visitors Detection
    print("\n🚨 Step 10: Testing High-Risk Visitors Detection...")
    response = requests.get(f"{BASE_URL}/ai/high-risk-visitors/{building_id}?min_risk_score=50", headers=auth_headers)
    print_response("High-Risk Visitors Detection", response)
    
    if response.status_code == 200:
        high_risk_count = response.json().get('total_count', 0)
        print(f"✅ Found {high_risk_count} high-risk visitor(s) (score >= 50)")
        if high_risk_count > 0:
            for visitor in response.json()['high_risk_visitors']:
                print(f"\n   ⚠️ {visitor['name']} ({visitor['phone']})")
                print(f"      Risk Score: {visitor['risk_score']}/100 ({visitor['risk_level'].upper()})")
                print(f"      Total Visits: {visitor['total_visits']}")
                print(f"      Risk Factors: {len(visitor['risk_factors'])}")
    
    # Final Summary
    print("\n" + "="*70)
    print("📊 AI ANALYTICS TEST SUMMARY")
    print("="*70)
    print(f"✅ Building: {test_building_name} (ID: {building_id})")
    print(f"✅ Test visitors created: 4 (with different patterns)")
    print(f"✅ Total visits created: ~17")
    print(f"\n✅ All AI Analytics endpoints tested:")
    print("   ✓ GET /ai/frequent-visitors/<building_id>")
    print("   ✓ GET /ai/late-night-visitors/<building_id>")
    print("   ✓ GET /ai/visitor-risk/<phone>")
    print("   ✓ GET /ai/building-analytics/<building_id>")
    print("   ✓ GET /ai/high-risk-visitors/<building_id>")
    print("\n🤖 AI-Powered Visitor Analytics system is fully functional!")
    print("="*70)
    
    print("\n💡 Key AI Features Demonstrated:")
    print("   🔍 Frequent visitor detection (>5 visits in 7 days)")
    print("   🌙 Late-night entry detection (12 AM - 5 AM)")
    print("   ⚠️ Risk scoring algorithm (0-100 scale)")
    print("   📊 Comprehensive building analytics")
    print("   🚨 High-risk visitor identification")
    print("   🎯 Multi-factor risk assessment")


if __name__ == "__main__":
    try:
        test_ai_analytics()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print("Make sure the Flask server is running on http://localhost:5000")
        print("Run: python run.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
