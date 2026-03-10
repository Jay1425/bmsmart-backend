# QR Code and Analytics Testing Guide

## Start the Server

```bash
python run.py
```

Server at: `http://localhost:5000`

---

## Test QR Code Generation

### 1. Create a Building First

```bash
curl -X POST http://localhost:5000/buildings/create -H "Content-Type: application/json" -d "{\"name\":\"Test Tower\",\"address\":\"123 Test St\",\"city\":\"Test City\"}"
```

Note the `building_id` returned.

---

### 2. Generate QR Code

#### Using curl (saves to file):
```bash
curl http://localhost:5000/buildings/1/qr -o building_1_qr.png
```

#### Using Web Browser:
Open: `http://localhost:5000/buildings/1/qr`

The QR code image will be displayed in your browser.

#### Using PowerShell:
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/buildings/1/qr" -OutFile "building_1_qr.png"
```

**Result:** A PNG image with QR code encoding `http://localhost:5000/visitor/entry/1`

---

### 3. Verify QR Code Content

Scan the QR code with your phone or use an online QR reader. It should decode to:
```
http://localhost:5000/visitor/entry/1
```

---

## Test Visitor Analytics

### 1. Add Some Test Visitors

#### Add visitor 1 (today):
```bash
curl -X POST http://localhost:5000/visitors/entry -H "Content-Type: application/json" -d "{\"name\":\"John Doe\",\"phone\":\"1234567890\",\"building_id\":1,\"reason\":\"Meeting\"}"
```

#### Add visitor 2 (today):
```bash
curl -X POST http://localhost:5000/visitors/entry -H "Content-Type: application/json" -d "{\"name\":\"Jane Smith\",\"phone\":\"9876543210\",\"building_id\":1,\"reason\":\"Delivery\"}"
```

#### Add visitor 3 (today):
```bash
curl -X POST http://localhost:5000/visitors/entry -H "Content-Type: application/json" -d "{\"name\":\"Bob Wilson\",\"phone\":\"5555555555\",\"building_id\":1,\"reason\":\"Maintenance\"}"
```

---

### 2. Record Exit for One Visitor

```bash
curl -X POST http://localhost:5000/visitors/exit/1
```

Now visitor 1 has exited, but visitors 2 and 3 are still inside.

---

### 3. Get Visitor Analytics

```bash
curl http://localhost:5000/analytics/visitors/1
```

**Expected Response:**
```json
{
  "today": 3,
  "this_week": 3,
  "inside": 2
}
```

**Explanation:**
- `today`: 3 visitors entered today
- `this_week`: 3 visitors entered this week
- `inside`: 2 visitors currently inside (no exit_time)

---

### 4. Test with PowerShell

```powershell
# Get analytics
Invoke-RestMethod -Uri "http://localhost:5000/analytics/visitors/1" -Method GET

# Add visitor
$visitor = @{
    name = "Test Visitor"
    phone = "1111111111"
    building_id = 1
    reason = "Testing"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/visitors/entry" -Method POST -Body $visitor -ContentType "application/json"

# Check updated analytics
Invoke-RestMethod -Uri "http://localhost:5000/analytics/visitors/1" -Method GET
```

---

## Complete Workflow Test

### Step 1: Create Building
```bash
curl -X POST http://localhost:5000/buildings/create -H "Content-Type: application/json" -d "{\"name\":\"Smart Tower\",\"address\":\"456 Main St\",\"city\":\"New York\"}"
```

### Step 2: Generate and Save QR Code
```bash
curl http://localhost:5000/buildings/1/qr -o smart_tower_qr.png
```

### Step 3: Simulate Multiple Visitors
```bash
# Visitor 1
curl -X POST http://localhost:5000/visitors/entry -H "Content-Type: application/json" -d "{\"name\":\"Alice\",\"phone\":\"1111111111\",\"building_id\":1}"

# Visitor 2
curl -X POST http://localhost:5000/visitors/entry -H "Content-Type: application/json" -d "{\"name\":\"Bob\",\"phone\":\"2222222222\",\"building_id\":1}"

# Visitor 3
curl -X POST http://localhost:5000/visitors/entry -H "Content-Type: application/json" -d "{\"name\":\"Charlie\",\"phone\":\"3333333333\",\"building_id\":1}"

# Visitor 4
curl -X POST http://localhost:5000/visitors/entry -H "Content-Type: application/json" -d "{\"name\":\"Diana\",\"phone\":\"4444444444\",\"building_id\":1}"
```

### Step 4: Some Visitors Exit
```bash
# Alice exits
curl -X POST http://localhost:5000/visitors/exit/1

# Bob exits
curl -X POST http://localhost:5000/visitors/exit/2
```

### Step 5: View Analytics
```bash
curl http://localhost:5000/analytics/visitors/1
```

**Expected:**
```json
{
  "today": 4,
  "this_week": 4,
  "inside": 2
}
```

### Step 6: View Active Visitors
```bash
curl http://localhost:5000/visitors/building/1
```

Shows all visitors with Charlie and Diana having `exit_time: null`.

---

## Error Cases

### Invalid Building ID (QR):
```bash
curl http://localhost:5000/buildings/999/qr
```
**Expected:** 404 - Building not found

### Invalid Building ID (Analytics):
```bash
curl http://localhost:5000/analytics/visitors/999
```
**Expected:** 404 - Building not found

---

## Production Use

1. **Generate QR Code for Each Building**
   - Call `/buildings/{id}/qr`
   - Print the QR code image
   - Display at building entrance

2. **Monitor Analytics Dashboard**
   - Poll `/analytics/visitors/{id}` periodically
   - Display real-time visitor counts
   - Track occupancy trends

3. **Visitor Flow**
   - Visitor scans QR → Opens entry form
   - Submits entry → Automatically counted in analytics
   - Exits building → "inside" count decreases

---

## Notes

- QR codes are permanent and can be regenerated anytime
- Analytics are real-time based on database queries
- "Today" resets at midnight UTC
- "This week" starts on Monday
- "Inside" count shows visitors without exit_time

---

## Success Indicators

✅ QR code image generates successfully  
✅ QR code encodes correct visitor entry URL  
✅ Analytics return correct counts  
✅ "Today" count includes all visitors from midnight  
✅ "This week" count includes all visitors since Monday  
✅ "Inside" count only includes visitors without exit_time  
