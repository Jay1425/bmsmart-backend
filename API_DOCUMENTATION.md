# BMSmart Backend API Documentation

## Overview
RESTful API for the BMSmart building management system built with Flask.

## Running the Application

```bash
python run.py
```

The server will start at `http://0.0.0.0:5000` in debug mode.

## Database
- SQLite database (bmsmart.db) created automatically on first run
- All tables are created automatically via SQLAlchemy

## API Endpoints

### Buildings

#### Create Building
- **POST** `/buildings/create`
- **Body:**
```json
{
  "name": "Tower A",
  "address": "123 Main Street",
  "city": "New York"    
}
```

#### Get All Buildings
- **GET** `/buildings`

#### Get Building QR Entry URL
- **GET** `/buildings/<building_id>/entry-url`
- **Description:** Get the permanent QR code entry URL for a building
- **Response:**
```json
{
  "building_id": 1,
  "entry_url": "/visitor/entry/1"
}
```

#### Generate Building QR Code
- **GET** `/buildings/<building_id>/qr`
- **Description:** Generate QR code image for building visitor entry
- **Response:** PNG image file
- **Usage Example:**
  ```bash
  curl http://localhost:5000/buildings/1/qr -o building_qr.png
  ```
- **QR Code Content:** Encodes `http://localhost:5000/visitor/entry/{building_id}`

---

### Public Visitor Form (QR Code Flow)

#### Get Visitor Form Data
- **GET** `/visitor/form/<building_id>`
- **Description:** Anonymous endpoint for visitors to get building info after scanning QR
- **Response:**
```json
{
  "building_id": 1,
  "building_name": "Tower A"
}
```

#### Get Entry Page Info
- **GET** `/visitor/entry/<building_id>`
- **Description:** Direct entry URL from QR code
- **Response:**
```json
{
  "building_id": 1,
  "building_name": "Tower A",
  "message": "Use POST /visitors/entry to submit visitor information"
}
```


#### Get All Users
- **GET** `/users`

#### Get User by ID
- **GET** `/users/<id>`

---

### Visitors

#### Record Visitor Entry
- **POST** `/visitors/entry`
- **Description:** Record a new visitor entry (entry_time set automatically)
- **Body:**
```json
{
  "name": "Jane Smith",
  "phone": "9876543210",
  "photo_url": "https://example.com/photo.jpg",
  "reason": "Meeting with resident",
  "building_id": 1
}
```
- **Response:**
```json
{
  "message": "Visitor entry recorded successfully",
  "visitor": {
    "id": 1,
    "name": "Jane Smith",
    "phone": "9876543210",
    "photo_url": "https://example.com/photo.jpg",
    "reason": "Meeting with resident",
    "building_id": 1,
    "entry_time": "2026-03-10T17:30:00.000000",
    "exit_time": null
  }
}
```

#### Record Visitor Exit
- **POST** `/visitors/exit/<visitor_id>`
- **Description:** Record visitor exit (exit_time set automatically)
- **Response:**
```json
{
  "message": "Visitor exit recorded successfully",
  "visitor": {
    "id": 1,
    "name": "Jane Smith",
    "phone": "9876543210",
    "photo_url": "https://example.com/photo.jpg",
    "reason": "Meeting with resident",
    "building_id": 1,
    "entry_time": "2026-03-10T17:30:00.000000",
    "exit_time": "2026-03-10T18:00:00.000000"
  }
}
```

#### Get All Visitors
- **GET** `/visitors`

#### Get Visitors by Building
- **GET** `/visitors/building/<building_id>`

---

### Payments

#### Create Payment
- **POST** `/payments/create`
- **Body:**
```json
{
  "user_id": 1,
  "amount": 1500.00,
  "purpose": "Monthly maintenance",
  "status": "pending"
}
```
- **Status:** `pending`, `paid`

#### Get All Payments
- **GET** `/payments`

#### Get Payments by User
- **GET** `/payments/user/<user_id>`

---

### Complaints

#### Create Complaint
- **POST** `/complaints/create`
- **Body:**
```json
{
  "user_id": 1,
  "title": "Water leakage",
  "description": "There is water leaking from the ceiling",
  "status": "open"
}
```
- **Status:** `open`, `in_progress`, `resolved`

#### Get All Complaints
- **GET** `/complaints`

#### Get Complaints by User
- **GET** `/complaints/user/<user_id>`

---

### Analytics

#### Get Visitor Analytics
- **GET** `/analytics/visitors/<building_id>`
- **Description:** Get visitor analytics for a specific building
- **Response:**
```json
{
  "today": 15,
  "this_week": 84,
  "inside": 3
}
```
- **Fields:**
  - `today` - Number of visitors who entered today (since midnight UTC)
  - `this_week` - Number of visitors who entered this week (since Monday)
  - `inside` - Number of visitors currently inside (no exit_time recorded)

---

## Models

### Building
- id (PK)
- name
- address
- city
- created_at
- **Relationships:** has many users, has many visitors

### User
- id (PK)
- name
- email (unique)
- phone
- password
- role
- building_id (FK)
- created_at
- **Relationships:** belongs to building, has many payments, has many complaints

### Visitor
- id (PK)
- name
- phone
- photo_url
- reason
- building_id (FK)
- entry_time
- exit_time
- **Relationships:** belongs to building

### Payment
- id (PK)
- user_id (FK)
- amount
- purpose
- status
- created_at
- **Relationships:** belongs to user

### Complaint
- id (PK)
- user_id (FK)
- title
- description
- status
- created_at
- **Relationships:** belongs to user

---

## QR Visitor Entry Flow

The BMSmart backend supports permanent QR code-based visitor entry:

### Flow Overview

1. **Building Manager Generates QR Code**
   - Call `GET /buildings/{id}/entry-url` to get the permanent entry URL
   - Encode the `entry_url` into a QR code
   - Display QR code at building entrance

2. **Visitor Scans QR Code**
   - QR code redirects to `/visitor/entry/{building_id}`
   - Frontend app calls `GET /visitor/form/{building_id}` to load building info

3. **Visitor Fills Entry Form**
   - Form collects: name, phone, reason, optional photo
   - Submit to `POST /visitors/entry` with building_id
   - `entry_time` is automatically set to current timestamp

4. **Visitor Inside Building**
   - Security can view active visitors via `GET /visitors/building/{building_id}`
   - Visitors without `exit_time` are currently inside

5. **Visitor Exits**
   - Call `POST /visitors/exit/{visitor_id}`
   - `exit_time` is automatically set to current timestamp

6. **View Visitor History**
   - Complete visitor log maintained in database
   - Query by building, time range, or visitor status

### Key Features

- ✅ **Permanent QR Codes**: Each building has a stable entry URL
- ✅ **Automatic Timestamps**: Entry and exit times set automatically
- ✅ **Anonymous Access**: Visitors don't need accounts
- ✅ **Real-time Tracking**: See who's currently in the building
- ✅ **Complete History**: All entries and exits logged

---

## Project Structure

```
bmsmart-backend/
├── app/
│   ├── __init__.py           # Application factory
│   ├── config.py             # Configuration classes
│   ├── extensions.py         # Flask extensions (db, cors)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── building_model.py
│   │   ├── user_model.py
│   │   ├── visitor_model.py
│   │   ├── payment_model.py
│   │   └── complaint_model.py
│   └── routes/
│       ├── __init__.py
│       ├── building_routes.py
│       ├── user_routes.py
│       ├── visitor_routes.py
│       ├── visitor_form_routes.py
│       ├── payment_routes.py
│       ├── complaint_routes.py
│       └── analytics_routes.py
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── README.md
```

## Testing with cURL

### Create a building:
```bash
curl -X POST http://localhost:5000/buildings/create \
  -H "Content-Type: application/json" \
  -d '{"name":"Tower A","address":"123 Main St","city":"New York"}'
```

### Get all buildings:
```bash
curl http://localhost:5000/buildings
```

### Get building QR entry URL:
```bash
curl http://localhost:5000/buildings/1/entry-url
```

### Generate building QR code:
```bash
curl http://localhost:5000/buildings/1/qr -o building_1_qr.png
```

### Get visitor analytics:
```bash
curl http://localhost:5000/analytics/visitors/1
```

### Get visitor form (QR flow):
```bash
curl http://localhost:5000/visitor/form/1
```

### Record visitor entry:
```bash
curl -X POST http://localhost:5000/visitors/entry \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Visitor","phone":"9876543210","reason":"Meeting","building_id":1}'
```

### Record visitor exit:
```bash
curl -X POST http://localhost:5000/visitors/exit/1
```

### Get visitors for building:
```bash
curl http://localhost:5000/visitors/building/1
```

### Register a user:
```bash
curl -X POST http://localhost:5000/users/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","phone":"1234567890","password":"pass123","building_id":1}'
```

## Testing QR Visitor Flow

See [QR_VISITOR_TESTING.md](QR_VISITOR_TESTING.md) for comprehensive testing guide with expected responses.

## Error Handling
All endpoints return JSON responses with appropriate HTTP status codes:
- `200` - Success (GET)
- `201` - Created (POST)
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `500` - Server Error
