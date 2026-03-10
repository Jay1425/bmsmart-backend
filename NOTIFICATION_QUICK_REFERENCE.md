# BMSmart Notification System - Quick Reference

## 🔔 Notification API Endpoints

All endpoints require JWT authentication unless specified.

---

### 1️⃣ Register Device Token

**Endpoint:** `POST /notifications/register-device`

**Purpose:** Store FCM device token for push notifications

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body:**
```json
{
  "device_token": "fcm_device_token_from_mobile_app"
}
```

**Success Response (200):**
```json
{
  "message": "Device token registered successfully",
  "user_id": 1
}
```

**When to call:** 
- On app launch after user login
- When FCM token refreshes
- After re-login

---

### 2️⃣ Get My Notifications

**Endpoint:** `GET /notifications/my`

**Purpose:** Retrieve notifications for current user

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Query Parameters:**
- `unread_only` (optional): `true` or `false` (default: `false`)
- `limit` (optional): Number of notifications (default: `50`)

**Examples:**
```
GET /notifications/my
GET /notifications/my?unread_only=true
GET /notifications/my?limit=20
GET /notifications/my?unread_only=true&limit=10
```

**Success Response (200):**
```json
{
  "notifications": [
    {
      "id": 1,
      "user_id": 5,
      "title": "Visitor Arrived",
      "message": "Rahul is waiting at the gate for A-402",
      "visitor_id": 12,
      "created_at": "2026-03-10T14:30:00",
      "is_read": false
    }
  ],
  "total": 1
}
```

**When to call:**
- On app launch
- When notification icon is tapped
- Pull-to-refresh in notifications screen

---

### 3️⃣ Mark Notification as Read

**Endpoint:** `POST /notifications/read/<notification_id>`

**Purpose:** Mark a single notification as read

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Success Response (200):**
```json
{
  "message": "Notification marked as read",
  "notification": {
    "id": 1,
    "is_read": true,
    ...
  }
}
```

**Error Response (403):**
```json
{
  "error": "Unauthorized access to notification"
}
```

**Error Response (404):**
```json
{
  "error": "Notification not found"
}
```

**When to call:**
- When user taps on a notification
- When notification details are viewed

---

### 4️⃣ Mark All Notifications as Read

**Endpoint:** `POST /notifications/mark-all-read`

**Purpose:** Mark all user's notifications as read

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Success Response (200):**
```json
{
  "message": "5 notification(s) marked as read",
  "count": 5
}
```

**When to call:**
- "Mark all as read" button
- Clear all notifications action

---

## 🚶 Visitor Entry (Auto-sends Notification)

**Endpoint:** `POST /visitors/entry`

**Purpose:** Create visitor entry (automatically sends notification to residents)

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Rahul Kumar",
  "phone": "9876543210",
  "building_id": 1,
  "flat_number": "A-402",
  "vehicle_number": "MH01AB1234",
  "reason": "Social visit",
  "photo_url": "https://example.com/photo.jpg"
}
```

**Success Response (201):**
```json
{
  "message": "Visitor entry recorded successfully",
  "visitor": {
    "id": 12,
    "name": "Rahul Kumar",
    ...
  },
  "notification_sent": true
}
```

**Notification Created:**
- Title: "Visitor Arrived"
- Message: "Rahul Kumar is waiting at the gate for A-402"
- Sent to: All residents in the building with device tokens

---

## 📱 Mobile App Integration Flow

### Initial Setup (After Login)
```
1. User logs in → Receive JWT token
2. Get FCM device token from Firebase
3. POST /notifications/register-device with token
4. Store JWT token for future requests
```

### Receiving Notifications
```
1. Visitor arrives at gate
2. Backend sends FCM push notification
3. Mobile app receives notification via Firebase
4. App displays notification in system tray
5. User taps → App opens to notification details
```

### Viewing Notifications
```
1. User opens notifications screen
2. GET /notifications/my
3. Display list of notifications
4. Show unread count badge
5. When user taps notification → POST /notifications/read/<id>
```

---

## 🔐 Authentication

All notification endpoints require JWT token in Authorization header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

Get JWT token from:
- `POST /auth/login` (returns access_token)
- `POST /auth/register` (returns access_token)

---

## 🎯 Notification Data Structure

```typescript
interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  visitor_id: number | null;
  created_at: string;  // ISO 8601 format
  is_read: boolean;
}
```

---

## 🚨 Error Responses

### 400 Bad Request
```json
{
  "error": "device_token is required"
}
```

### 401 Unauthorized
```json
{
  "msg": "Missing Authorization Header"
}
```

### 403 Forbidden
```json
{
  "error": "Unauthorized access to notification"
}
```

### 404 Not Found
```json
{
  "error": "Notification not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Database error message"
}
```

---

## 🧪 Testing with cURL

### Register Device Token
```bash
curl -X POST http://localhost:5000/notifications/register-device \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"device_token": "test_fcm_token_123"}'
```

### Get Notifications
```bash
curl -X GET http://localhost:5000/notifications/my \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Unread Notifications
```bash
curl -X GET "http://localhost:5000/notifications/my?unread_only=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Mark Notification as Read
```bash
curl -X POST http://localhost:5000/notifications/read/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Create Visitor Entry (triggers notification)
```bash
curl -X POST http://localhost:5000/visitors/entry \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Visitor",
    "phone": "9876543210",
    "building_id": 1,
    "flat_number": "A-402",
    "reason": "Social visit"
  }'
```

---

## 📊 Database Schema

### notifications table
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| user_id | INTEGER | NOT NULL, FK → users.id |
| title | VARCHAR(200) | NOT NULL |
| message | TEXT | NOT NULL |
| visitor_id | INTEGER | NULLABLE, FK → visitors.id |
| created_at | DATETIME | NOT NULL, DEFAULT now() |
| is_read | BOOLEAN | NOT NULL, DEFAULT FALSE |

### users table (updated)
| Column | Type | Constraints |
|--------|------|-------------|
| ... | ... | ... |
| device_token | VARCHAR(500) | NULLABLE |

---

## 🔥 Firebase Setup

1. Create Firebase project at https://console.firebase.google.com/
2. Add Android/iOS app to project
3. Download google-services.json (Android) or GoogleService-Info.plist (iOS)
4. Generate service account key:
   - Project Settings → Service Accounts
   - Generate New Private Key
   - Save as `firebase-credentials.json`
5. Set environment variable (optional):
   ```bash
   export FIREBASE_CREDENTIALS_PATH="/path/to/firebase-credentials.json"
   ```

---

## ✅ Test Checklist

- [ ] Install firebase-admin: `pip install firebase-admin`
- [ ] Place firebase-credentials.json in project root
- [ ] Start server: `python run.py`
- [ ] Run test script: `python test_notification_system.py`
- [ ] Register device token via API
- [ ] Create visitor entry
- [ ] Verify notification created in database
- [ ] Check FCM push notification sent (if configured)
- [ ] Retrieve notifications via API
- [ ] Mark notification as read
- [ ] Test unread filter
- [ ] Test on actual mobile device

---

## 🎓 Best Practices

1. **Register token on every app launch**
   - FCM tokens can expire or change
   - Always update on app start

2. **Handle token refresh**
   - Listen for FCM token refresh events
   - Update backend immediately

3. **Show notification badge**
   - Display unread count on notification icon
   - Update when notifications received

4. **Mark as read appropriately**
   - When notification is tapped
   - When notification details viewed
   - Not just on notification receipt

5. **Error handling**
   - Gracefully handle network errors
   - Retry failed token registrations
   - Show user-friendly error messages

6. **Notification persistence**
   - Notifications stored in database
   - Available even if push fails
   - Can be retrieved anytime via API

---

## 📞 Support

For issues or questions:
1. Check server logs for errors
2. Verify Firebase credentials are valid
3. Test with curl commands first
4. Review NOTIFICATION_SYSTEM_IMPLEMENTATION.md for detailed guide
5. Check mobile app has notification permissions

---

**Last Updated:** March 10, 2026  
**BMSmart Backend Version:** 2.0  
**Notification System Version:** 1.0
