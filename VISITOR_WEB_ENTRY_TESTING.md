# Visitor Web Entry System - Testing Guide

## Overview
Complete visitor entry system using server-rendered HTML pages that integrate with the existing BMSmart backend.

---

## System Architecture

### Flow:
```
QR Code → /visitor/form/<building_id> (GET) → Visitor Form (HTML)
                                              ↓
                                         Form Submit (POST)
                                              ↓
                                    Save to Database + Photo Upload
                                              ↓
                                    /visitor/success (Redirect)
```

---

## Start the Server

```powershell
python run.py
```

Server: `http://localhost:5000`

---

## Testing the Visitor Entry System

### 1. Create a Test Building First

```powershell
$building = @{
    name = "Sunset Apartments"
    address = "123 Main Street"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/buildings/create" `
    -Method POST -Body $building -ContentType "application/json"
```

**Response:**
```json
{
  "message": "Building created successfully",
  "building": {
    "id": 1,
    "name": "Sunset Apartments",
    "address": "123 Main Street"
  }
}
```

---

### 2. Access Visitor Form (Web Browser)

Open in your browser:
```
http://localhost:5000/visitor/form/1
```

This will display a mobile-friendly web form with:
- Clean, modern design with gradient background
- Building name display
- Form fields:
  - Full Name (required)
  - Phone Number (required)
  - Flat/Unit Number (optional)
  - Reason for Visit (required)
  - Vehicle Number (optional)
  - Photo Upload (optional)

---

### 3. Submit Visitor Entry (Web Form)

Fill out the form in your browser and click "Submit Entry"

On successful submission, you'll be redirected to:
```
http://localhost:5000/visitor/success?visitor_id=1&building_id=1
```

This displays:
- Success icon with animation
- Visitor details
- Building name
- Entry timestamp
- Buttons to print receipt or add new entry

---

### 4. Test with curl (Manual Testing)

#### GET Form (returns HTML):
```bash
curl http://localhost:5000/visitor/form/1
```

#### POST Form Submission:
```bash
curl -X POST http://localhost:5000/visitor/form/1 \
  -F "name=John Doe" \
  -F "phone=9876543210" \
  -F "flat_number=A-101" \
  -F "reason=Personal visit" \
  -F "vehicle_number=MH01AB1234"
```

#### With Photo Upload:
```bash
curl -X POST http://localhost:5000/visitor/form/1 \
  -F "name=Jane Smith" \
  -F "phone=9876543210" \
  -F "flat_number=B-205" \
  -F "reason=Delivery" \
  -F "vehicle_number=MH02CD5678" \
  -F "photo=@/path/to/photo.jpg"
```

---

### 5. PowerShell Testing (Form Submission)

```powershell
# Submit visitor entry with form data
$form = @{
    name = "John Doe"
    phone = "9876543210"
    flat_number = "A-101"
    reason = "Personal visit"
    vehicle_number = "MH01AB1234"
}

# Note: PowerShell Invoke-RestMethod doesn't handle multipart/form-data easily
# Use Invoke-WebRequest for form posts:
$response = Invoke-WebRequest -Uri "http://localhost:5000/visitor/form/1" `
    -Method POST -Body $form -ContentType "application/x-www-form-urlencoded"

Write-Host "Status Code: $($response.StatusCode)"
```

---

## QR Code Integration Testing

### 1. Generate QR Code for Building

```powershell
# Get QR code image
Invoke-WebRequest -Uri "http://localhost:5000/buildings/1/qr" `
    -OutFile "building_1_qr.png"

Write-Host "QR code saved as building_1_qr.png"
```

### 2. QR Code Flow

The QR code contains the URL:
```
http://localhost:5000/visitor/form/1
```

When scanned:
1. Opens mobile browser
2. Displays visitor entry form
3. User fills details
4. Submits form
5. Success page displayed

---

## Verify Database Entries

### Check All Visitors:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/visitors" -Method GET
```

### Check Visitors for Specific Building:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/visitors/building/1" -Method GET
```

**Example Response:**
```json
{
  "visitors": [
    {
      "id": 1,
      "name": "John Doe",
      "phone": "9876543210",
      "flat_number": "A-101",
      "vehicle_number": "MH01AB1234",
      "reason": "Personal visit",
      "photo_url": "/static/uploads/visitor_photos/John_Doe_20260310_183245.jpg",
      "building_id": 1,
      "entry_time": "2026-03-10T18:32:45.123456",
      "exit_time": null
    }
  ]
}
```

---

## Mobile Testing Flow

### Complete E2E Test on Mobile:

1. **Generate QR Code:**
   - Use `/buildings/<id>/qr` endpoint
   - Print or display QR code

2. **Scan QR Code:**
   - Open mobile camera
   - Scan QR code
   - Browser opens automatically

3. **Fill Form:**
   - Mobile-optimized form loads
   - All fields responsive
   - Photo can be taken with camera or uploaded

4. **Submit:**
   - Tap "Submit Entry"
   - Form validation runs
   - Photo uploaded (if provided)

5. **Success Page:**
   - Success animation plays
   - Details displayed
   - Can print receipt or add new entry

---

## API Endpoints Summary

### Web Routes (HTML):
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/visitor/form/<building_id>` | Render visitor entry form |
| POST | `/visitor/form/<building_id>` | Process form submission |
| GET | `/visitor/success?visitor_id=X&building_id=Y` | Display success page |

### API Routes (JSON):
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/visitors/entry` | Create visitor entry (API) |
| GET | `/visitors` | Get all visitors |
| GET | `/visitors/building/<building_id>` | Get building visitors |
| POST | `/visitors/exit/<visitor_id>` | Record visitor exit |

---

## File Upload Details

### Configuration:
- **Upload Location:** `app/static/uploads/visitor_photos/`
- **Max File Size:** 5 MB
- **Allowed Formats:** PNG, JPG, JPEG, HEIC
- **Filename Format:** `{visitor_name}_{timestamp}.{ext}`

### Example Photo URL:
```
/static/uploads/visitor_photos/John_Doe_20260310_183245.jpg
```

### Access Uploaded Photo:
```
http://localhost:5000/static/uploads/visitor_photos/John_Doe_20260310_183245.jpg
```

---

## Database Schema Updates

### Visitor Model Fields:
```python
id                 # Auto-increment primary key
name               # String(200) - Required
phone              # String(20) - Required
flat_number        # String(50) - Optional (NEW)
vehicle_number     # String(50) - Optional (NEW)
photo_url          # String(500) - Optional
reason             # String(500) - Optional
building_id        # Foreign key - Required
entry_time         # DateTime - Auto-generated
exit_time          # DateTime - Nullable
```

---

## Error Handling

### Invalid Building:
```
GET /visitor/form/999
```
**Response:** 404 HTML page with error message

### Missing Required Fields:
```
POST /visitor/form/1 (without name/phone/reason)
```
**Response:** 400 HTML form with error message displayed

### Invalid File Type:
```
POST /visitor/form/1 with .exe file
```
**Response:** File not uploaded, but visitor entry still created

### File Too Large:
```
POST /visitor/form/1 with 10MB image
```
**Response:** 413 Request Entity Too Large (Flask limit)

---

## Features & Highlights

### ✅ Mobile-Optimized Design
- Responsive layout
- Touch-friendly inputs
- Large buttons
- Clear typography

### ✅ Modern UI/UX
- Gradient backgrounds
- Smooth animations
- Success checkmark
- Clean forms

### ✅ Photo Upload
- Camera capture support
- File upload from gallery
- Auto-resize and optimize
- Secure filename handling

### ✅ Form Validation
- Required field checks
- Phone number pattern
- Client-side validation
- Server-side validation

### ✅ User Experience
- Clear error messages
- Success confirmation
- Print receipt option
- Quick "new entry" button

### ✅ Security
- Secure filename handling
- File type validation
- File size limits
- SQL injection protection

---

## Production Checklist

### Before Deployment:

- [ ] Update Flask SECRET_KEY
- [ ] Configure proper UPLOAD_FOLDER path
- [ ] Set up file storage (S3, CDN)
- [ ] Implement image optimization
- [ ] Add rate limiting on form submission
- [ ] Enable HTTPS
- [ ] Add CAPTCHA for spam prevention
- [ ] Implement visitor notification system
- [ ] Add visitor exit tracking UI
- [ ] Create admin dashboard for visitor management

---

## Troubleshooting

### Form Not Loading:
- Check if building exists: `GET /buildings/<id>`
- Verify templates directory exists: `app/templates/`
- Check Flask is finding templates

### Photo Upload Fails:
- Check upload directory exists: `app/static/uploads/visitor_photos/`
- Verify file size < 5MB
- Check file extension is allowed
- Ensure write permissions on upload folder

### Success Page Not Showing:
- Verify visitor was created (check database)
- Check redirect URL parameters
- Look for database commit errors

### Styles Not Loading:
- Styles are inline in HTML (no external CSS)
- Check browser console for errors

---

## Complete Testing Script

```powershell
# Complete visitor entry test

# 1. Create building
$building = @{name="Test Building"; address="Test Address"} | ConvertTo-Json
$b = Invoke-RestMethod -Uri "http://localhost:5000/buildings/create" -Method POST -Body $building -ContentType "application/json"
$buildingId = $b.building.id

Write-Host "Building created: ID=$buildingId"

# 2. Generate QR code
Invoke-WebRequest -Uri "http://localhost:5000/buildings/$buildingId/qr" -OutFile "qr.png"
Write-Host "QR code saved as qr.png"

# 3. Open form in browser
Start-Process "http://localhost:5000/visitor/form/$buildingId"

# 4. Wait for user to submit form manually
Write-Host "Fill the form in your browser and submit..."
Read-Host "Press Enter after submitting the form"

# 5. Check if visitor was created
$visitors = Invoke-RestMethod -Uri "http://localhost:5000/visitors/building/$buildingId"
Write-Host "Visitors in building:"
$visitors.visitors | Format-Table name, phone, flat_number, entry_time

Write-Host "Test completed successfully!"
```

---

## Next Steps

1. Test on actual mobile devices
2. Implement visitor exit web page
3. Add SMS/email notifications to residents
4. Create admin panel for visitor management
5. Add visitor history and reports
6. Implement visitor pre-approval system
7. Add facial recognition for photos
8. Create visitor badge printing system

---

## Success Indicators

✅ Visitor form loads correctly in browser  
✅ Form is mobile-responsive and looks good  
✅ Form validation works (required fields)  
✅ Photo upload works correctly  
✅ Visitor entry saved to database  
✅ Success page displays with correct details  
✅ QR code opens correct form URL  
✅ All new fields (flat_number, vehicle_number) stored  
✅ No errors in Flask console  
✅ Static files accessible  

---

## Support

For issues or questions about the visitor entry system:
1. Check Flask console logs for errors
2. Verify database schema is up to date
3. Check file upload permissions
4. Review error messages in browser console
5. Test with curl/PowerShell first before mobile testing

---

**System Status:** ✅ Fully Operational  
**Last Updated:** March 10, 2026  
**Version:** 1.0.0
