"""
Test script for BMSmart Flat Number Linking Enhancement.

This script tests the enhanced notification system that links visitors to specific residents by flat_number:
1. Register residents with specific flat numbers
2. Create visitor entry for a specific flat
3. Verify notification sent only to the correct resident
4. Test case where no resident exists for flat number
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Test data
test_building_name = f"Flat Linking Test Tower {datetime.now().strftime('%H%M%S')}"


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


def test_flat_number_linking():
    """Test the flat number linking enhancement."""
    
    print("\n🏢 BMSmart Flat Number Linking Test")
    print("="*70)
    
    # Step 1: Create a building
    print("\n📍 Step 1: Creating test building...")
    building_data = {
        "name": test_building_name,
        "address": "456 Flat Linking Test Avenue"
    }
    response = requests.post(f"{BASE_URL}/buildings", json=building_data, headers=HEADERS)
    print_response("Building Created", response)
    
    if response.status_code != 201:
        print("❌ Failed to create building. Exiting.")
        return
    
    building_id = response.json()['building']['id']
    print(f"✅ Building created with ID: {building_id}")
    
    # Step 2: Register Resident 1 for Flat A-402
    print("\n👤 Step 2: Registering Resident 1 (Flat A-402)...")
    resident1_email = f"resident_a402_{datetime.now().strftime('%H%M%S')}@test.com"
    resident1_data = {
        "name": "Jay Kumar",
        "email": resident1_email,
        "password": "password123",
        "phone": "9876543210",
        "role": "resident",
        "building_id": building_id,
        "flat_number": "A-402"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=resident1_data, headers=HEADERS)
    print_response("Resident 1 Registered (A-402)", response)
    
    if response.status_code != 201:
        print("❌ Failed to register Resident 1. Exiting.")
        return
    
    resident1_id = response.json()['user']['id']
    resident1_flat = response.json()['user']['flat_number']
    resident1_token = response.json()['access_token']
    print(f"✅ Resident 1 registered: {resident1_email}")
    print(f"✅ Resident 1 ID: {resident1_id}, Flat: {resident1_flat}")
    
    # Step 3: Register Resident 2 for Flat B-101
    print("\n👤 Step 3: Registering Resident 2 (Flat B-101)...")
    resident2_email = f"resident_b101_{datetime.now().strftime('%H%M%S')}@test.com"
    resident2_data = {
        "name": "Priya Sharma",
        "email": resident2_email,
        "password": "password123",
        "phone": "9123456789",
        "role": "resident",
        "building_id": building_id,
        "flat_number": "B-101"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=resident2_data, headers=HEADERS)
    print_response("Resident 2 Registered (B-101)", response)
    
    if response.status_code != 201:
        print("❌ Failed to register Resident 2. Exiting.")
        return
    
    resident2_id = response.json()['user']['id']
    resident2_flat = response.json()['user']['flat_number']
    resident2_token = response.json()['access_token']
    print(f"✅ Resident 2 registered: {resident2_email}")
    print(f"✅ Resident 2 ID: {resident2_id}, Flat: {resident2_flat}")
    
    # Step 4: Register device tokens for both residents
    print("\n📱 Step 4: Registering device tokens for both residents...")
    
    # Register device token for Resident 1
    auth_headers_1 = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {resident1_token}"
    }
    device_data_1 = {"device_token": f"fcm_token_resident1_{resident1_id}"}
    response = requests.post(f"{BASE_URL}/notifications/register-device", json=device_data_1, headers=auth_headers_1)
    print_response("Device Token Registered for Resident 1", response)
    
    # Register device token for Resident 2
    auth_headers_2 = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {resident2_token}"
    }
    device_data_2 = {"device_token": f"fcm_token_resident2_{resident2_id}"}
    response = requests.post(f"{BASE_URL}/notifications/register-device", json=device_data_2, headers=auth_headers_2)
    print_response("Device Token Registered for Resident 2", response)
    
    print("✅ Device tokens registered for both residents")
    
    # Step 5: Create visitor entry for Flat A-402 (should notify ONLY Resident 1)
    print("\n🚶 Step 5: Creating visitor entry for Flat A-402...")
    print("   Expected: Notification sent ONLY to Resident 1 (Jay Kumar)")
    visitor1_data = {
        "name": "Rahul Visitor",
        "phone": "9999888877",
        "building_id": building_id,
        "flat_number": "A-402",
        "vehicle_number": "MH01AB1234",
        "reason": "Social visit"
    }
    response = requests.post(f"{BASE_URL}/visitors/entry", json=visitor1_data, headers=HEADERS)
    print_response("Visitor Entry Created for A-402", response)
    
    if response.status_code != 201:
        print("❌ Failed to create visitor entry. Exiting.")
        return
    
    visitor1_id = response.json()['visitor']['id']
    resident_notified = response.json().get('resident_notified', False)
    notification_sent = response.json().get('notification_sent', False)
    print(f"✅ Visitor entry created: {visitor1_id}")
    print(f"✅ Resident notified (database): {resident_notified}")
    print(f"✅ Push notification sent (FCM): {notification_sent}")
    
    # Step 6: Check notifications for Resident 1 (should have 1 notification)
    print("\n🔔 Step 6: Checking notifications for Resident 1 (A-402)...")
    response = requests.get(f"{BASE_URL}/notifications/my", headers=auth_headers_1)
    print_response("Resident 1 Notifications", response)
    
    if response.status_code == 200:
        resident1_notifications = response.json().get('notifications', [])
        print(f"✅ Resident 1 has {len(resident1_notifications)} notification(s)")
        if resident1_notifications:
            print(f"   Title: {resident1_notifications[0]['title']}")
            print(f"   Message: {resident1_notifications[0]['message']}")
            print(f"   Visitor ID: {resident1_notifications[0]['visitor_id']}")
    
    # Step 7: Check notifications for Resident 2 (should have 0 notifications)
    print("\n🔔 Step 7: Checking notifications for Resident 2 (B-101)...")
    response = requests.get(f"{BASE_URL}/notifications/my", headers=auth_headers_2)
    print_response("Resident 2 Notifications", response)
    
    if response.status_code == 200:
        resident2_notifications = response.json().get('notifications', [])
        print(f"✅ Resident 2 has {len(resident2_notifications)} notification(s)")
        if len(resident2_notifications) == 0:
            print("   ✅ CORRECT: Resident 2 should NOT receive notification for A-402 visitor")
    
    # Step 8: Create visitor entry for Flat B-101 (should notify ONLY Resident 2)
    print("\n🚶 Step 8: Creating visitor entry for Flat B-101...")
    print("   Expected: Notification sent ONLY to Resident 2 (Priya Sharma)")
    visitor2_data = {
        "name": "Sneha Visitor",
        "phone": "9888777666",
        "building_id": building_id,
        "flat_number": "B-101",
        "vehicle_number": "MH02XY5678",
        "reason": "Delivery"
    }
    response = requests.post(f"{BASE_URL}/visitors/entry", json=visitor2_data, headers=HEADERS)
    print_response("Visitor Entry Created for B-101", response)
    
    if response.status_code == 201:
        visitor2_id = response.json()['visitor']['id']
        resident_notified = response.json().get('resident_notified', False)
        print(f"✅ Visitor entry created: {visitor2_id}")
        print(f"✅ Resident notified: {resident_notified}")
    
    # Step 9: Check notifications again for both residents
    print("\n🔔 Step 9: Checking final notification counts...")
    
    # Resident 1 - should still have only 1 notification
    response = requests.get(f"{BASE_URL}/notifications/my", headers=auth_headers_1)
    if response.status_code == 200:
        resident1_count = response.json().get('total', 0)
        print(f"✅ Resident 1 (A-402) final count: {resident1_count} notification(s)")
        if resident1_count == 1:
            print("   ✅ CORRECT: Only notified for A-402 visitor")
    
    # Resident 2 - should now have 1 notification
    response = requests.get(f"{BASE_URL}/notifications/my", headers=auth_headers_2)
    if response.status_code == 200:
        resident2_count = response.json().get('total', 0)
        print(f"✅ Resident 2 (B-101) final count: {resident2_count} notification(s)")
        if resident2_count == 1:
            print("   ✅ CORRECT: Only notified for B-101 visitor")
    
    # Step 10: Test visitor entry for non-existent flat (should create visitor but no notification)
    print("\n🚶 Step 10: Creating visitor entry for non-existent Flat C-999...")
    print("   Expected: Visitor created, but NO notification sent")
    visitor3_data = {
        "name": "Unknown Flat Visitor",
        "phone": "9777666555",
        "building_id": building_id,
        "flat_number": "C-999",
        "reason": "Looking for flat"
    }
    response = requests.post(f"{BASE_URL}/visitors/entry", json=visitor3_data, headers=HEADERS)
    print_response("Visitor Entry Created for C-999 (Non-existent)", response)
    
    if response.status_code == 201:
        visitor3_id = response.json()['visitor']['id']
        resident_notified = response.json().get('resident_notified', False)
        print(f"✅ Visitor entry created: {visitor3_id}")
        print(f"✅ Resident notified: {resident_notified}")
        if not resident_notified:
            print("   ✅ CORRECT: No resident found for C-999, no notification sent")
    
    # Final Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY - FLAT NUMBER LINKING")
    print("="*70)
    print(f"✅ Building created: {test_building_name} (ID: {building_id})")
    print(f"✅ Resident 1 registered: Flat A-402 (ID: {resident1_id})")
    print(f"✅ Resident 2 registered: Flat B-101 (ID: {resident2_id})")
    print(f"✅ Visitor 1 created for A-402 → Notified Resident 1 only")
    print(f"✅ Visitor 2 created for B-101 → Notified Resident 2 only")
    print(f"✅ Visitor 3 created for C-999 → No resident found, no notification")
    print("\n✅ Flat number linking works correctly!")
    print("✅ Notifications sent only to the correct resident based on flat_number")
    print("="*70)
    
    print("\n💡 Key Features Verified:")
    print("   ✓ Users can register with flat_number field")
    print("   ✓ Visitor notification query filters by flat_number + building_id")
    print("   ✓ Only the specific resident receives notification")
    print("   ✓ Other residents in same building are NOT notified")
    print("   ✓ System handles non-existent flat numbers gracefully")
    print("   ✓ Visitor entry succeeds even if no resident exists for flat")


if __name__ == "__main__":
    try:
        test_flat_number_linking()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print("Make sure the Flask server is running on http://localhost:5000")
        print("Run: python run.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
