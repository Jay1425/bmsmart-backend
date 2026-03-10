"""
Test script for BMSmart Notification System.

This script tests the complete notification flow:
1. Building registration
2. User registration with device token
3. Visitor entry (triggers notification)
4. Notification retrieval
5. Mark notification as read
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Test data
test_building_name = f"Notification Test Tower {datetime.now().strftime('%H%M%S')}"
test_user_email = f"resident_{datetime.now().strftime('%H%M%S')}@test.com"
test_device_token = "test_fcm_device_token_123456789"


def print_response(title, response):
    """Print formatted API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")


def test_notification_system():
    """Test the complete notification system."""
    
    print("\n🚀 BMSmart Notification System Test")
    print("="*60)
    
    # Step 1: Create a building
    print("\n📍 Step 1: Creating test building...")
    building_data = {
        "name": test_building_name,
        "address": "123 Notification Test Street"
    }
    response = requests.post(f"{BASE_URL}/buildings", json=building_data, headers=HEADERS)
    print_response("Building Created", response)
    
    if response.status_code != 201:
        print("❌ Failed to create building. Exiting.")
        return
    
    building_id = response.json()['building']['id']
    print(f"✅ Building created with ID: {building_id}")
    
    # Step 2: Register a resident user
    print("\n👤 Step 2: Registering resident user...")
    user_data = {
        "name": "Test Resident",
        "email": test_user_email,
        "password": "password123",
        "phone": "9876543210",
        "role": "resident",
        "building_id": building_id
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data, headers=HEADERS)
    print_response("User Registered", response)
    
    if response.status_code != 201:
        print("❌ Failed to register user. Exiting.")
        return
    
    user_id = response.json()['user']['id']
    access_token = response.json()['access_token']
    print(f"✅ User registered with ID: {user_id}")
    print(f"✅ Access token received")
    
    # Step 3: Register device token
    print("\n📱 Step 3: Registering FCM device token...")
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    device_data = {
        "device_token": test_device_token
    }
    response = requests.post(f"{BASE_URL}/notifications/register-device", json=device_data, headers=auth_headers)
    print_response("Device Token Registered", response)
    
    if response.status_code != 200:
        print("❌ Failed to register device token. Exiting.")
        return
    
    print(f"✅ Device token registered successfully")
    
    # Step 4: Create a visitor entry (should trigger notification)
    print("\n🚶 Step 4: Creating visitor entry (should trigger notification)...")
    visitor_data = {
        "name": "Test Visitor",
        "phone": "9123456789",
        "building_id": building_id,
        "flat_number": "A-402",
        "vehicle_number": "MH01AB1234",
        "reason": "Social visit"
    }
    response = requests.post(f"{BASE_URL}/visitors/entry", json=visitor_data, headers=HEADERS)
    print_response("Visitor Entry Created", response)
    
    if response.status_code != 201:
        print("❌ Failed to create visitor entry. Exiting.")
        return
    
    visitor_id = response.json()['visitor']['id']
    notification_sent = response.json().get('notification_sent', False)
    print(f"✅ Visitor entry created with ID: {visitor_id}")
    print(f"✅ Notification sent: {notification_sent}")
    
    # Step 5: Get notifications
    print("\n🔔 Step 5: Retrieving notifications...")
    response = requests.get(f"{BASE_URL}/notifications/my", headers=auth_headers)
    print_response("Notifications Retrieved", response)
    
    if response.status_code != 200:
        print("❌ Failed to retrieve notifications.")
        return
    
    notifications = response.json().get('notifications', [])
    total_notifications = response.json().get('total', 0)
    print(f"✅ Retrieved {total_notifications} notification(s)")
    
    if not notifications:
        print("⚠️ No notifications found. This might be expected if FCM credentials are not configured.")
        notification_id = None
    else:
        notification_id = notifications[0]['id']
        print(f"✅ First notification ID: {notification_id}")
        print(f"   Title: {notifications[0]['title']}")
        print(f"   Message: {notifications[0]['message']}")
        print(f"   Is Read: {notifications[0]['is_read']}")
    
    # Step 6: Get unread notifications only
    print("\n🔔 Step 6: Retrieving unread notifications only...")
    response = requests.get(f"{BASE_URL}/notifications/my?unread_only=true", headers=auth_headers)
    print_response("Unread Notifications Retrieved", response)
    
    if response.status_code == 200:
        unread_count = response.json().get('total', 0)
        print(f"✅ Retrieved {unread_count} unread notification(s)")
    
    # Step 7: Mark notification as read (if we have a notification)
    if notification_id:
        print(f"\n✅ Step 7: Marking notification {notification_id} as read...")
        response = requests.post(f"{BASE_URL}/notifications/read/{notification_id}", headers=auth_headers)
        print_response("Notification Marked as Read", response)
        
        if response.status_code == 200:
            print(f"✅ Notification marked as read")
        else:
            print("❌ Failed to mark notification as read")
        
        # Step 8: Verify notification is now marked as read
        print("\n🔔 Step 8: Verifying notification is marked as read...")
        response = requests.get(f"{BASE_URL}/notifications/my", headers=auth_headers)
        if response.status_code == 200:
            notifications = response.json().get('notifications', [])
            if notifications:
                is_read = notifications[0]['is_read']
                print(f"✅ Notification read status: {is_read}")
                if is_read:
                    print("✅ Notification successfully marked as read!")
                else:
                    print("❌ Notification still showing as unread")
    else:
        print("\n⚠️ Step 7-8: Skipping mark-as-read test (no notifications found)")
    
    # Step 9: Mark all notifications as read
    print("\n✅ Step 9: Marking all notifications as read...")
    response = requests.post(f"{BASE_URL}/notifications/mark-all-read", headers=auth_headers)
    print_response("All Notifications Marked as Read", response)
    
    if response.status_code == 200:
        count = response.json().get('count', 0)
        print(f"✅ Marked {count} notification(s) as read")
    
    # Final Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Building created: {test_building_name} (ID: {building_id})")
    print(f"✅ User registered: {test_user_email} (ID: {user_id})")
    print(f"✅ Device token registered: {test_device_token}")
    print(f"✅ Visitor entry created: Test Visitor (ID: {visitor_id})")
    print(f"✅ Notifications created: {total_notifications}")
    
    if notification_sent:
        print("✅ Push notification sent via FCM")
    else:
        print("⚠️ Push notification not sent (FCM may not be configured)")
    
    print("\n🎉 Notification system test completed!")
    print("="*60)
    
    print("\n💡 Notes:")
    print("- If 'notification_sent' is False, check Firebase credentials")
    print("- Firebase Admin SDK must be installed: pip install firebase-admin")
    print("- Firebase credentials must be in firebase-credentials.json")
    print("- See NOTIFICATION_SYSTEM_IMPLEMENTATION.md for setup guide")


if __name__ == "__main__":
    try:
        test_notification_system()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print("Make sure the Flask server is running on http://localhost:5000")
        print("Run: python run.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
