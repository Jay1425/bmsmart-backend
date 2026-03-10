# Security Module - Quick Reference

## 🔐 Security Dashboard API Endpoints

All endpoints require JWT authentication via `Authorization: Bearer TOKEN`

### Dashboard Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/security/visitors/today/<building_id>` | GET | Get today's visitors |
| `/security/visitors/inside/<building_id>` | GET | Get visitors currently inside |
| `/security/visitors/recent/<building_id>` | GET | Get last 20 visitors |
| `/security/visitors/pending/<building_id>` | GET | Get pending approval visitors |
| `/security/visitors/stats/<building_id>` | GET | Get visitor statistics |

### Action Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/security/visitor/approve/<visitor_id>` | POST | Approve visitor entry |
| `/security/visitor/reject/<visitor_id>` | POST | Reject visitor entry |
| `/security/visitor/force-exit/<visitor_id>` | POST | Force visitor exit |

## 📊 Response Examples

### Get Today's Visitors
```json
{
  "building_id": 1,
  "building_name": "Tower A",
  "date": "2026-03-10",
  "total_count": 5,
  "visitors": [
    {
      "id": 1,
      "name": "John Doe",
      "phone": "9876543210",
      "flat_number": "A-101",
      "reason": "Delivery",
      "approval_status": "pending",
      "entry_time": "2026-03-10T10:30:00",
      "exit_time": null
    }
  ]
}
```

### Get Statistics
```json
{
  "building_id": 1,
  "building_name": "Tower A",
  "stats": {
    "total_today": 15,
    "currently_inside": 8,
    "pending_approval": 3,
    "approved": 10,
    "rejected": 2
  }
}
```

### Approve Visitor
```json
{
  "message": "Visitor approved successfully",
  "visitor": {
    "id": 1,
    "name": "John Doe",
    "approval_status": "approved",
    "approved_by": 2,
    "approval_time": "2026-03-10T10:35:00"
  }
}
```

## 🚀 Quick Start

### 1. Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"security@example.com","password":"password123"}'
```

### 2. Get Today's Visitors
```bash
curl http://localhost:5000/security/visitors/today/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Approve Visitor
```bash
curl -X POST http://localhost:5000/security/visitor/approve/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📋 Database Fields

### Visitor Model (New Fields)
- `approval_status` - Values: pending, approved, rejected
- `approved_by` - User ID who approved/rejected
- `approval_time` - Timestamp of approval/rejection

## ⚡ Features

✅ JWT-protected security endpoints  
✅ Real-time visitor monitoring  
✅ Approval workflow tracking  
✅ Force exit capability  
✅ Rate limiting (5-minute window)  
✅ Comprehensive statistics  
✅ Audit trail (who approved/rejected)  
✅ Multi-building support  

## 📝 Testing

Run the test script:
```bash
python test_security_module.py
```

## 📚 Full Documentation

See [SECURITY_MODULE_IMPLEMENTATION_SUMMARY.md](SECURITY_MODULE_IMPLEMENTATION_SUMMARY.md) for complete details.
