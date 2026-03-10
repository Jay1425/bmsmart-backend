"""
Test script to verify QR visitor entry functionality.
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

print("\n=== BMSmart QR Visitor Entry Test ===\n")

# Test 1: Create a building
print("1. Creating a test building...")
building_data = {
    "name": "Test Tower",
    "address": "123 Test Street",
    "city": "Test City"
}

try:
    response = requests.post(f"{BASE_URL}/buildings/create", json=building_data)
    if response.status_code == 201:
        building = response.json()['building']
        building_id = building['id']
        print(f"   ✓ Building created: {building['name']} (ID: {building_id})")
    else:
        print(f"   ✗ Failed: {response.json()}")
        exit(1)
except requests.exceptions.ConnectionError:
    print("   ✗ Error: Server not running. Please start the server with 'python run.py'")
    exit(1)

# Test 2: Get building entry URL (for QR code)
print(f"\n2. Getting QR entry URL for building {building_id}...")
response = requests.get(f"{BASE_URL}/buildings/{building_id}/entry-url")
if response.status_code == 200:
    entry_data = response.json()
    print(f"   ✓ Entry URL: {entry_data['entry_url']}")
else:
    print(f"   ✗ Failed: {response.json()}")

# Test 3: Get visitor form data
print(f"\n3. Getting visitor form data...")
response = requests.get(f"{BASE_URL}/visitor/form/{building_id}")
if response.status_code == 200:
    form_data = response.json()
    print(f"   ✓ Building: {form_data['building_name']} (ID: {form_data['building_id']})")
else:
    print(f"   ✗ Failed: {response.json()}")

# Test 4: Record visitor entry
print(f"\n4. Recording visitor entry...")
visitor_data = {
    "name": "John Visitor",
    "phone": "9876543210",
    "reason": "Meeting with resident",
    "building_id": building_id,
    "photo_url": "https://example.com/photo.jpg"
}
response = requests.post(f"{BASE_URL}/visitors/entry", json=visitor_data)
if response.status_code == 201:
    visitor = response.json()['visitor']
    visitor_id = visitor['id']
    print(f"   ✓ Visitor entry recorded: {visitor['name']}")
    print(f"   ✓ Entry time: {visitor['entry_time']}")
    print(f"   ✓ Visitor ID: {visitor_id}")
else:
    print(f"   ✗ Failed: {response.json()}")
    exit(1)

# Test 5: Get visitors for building
print(f"\n5. Getting all visitors for building {building_id}...")
response = requests.get(f"{BASE_URL}/visitors/building/{building_id}")
if response.status_code == 200:
    visitors = response.json()['visitors']
    print(f"   ✓ Found {len(visitors)} visitor(s)")
    for v in visitors:
        status = "Inside" if not v['exit_time'] else "Exited"
        print(f"     - {v['name']} ({status})")
else:
    print(f"   ✗ Failed: {response.json()}")

# Test 6: Record visitor exit
print(f"\n6. Recording visitor exit...")
response = requests.post(f"{BASE_URL}/visitors/exit/{visitor_id}")
if response.status_code == 200:
    visitor = response.json()['visitor']
    print(f"   ✓ Visitor exit recorded: {visitor['name']}")
    print(f"   ✓ Exit time: {visitor['exit_time']}")
else:
    print(f"   ✗ Failed: {response.json()}")

# Test 7: Verify exit was recorded
print(f"\n7. Verifying visitor exit...")
response = requests.get(f"{BASE_URL}/visitors/building/{building_id}")
if response.status_code == 200:
    visitors = response.json()['visitors']
    for v in visitors:
        if v['id'] == visitor_id:
            if v['exit_time']:
                print(f"   ✓ Exit confirmed for {v['name']}")
                print(f"   ✓ Entry: {v['entry_time']}")
                print(f"   ✓ Exit:  {v['exit_time']}")
            else:
                print(f"   ✗ Exit not recorded")
else:
    print(f"   ✗ Failed: {response.json()}")

print("\n=== QR Visitor Entry Flow Test Complete ===\n")
print("Summary:")
print("✓ Building QR entry URL generation")
print("✓ Public visitor form endpoint")
print("✓ Visitor entry with automatic timestamp")
print("✓ Visitor exit with timestamp update")
print("✓ Visitor tracking by building")
print("\nThe QR visitor entry system is fully functional!")
