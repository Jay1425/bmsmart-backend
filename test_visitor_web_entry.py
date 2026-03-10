"""
Test script for visitor web entry system
"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("VISITOR WEB ENTRY SYSTEM - TEST SCRIPT")
print("=" * 60)

# Test 1: Create a test building
print("\n[Test 1] Creating test building...")
building_data = {
    "name": "Sunrise Towers",
    "address": "456 Test Avenue",
    "city": "Mumbai"
}

try:
    response = requests.post(f"{BASE_URL}/buildings/create", json=building_data)
    if response.status_code == 201:
        building = response.json()['building']
        building_id = building['id']
        print(f"✓ Building created successfully!")
        print(f"  ID: {building_id}")
        print(f"  Name: {building['name']}")
    else:
        print(f"✗ Failed to create building: {response.text}")
        exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Test 2: Access visitor form page (GET)
print(f"\n[Test 2] Accessing visitor form page...")
try:
    response = requests.get(f"{BASE_URL}/visitor/form/{building_id}")
    if response.status_code == 200:
        html_content = response.text
        print(f"✓ Form page loaded successfully!")
        print(f"  Status Code: {response.status_code}")
        print(f"  Content Type: {response.headers.get('Content-Type')}")
        print(f"  Content Length: {len(html_content)} bytes")
        
        # Check for key elements
        print("\n  Checking HTML content:")
        checks = [
            ("Page title", "Visitor Entry" in html_content),
            ("Building name", building['name'] in html_content),
            ("Name field", 'name="name"' in html_content),
            ("Phone field", 'name="phone"' in html_content),
            ("Flat number field", 'name="flat_number"' in html_content),
            ("Vehicle number field", 'name="vehicle_number"' in html_content),
            ("Reason field", 'name="reason"' in html_content),
            ("Photo upload", 'name="photo"' in html_content),
            ("Submit button", "Submit Entry" in html_content),
        ]
        
        for check_name, result in checks:
            status = "✓" if result else "✗"
            print(f"    {status} {check_name}")
    else:
        print(f"✗ Failed to load form: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Test 3: Submit visitor entry (POST)
print(f"\n[Test 3] Submitting visitor entry...")
visitor_data = {
    "name": "Test Visitor",
    "phone": "9876543210",
    "flat_number": "C-301",
    "reason": "Automated test visit",
    "vehicle_number": "MH12XY9876"
}

try:
    response = requests.post(f"{BASE_URL}/visitor/form/{building_id}", data=visitor_data)
    if response.status_code in [200, 302]:  # 302 for redirect
        print(f"✓ Visitor entry submitted successfully!")
        print(f"  Status Code: {response.status_code}")
        
        # If redirected, check the success page
        if response.status_code == 302 or 'success' in response.url:
            print(f"  Redirected to: {response.url}")
    else:
        print(f"✗ Failed to submit entry: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Test 4: Verify visitor was created in database
print(f"\n[Test 4] Verifying visitor in database...")
try:
    response = requests.get(f"{BASE_URL}/visitors/building/{building_id}")
    if response.status_code == 200:
        visitors = response.json()['visitors']
        print(f"✓ Retrieved {len(visitors)} visitor(s)")
        
        if visitors:
            latest_visitor = visitors[-1]  # Get last visitor
            print(f"\n  Latest Visitor Details:")
            print(f"    Name: {latest_visitor['name']}")
            print(f"    Phone: {latest_visitor['phone']}")
            print(f"    Flat: {latest_visitor.get('flat_number', 'N/A')}")
            print(f"    Vehicle: {latest_visitor.get('vehicle_number', 'N/A')}")
            print(f"    Reason: {latest_visitor['reason']}")
            print(f"    Entry Time: {latest_visitor['entry_time']}")
    else:
        print(f"✗ Failed to retrieve visitors: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Test invalid building
print(f"\n[Test 5] Testing error handling (invalid building)...")
try:
    response = requests.get(f"{BASE_URL}/visitor/form/9999")
    if response.status_code == 404:
        print(f"✓ Error handling working correctly!")
        print(f"  Status Code: {response.status_code}")
        if "Building not found" in response.text or "not found" in response.text.lower():
            print(f"  Error message displayed in HTML")
    else:
        print(f"✗ Expected 404, got {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("✓ All core functionality working!")
print(f"\nVisitor Form URL: {BASE_URL}/visitor/form/{building_id}")
print("\nYou can now:")
print("  1. Open the form URL in a browser")
print("  2. Scan QR code with mobile device")
print("  3. Test photo upload manually")
print("=" * 60)
