# QR Visitor Entry - Manual Testing Guide

## Test the QR Visitor Entry Flow

### Prerequisites
Server must be running:
```bash
python run.py
```

Server will be at: `http://localhost:5000`

---

## Test Flow

### 1. Create a Building
```bash
curl -X POST http://localhost:5000/buildings/create -H "Content-Type: application/json" -d "{\"name\":\"Test Tower\",\"address\":\"123 Test St\",\"city\":\"Test City\"}"
```

Expected Response:
```json
{
  "message": "Building created successfully",
  "building": {
    "id": 1,
    "name": "Test Tower",
    "address": "123 Test St",
    "city": "Test City",
    "created_at": "2026-03-10T17:30:00.000000"
  }
}
```

Note the `building_id` for next steps.

---

### 2. Get Building QR Entry URL
```bash
curl http://localhost:5000/buildings/1/entry-url
```

Expected Response:
```json
{
  "building_id": 1,
  "entry_url": "/visitor/entry/1"
}
```

This URL can be encoded into a QR code that visitors can scan.

---

### 3. Get Visitor Form (What visitors see after scanning QR)
```bash
curl http://localhost:5000/visitor/form/1
```

Expected Response:
```json
{
  "building_id": 1,
  "building_name": "Test Tower"
}
```

---

### 4. Submit Visitor Entry (Visitor fills form and submits)
```bash
curl -X POST http://localhost:5000/visitors/entry -H "Content-Type: application/json" -d "{\"name\":\"John Visitor\",\"phone\":\"9876543210\",\"reason\":\"Meeting with resident\",\"building_id\":1,\"photo_url\":\"https://example.com/photo.jpg\"}"
```

Expected Response:
```json
{
  "message": "Visitor entry recorded successfully",
  "visitor": {
    "id": 1,
    "name": "John Visitor",
    "phone": "9876543210",
    "photo_url": "https://example.com/photo.jpg",
    "reason": "Meeting with resident",
    "building_id": 1,
    "entry_time": "2026-03-10T17:30:00.000000",
    "exit_time": null
  }
}
```

Note the `visitor_id` for exit step.

---

### 5. View Visitors for Building
```bash
curl http://localhost:5000/visitors/building/1
```

Expected Response:
```json
{
  "visitors": [
    {
      "id": 1,
      "name": "John Visitor",
      "phone": "9876543210",
      "photo_url": "https://example.com/photo.jpg",
      "reason": "Meeting with resident",
      "building_id": 1,
      "entry_time": "2026-03-10T17:30:00.000000",
      "exit_time": null
    }
  ]
}
```

---

### 6. Record Visitor Exit
```bash
curl -X POST http://localhost:5000/visitors/exit/1
```

Expected Response:
```json
{
  "message": "Visitor exit recorded successfully",
  "visitor": {
    "id": 1,
    "name": "John Visitor",
    "phone": "9876543210",
    "photo_url": "https://example.com/photo.jpg",
    "reason": "Meeting with resident",
    "building_id": 1,
    "entry_time": "2026-03-10T17:30:00.000000",
    "exit_time": "2026-03-10T18:00:00.000000"
  }
}
```

---

## Complete QR Visitor Flow

```
1. Building Manager generates QR code
   └→ GET /buildings/{id}/entry-url

2. Visitor scans QR code
   └→ Redirects to: /visitor/entry/{building_id}

3. App fetches building info
   └→ GET /visitor/form/{building_id}

4. Visitor fills form (name, phone, reason, photo)
   └→ POST /visitors/entry (with building_id)
   └→ entry_time is set automatically

5. Visitor inside building
   └→ System tracks active visitors
   └→ GET /visitors/building/{building_id}

6. Visitor leaves
   └→ POST /visitors/exit/{visitor_id}
   └→ exit_time is set automatically

7. View complete visitor log
   └→ GET /visitors/building/{building_id}
```

---

## PowerShell Commands (Windows)

If using PowerShell, use `Invoke-RestMethod`:

### Create Building
```powershell
$body = @{
    name = "Test Tower"
    address = "123 Test St"
    city = "Test City"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/buildings/create" -Method POST -Body $body -ContentType "application/json"
```

### Get QR Entry URL
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/buildings/1/entry-url" -Method GET
```

### Submit Visitor Entry
```powershell
$visitor = @{
    name = "John Visitor"
    phone = "9876543210"
    reason = "Meeting with resident"
    building_id = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/visitors/entry" -Method POST -Body $visitor -ContentType "application/json"
```

### Record Exit
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/visitors/exit/1" -Method POST
```

---

## Success Indicators

✅ Building QR URL generated successfully  
✅ Visitor form shows correct building name  
✅ Visitor entry recorded with automatic timestamp  
✅ Visitor appears in building visitor list  
✅ Visitor exit recorded with automatic timestamp  
✅ Complete visitor log maintained  

---

## Error Cases to Test

### Invalid Building ID
```bash
curl http://localhost:5000/visitor/form/999
```
Expected: 404 Not Found

### Missing Required Fields
```bash
curl -X POST http://localhost:5000/visitors/entry -H "Content-Type: application/json" -d "{\"name\":\"John\"}"
```
Expected: 400 Bad Request

### Double Exit
```bash
curl -X POST http://localhost:5000/visitors/exit/1
curl -X POST http://localhost:5000/visitors/exit/1
```
Expected: Second call returns 400 "Visitor has already exited"
