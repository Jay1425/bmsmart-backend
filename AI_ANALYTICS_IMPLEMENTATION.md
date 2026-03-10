# AI-Powered Visitor Analytics - Implementation Complete

## ✅ Overview

BMSmart now includes an intelligent visitor behavior analytics system that uses AI-style algorithms to detect suspicious patterns and assess security risks.

---

## 📁 Files Created

### 1. [app/services/visitor_ai_service.py](app/services/visitor_ai_service.py)
**VisitorAIService class with 4 methods:**

#### `detect_frequent_visitors(building_id, days=7, threshold=5)`
- Identifies visitors with multiple visits in recent days
- Uses SQLAlchemy GROUP BY and COUNT operations
- Returns list of frequent visitors with visit counts

#### `detect_late_night_visitors(building_id, days=30)`
- Detects entries between 12 AM and 5 AM
- Filters by entry hour (0-5)
- Returns suspicious late-night entries

#### `calculate_visitor_risk_score(phone, building_id=None)`
- **AI-style risk scoring algorithm** (0-100 scale)
- Multi-factor risk assessment:
  - Frequent visits (>5 in 7 days): +30 points
  - Late night entries: +20 points each
  - No flat number: +15 points each
  - Rejected approvals: +25 points each
- Risk levels: minimal, low, medium, high

#### `get_building_analytics_summary(building_id, days=30)`
- Comprehensive building statistics
- Metrics: total visits, unique visitors, late night %, rejection rate
- Analytics dashboard data

---

### 2. [app/routes/ai_routes.py](app/routes/ai_routes.py)
**AI Blueprint (`ai_bp`) with 5 JWT-protected endpoints:**

#### `GET /ai/frequent-visitors/<building_id>`
**Purpose:** Detect frequent visitors

**Query Parameters:**
- `days` (optional): Lookback period (default: 7)
- `threshold` (optional): Minimum visits (default: 5)

**Response:**
```json
{
  "building_id": 1,
  "building_name": "ABC Tower",
  "analysis_period_days": 7,
  "threshold": 5,
  "frequent_visitors": [
    {
      "name": "Rahul",
      "phone": "9999999999",
      "visits_last_week": 12,
      "last_visit": "2026-03-10T14:30:00",
      "first_visit": "2026-03-03T10:00:00"
    }
  ],
  "total_count": 1
}
```

---

#### `GET /ai/late-night-visitors/<building_id>`
**Purpose:** Detect suspicious late-night entries (12 AM - 5 AM)

**Query Parameters:**
- `days` (optional): Lookback period (default: 30)

**Response:**
```json
{
  "building_id": 1,
  "building_name": "ABC Tower",
  "analysis_period_days": 30,
  "late_night_visitors": [
    {
      "id": 123,
      "name": "Suspicious Visitor",
      "phone": "9888888888",
      "flat_number": "A-402",
      "entry_time": "2026-03-10T02:30:00",
      "entry_hour": 2,
      "reason": "Emergency",
      "approval_status": "pending"
    }
  ],
  "total_count": 1
}
```

---

#### `GET /ai/visitor-risk/<phone>`
**Purpose:** Calculate AI-powered risk score for a visitor

**Query Parameters:**
- `building_id` (optional): Limit to specific building

**Response:**
```json
{
  "phone": "9999999999",
  "name": "Rahul",
  "risk_score": 65,
  "risk_level": "medium",
  "total_visits": 15,
  "recent_visits_7_days": 8,
  "late_night_entries": 2,
  "no_flat_entries": 0,
  "rejected_approvals": 1,
  "risk_factors": [
    "Frequent visitor: 8 visits in last 7 days",
    "Late night entries: 2 times",
    "Rejected approvals: 1 times"
  ],
  "last_visit": "2026-03-10T14:30:00",
  "buildings_visited": [1, 2]
}
```

**Risk Levels:**
- **minimal:** 0-19 points
- **low:** 20-39 points
- **medium:** 40-69 points
- **high:** 70-100 points

---

#### `GET /ai/building-analytics/<building_id>`
**Purpose:** Comprehensive building analytics dashboard

**Query Parameters:**
- `days` (optional): Analysis period (default: 30)

**Response:**
```json
{
  "building_id": 1,
  "building_name": "ABC Tower",
  "analysis_period_days": 30,
  "total_visits": 450,
  "unique_visitors": 120,
  "avg_visits_per_day": 15.0,
  "late_night_visits": 12,
  "late_night_percentage": 2.67,
  "no_flat_number": 25,
  "no_flat_percentage": 5.56,
  "pending_approvals": 10,
  "approved_visits": 400,
  "rejected_visits": 40,
  "rejection_rate": 8.89
}
```

---

#### `GET /ai/high-risk-visitors/<building_id>`
**Purpose:** Identify high-risk visitors

**Query Parameters:**
- `days` (optional): Lookback period (default: 30)
- `min_risk_score` (optional): Minimum score (default: 70)

**Response:**
```json
{
  "building_id": 1,
  "building_name": "ABC Tower",
  "analysis_period_days": 30,
  "min_risk_score": 70,
  "high_risk_visitors": [
    {
      "phone": "9888888888",
      "name": "Suspicious Person",
      "risk_score": 85,
      "risk_level": "high",
      "total_visits": 20,
      "risk_factors": [
        "Frequent visitor: 15 visits in last 7 days",
        "Late night entries: 5 times",
        "No flat number specified: 10 times"
      ]
    }
  ],
  "total_count": 1
}
```

---

## 🧠 AI Risk Scoring Algorithm

### Risk Calculation Formula

```python
risk_score = 0

# Factor 1: Frequent Visits
if visits_last_7_days > 5:
    risk_score += 30

# Factor 2: Late Night Entries
risk_score += (late_night_count * 20)

# Factor 3: No Flat Number
risk_score += (no_flat_count * 15)

# Factor 4: Rejected Approvals
risk_score += (rejected_count * 25)

# Cap at 100
risk_score = min(risk_score, 100)
```

### Risk Level Classification

| Score Range | Risk Level | Action Recommended |
|-------------|------------|-------------------|
| 0-19 | Minimal | Normal monitoring |
| 20-39 | Low | Standard verification |
| 40-69 | Medium | Enhanced screening |
| 70-100 | High | Security alert, special approval |

---

## 🔐 Security & Authentication

**All AI analytics endpoints require JWT authentication:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Protected Features:**
- ✅ All endpoints use `@jwt_required()` decorator
- ✅ Building validation (404 if not found)
- ✅ Role-based access ready for future enhancement
- ✅ Secure analytics data access

---

## 📊 Use Cases

### 1. Security Dashboard
Display high-risk visitors to security staff:
```
GET /ai/high-risk-visitors/1?min_risk_score=70
→ Show top security threats
```

### 2. Building Manager Analytics
Monitor building patterns:
```
GET /ai/building-analytics/1?days=30
→ Monthly visitor trends and statistics
```

### 3. Visitor Screening
Check individual visitor risk:
```
GET /ai/visitor-risk/9999999999
→ Risk score before approval
```

### 4. Suspicious Activity Alerts
Identify unusual patterns:
```
GET /ai/late-night-visitors/1
GET /ai/frequent-visitors/1
→ Flag suspicious behavior
```

### 5. Compliance Reporting
Generate periodic reports:
```
GET /ai/building-analytics/1?days=90
→ Quarterly security reports
```

---

## 🧪 Testing

### Run Automated Tests
```bash
# Start server
python run.py

# In another terminal
python test_ai_analytics.py
```

### Test Scenarios Covered
1. ✅ Frequent visitor detection (>5 visits)
2. ✅ Late-night entry detection (12 AM - 5 AM)
3. ✅ Risk scoring for multiple visitor profiles
4. ✅ Building analytics summary
5. ✅ High-risk visitor identification
6. ✅ Multi-factor risk assessment

### Expected Test Results
- **Rahul (Frequent):** Risk score ~30-50 (8 visits)
- **Amit (Suspicious):** Risk score ~60-90 (6 visits, no flat)
- **Priya (Normal):** Risk score ~0-20 (2 visits)
- **Sneha (One-time):** Risk score ~0 (1 visit)

---

## 📱 Mobile App Integration

### Security Staff Dashboard

**1. High-Risk Visitors Widget**
```kotlin
// Fetch high-risk visitors
val response = apiClient.get("/ai/high-risk-visitors/$buildingId?min_risk_score=70")

// Display in red alert card
highRiskList.adapter = HighRiskAdapter(response.high_risk_visitors)
```

**2. Visitor Risk Badge**
```kotlin
// Show risk score when reviewing visitor entry
val riskData = apiClient.get("/ai/visitor-risk/${visitor.phone}")

when (riskData.risk_level) {
    "high" -> visitorCard.setBackgroundColor(Color.RED)
    "medium" -> visitorCard.setBackgroundColor(Color.ORANGE)
    "low" -> visitorCard.setBackgroundColor(Color.YELLOW)
    "minimal" -> visitorCard.setBackgroundColor(Color.GREEN)
}
```

**3. Analytics Dashboard**
```kotlin
// Building manager overview
val analytics = apiClient.get("/ai/building-analytics/$buildingId?days=30")

statsCard.totalVisits.text = analytics.total_visits.toString()
statsCard.avgPerDay.text = analytics.avg_visits_per_day.toString()
statsCard.lateNightPercent.text = "${analytics.late_night_percentage}%"
```

---

## 🎯 API Quick Reference

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/ai/frequent-visitors/<id>` | GET | JWT | Detect frequent visitors |
| `/ai/late-night-visitors/<id>` | GET | JWT | Find late-night entries |
| `/ai/visitor-risk/<phone>` | GET | JWT | Calculate risk score |
| `/ai/building-analytics/<id>` | GET | JWT | Building statistics |
| `/ai/high-risk-visitors/<id>` | GET | JWT | Identify high-risk visitors |

---

## 🚀 Performance Considerations

### Database Optimization
- ✅ Efficient GROUP BY queries for aggregations
- ✅ Indexed columns (building_id, phone, entry_time)
- ✅ Single query results (no N+1 problems)
- ✅ Date range filtering for fast lookups

### Caching Opportunities
Consider caching for production:
- Building analytics (update every 5 minutes)
- High-risk visitors list (update every 10 minutes)
- Risk scores (cache per visitor for 1 hour)

### Scalability
- Queries optimized for large datasets
- Risk calculations run on-demand
- Analytics computed from filtered datasets
- No expensive joins or nested queries

---

## 📈 Future Enhancements

### 1. Machine Learning Integration
- Train ML model on historical patterns
- Predict visitor intent
- Anomaly detection algorithms
- Behavioral clustering

### 2. Real-Time Alerts
- WebSocket notifications for high-risk entries
- SMS/Email alerts for security staff
- Push notifications for critical events

### 3. Advanced Analytics
- Time-series analysis
- Peak hour detection
- Visitor relationship mapping
- Building comparison analytics

### 4. Custom Risk Weights
- Allow admins to configure risk factors
- Building-specific thresholds
- Role-based risk assessment
- Whitelist/Blacklist management

### 5. Historical Trend Analysis
- Month-over-month comparisons
- Seasonal pattern detection
- Predictive analytics
- Security effectiveness metrics

---

## ✅ Implementation Checklist

- [x] VisitorAIService created with 4 core methods
- [x] AI routes blueprint with 5 endpoints
- [x] Risk scoring algorithm implemented (0-100 scale)
- [x] Frequent visitor detection
- [x] Late-night visitor detection
- [x] Building analytics summary
- [x] High-risk visitor identification
- [x] JWT authentication on all endpoints
- [x] Building validation and error handling
- [x] Comprehensive test script
- [x] Complete documentation
- [x] Blueprint registered in app factory
- [x] Services and routes packages updated

---

## 🎉 Summary

**Status:** ✅ Complete and Production-Ready

**Key Features:**
- 🤖 AI-powered risk scoring (0-100 scale)
- 🔍 Intelligent pattern detection
- 📊 Comprehensive analytics dashboard
- 🚨 High-risk visitor identification
- 🌙 Late-night activity monitoring
- ⚡ Frequent visitor detection
- 🎯 Multi-factor risk assessment

**Benefits:**
- Enhanced security monitoring
- Proactive threat detection
- Data-driven decision making
- Automated suspicious activity alerts
- Compliance and reporting support
- Improved building safety

**Ready for:**
- Mobile app integration
- Security staff dashboards
- Building manager reports
- Real-time monitoring systems
- Future ML enhancements

---

**Implementation Date:** March 10, 2026  
**BMSmart Version:** 2.2  
**Module:** AI-Powered Visitor Analytics  
**Status:** ✅ Fully Operational
