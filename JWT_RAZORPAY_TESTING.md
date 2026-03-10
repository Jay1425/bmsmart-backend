# JWT Authentication & Razorpay Payment Integration - Testing Guide

## Overview
BMSmart backend now includes JWT-based authentication and Razorpay payment gateway integration.

---

## Start the Server

```bash
python run.py
```

Server at: `http://localhost:5000`

---

## JWT Authentication Testing

### 1. Register a New User

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "password": "password123",
    "building_id": 1,
    "role": "resident"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "role": "resident",
    "building_id": 1
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Save the `access_token` for subsequent requests!**

---

### 2. Login with Existing User

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {...},
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 3. Get Current User Profile

```bash
curl -X GET http://localhost:5000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "resident",
    "building_id": 1
  }
}
```

---

### 4. Refresh Access Token

```bash
curl -X POST http://localhost:5000/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Protected Routes Testing

### Test JWT Protection

#### Without Token (Should Fail):
```bash
curl -X GET http://localhost:5000/users
```

**Expected:** 401 Unauthorized - Missing Authorization Header

#### With Valid Token (Success):
```bash
curl -X GET http://localhost:5000/users \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected:** 200 OK - Returns user list

---

## Razorpay Payment Integration Testing

### 1. Create Razorpay Order

**Requires JWT Token**

```bash
curl -X POST http://localhost:5000/payments/create-order \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "amount": 1500.00,
    "purpose": "Monthly maintenance fee"
  }'
```

**Response:**
```json
{
  "message": "Razorpay order created successfully",
  "order_id": "order_K1rLF9qQtODm4Y",
  "amount": 1500.0,
  "currency": "INR",
  "payment_id": 1,
  "razorpay_key": "rzp_test_key"
}
```

**Save the `order_id` for payment verification!**

---

### 2. Verify Payment

**After successful payment on mobile app, verify with backend:**

```bash
curl -X POST http://localhost:5000/payments/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "razorpay_order_id": "order_K1rLF9qQtODm4Y",
    "razorpay_payment_id": "pay_K1rLF9qQtODm4Z",
    "razorpay_signature": "d8f1b8f3c8f3b8f3c8f3b8f3c8f3b8f3",
    "payment_method": "upi"
  }'
```

**Response (Success):**
```json
{
  "message": "Payment verified successfully",
  "status": "paid",
  "payment": {
    "id": 1,
    "user_id": 1,
    "amount": 1500.0,
    "purpose": "Monthly maintenance fee",
    "status": "paid",
    "razorpay_order_id": "order_K1rLF9qQtODm4Y",
    "razorpay_payment_id": "pay_K1rLF9qQtODm4Z",
    "payment_method": "upi"
  }
}
```

**Response (Invalid Signature):**
```json
{
  "error": "Invalid signature",
  "status": "failed"
}
```

---

## PowerShell Testing Commands

### 1. Register User
```powershell
$user = @{
    name = "John Doe"
    email = "john@example.com"
    phone = "1234567890"
    password = "password123"
    building_id = 1
    role = "resident"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/auth/register" `
    -Method POST -Body $user -ContentType "application/json"

# Save token
$token = $response.access_token
Write-Host "Access Token: $token"
```

### 2. Login
```powershell
$credentials = @{
    email = "john@example.com"
    password = "password123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/auth/login" `
    -Method POST -Body $credentials -ContentType "application/json"

$token = $response.access_token
```

### 3. Get Current User
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:5000/auth/me" `
    -Method GET -Headers $headers
```

### 4. Create Razorpay Order
```powershell
$order = @{
    amount = 1500.00
    purpose = "Monthly maintenance"
} | ConvertTo-Json

$headers = @{
    Authorization = "Bearer $token"
}

$response = Invoke-RestMethod -Uri "http://localhost:5000/payments/create-order" `
    -Method POST -Body $order -ContentType "application/json" -Headers $headers

Write-Host "Order ID: $($response.order_id)"
```

### 5. Verify Payment
```powershell
$verification = @{
    razorpay_order_id = "order_K1rLF9qQtODm4Y"
    razorpay_payment_id = "pay_K1rLF9qQtODm4Z"
    razorpay_signature = "d8f1b8f3c8f3b8f3c8f3b8f3c8f3b8f3"
    payment_method = "upi"
} | ConvertTo-Json

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:5000/payments/verify" `
    -Method POST -Body $verification -ContentType "application/json" -Headers $headers
```

---

## Complete Mobile App Flow

### Step 1: User Registration/Login
```
Mobile App → POST /auth/register or /auth/login
← Returns: access_token, refresh_token, user data
```

### Step 2: Store Tokens
```
Mobile App: Save tokens in secure storage (Keychain/KeyStore)
```

### Step 3: Create Payment Order
```
Mobile App → POST /payments/create-order
Headers: Authorization: Bearer {access_token}
Body: { amount, purpose }
← Returns: order_id, razorpay_key, payment_id
```

### Step 4: Open Razorpay Checkout
```
Mobile App: Initialize Razorpay SDK
- Use order_id from Step 3
- Use razorpay_key from Step 3
- User completes payment
← Razorpay returns: payment_id, signature
```

### Step 5: Verify Payment with Backend
```
Mobile App → POST /payments/verify
Headers: Authorization: Bearer {access_token}
Body: { 
  razorpay_order_id,
  razorpay_payment_id,
  razorpay_signature,
  payment_method
}
← Backend verifies signature and updates payment status
← Returns: payment details with status "paid"
```

### Step 6: Show Success/Failure
```
Mobile App: Display payment confirmation
- Success: Show receipt, payment details
- Failure: Show error, retry option
```

---

## JWT Protected Endpoints

### Automatically Protected:
- `GET /auth/me` - Get current user
- `POST /auth/refresh` - Refresh token
- `GET /users` - Get all users
- `GET /users/<id>` - Get user by ID
- `POST /complaints/create` - Create complaint (uses logged-in user)
- `GET /complaints` - Get all complaints
- `GET /complaints/user/<user_id>` - Get user complaints
- `POST /payments/create-order` - Create Razorpay order
- `POST /payments/verify` - Verify payment

### Public Endpoints (No JWT Required):
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /buildings/create` - Create building
- `GET /buildings` - Get all buildings
- `GET /buildings/<id>/qr` - Generate QR code
- `POST /visitors/entry` - Visitor entry (public for QR flow)
- `GET /visitor/form/<building_id>` - Visitor form (public)
- `GET /analytics/visitors/<building_id>` - Analytics (consider protecting)

---

## Error Cases

### 1. Invalid Credentials
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"wrong@example.com","password":"wrong"}'
```
**Expected:** 401 - Invalid email or password

### 2. Expired Token
```bash
curl -X GET http://localhost:5000/auth/me \
  -H "Authorization: Bearer EXPIRED_TOKEN"
```
**Expected:** 401 - Token has expired

### 3. Missing Authorization Header
```bash
curl -X GET http://localhost:5000/users
```
**Expected:** 401 - Missing Authorization Header

### 4. Invalid Razorpay Signature
```bash
curl -X POST http://localhost:5000/payments/verify \
  -H "Authorization: Bearer TOKEN" \
  -d '{"razorpay_order_id":"order_123","razorpay_payment_id":"pay_123","razorpay_signature":"invalid"}'
```
**Expected:** 400 - Invalid signature, status: failed

---

## Environment Variables

Create a `.env` file in project root:

```env
# Flask
SECRET_KEY=your-super-secret-key-here
FLASK_CONFIG=development

# JWT
JWT_SECRET_KEY=your-jwt-secret-key-here

# Razorpay (Test Mode)
RAZORPAY_KEY_ID=rzp_test_YOUR_KEY_ID
RAZORPAY_KEY_SECRET=YOUR_SECRET_KEY

# Database
DATABASE_URL=sqlite:///bmsmart.db

# CORS
CORS_ORIGINS=*
```

**Get Razorpay Test Keys:**
1. Sign up at https://razorpay.com
2. Go to Settings → API Keys
3. Generate Test Keys
4. Use test keys for development

---

## Security Notes

### Password Security
- Passwords are hashed using Werkzeug's `generate_password_hash()`
- Never store plain text passwords
- Passwords are NOT returned in API responses

### JWT Tokens
- Access tokens expire after 24 hours
- Refresh tokens expire after 30 days
- Tokens are signed with JWT_SECRET_KEY
- Always use HTTPS in production

### Razorpay Security
- Signatures are verified using HMAC-SHA256
- Payment status updated only after signature verification
- Razorpay secrets never exposed to client
- All payment routes require JWT authentication

---

## Production Checklist

### Before deploying:
- [ ] Change SECRET_KEY and JWT_SECRET_KEY to strong random values
- [ ] Use production Razorpay keys (not test keys)
- [ ] Enable HTTPS/SSL
- [ ] Set proper CORS_ORIGINS (not '*')
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable rate limiting on auth endpoints
- [ ] Set up proper logging
- [ ] Add email verification for registration
- [ ] Implement password reset functionality
- [ ] Add 2FA for sensitive operations

---

## Troubleshooting

### "Missing Authorization Header"
- Ensure you're including: `Authorization: Bearer YOUR_TOKEN`
- Check token is not empty or expired

### "Token has expired"
- Use refresh token to get new access token
- POST /auth/refresh with refresh token

### "Invalid signature" (Razorpay)
- Verify Razorpay keys are correct
- Ensure signature calculation matches Razorpay's format
- Check order_id and payment_id are correct

### "User not found"
- Ensure user is registered first
- Check JWT token is for valid user ID

---

## Success Indicators

✅ User registration returns JWT tokens  
✅ Login authentication works correctly  
✅ Protected routes require valid JWT  
✅ Razorpay order created successfully  
✅ Payment signature verification working  
✅ Payment status updated to 'paid' after verification  
✅ Complaint creation uses logged-in user ID  
✅ All 26 routes registered successfully  

---

## Next Steps

1. Integrate Razorpay SDK in mobile app
2. Implement proper error handling in mobile app
3. Add payment receipt generation
4. Implement webhook for payment confirmations
5. Add email notifications for successful payments
6. Create admin dashboard for payment management
