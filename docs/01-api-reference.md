# API Reference

Complete endpoint reference for the ICMON Auto Repair API.

**Base URL:** `http://localhost:8000`

---

## Authentication

All endpoints (except those marked **Public**) require authentication via one of:

- **JWT Bearer Token:** `Authorization: Bearer <access_token>`
- **API Key:** `X-API-Key: <api_key>` (maps to admin user)

Tokens are obtained from `POST /api/v1/authentication/login/`.

### Role-Based Access

| Role      | Access Level                                        |
|-----------|-----------------------------------------------------|
| `admin`   | All endpoints + Alembic version                     |
| `manager` | All endpoints except admin-only                     |
| `user`    | Standard user endpoints + own profile               |

---

## 1. Authentication

Base prefix: `/api/v1/authentication`

| Method | Endpoint          | Auth     | Description                          |
|--------|-------------------|----------|--------------------------------------|
| POST   | `/login/`         | Public   | Login with username/password (OAuth2 form) |
| POST   | `/register/`      | Public   | Register a new user account          |
| GET    | `/me/`            | JWT      | Get current authenticated user info  |
| PATCH  | `/refresh/`       | JWT (refresh) | Refresh access token            |
| DELETE | `/logout/`        | JWT      | Logout and blacklist session         |

### POST `/login/`

**Request:** `application/x-www-form-urlencoded`

| Field    | Type   | Required |
|----------|--------|----------|
| username | string | Yes      |
| password | string | Yes      |

**Response (200):**
```json
{
  "token_type": "Bearer",
  "access_token": "...",
  "refresh_token": "...",
  "expires_in": 1800
}
```

Cookies are also set: `token_type`, `access_token`, `refresh_token`.

### POST `/register/`

**Request body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "preferred_name": "John",
  "gender": "MALE",
  "birthdate": "1990-01-15",
  "email": "john@example.com",
  "username": "johndoe",
  "phone": "+66812345678",
  "password": "securepassword",
  "role": "user"
}
```

**Response (200):**
```json
{
  "message": "User registered successfully"
}
```

### GET `/me/`

**Response (200):**
```json
{
  "id": "uuid",
  "first_name": "John",
  "last_name": "Doe",
  "preferred_name": "John",
  "email": "john@example.com",
  "username": "johndoe",
  "phone": "+66812345678",
  "role": "user",
  "status": "active"
}
```

### PATCH `/refresh/`

Uses refresh token from cookie or body. Returns new access + refresh tokens.

### DELETE `/logout/`

Blacklists the current session and refresh token.

---

## 2. User

Base prefix: `/api/v1/user`

| Method | Endpoint  | Auth       | Description            |
|--------|-----------|------------|------------------------|
| POST   | `/`       | JWT        | Create a new user      |
| GET    | `/me/`    | JWT/API Key| Get current user profile|

### POST `/`

**Request body:** Same as register schema.

**Response (200):** User object.

### GET `/me/`

**Response (200):** Current user profile.

---

## 3. Customer

Base prefix: `/customer`

### Customer Endpoints

| Method | Endpoint         | Auth | Description              |
|--------|------------------|------|--------------------------|
| GET    | `/`              | JWT  | List customers (paginated)|
| POST   | `/`              | JWT  | Create a customer         |
| GET    | `/{customer_id}` | JWT  | Get a customer by ID      |
| PUT    | `/{customer_id}` | JWT  | Update a customer         |
| DELETE | `/{customer_id}` | JWT  | Soft-delete a customer    |

**Query params (GET `/`):**
| Param    | Type | Default | Description         |
|----------|------|---------|---------------------|
| page     | int  | 1       | Page number          |
| per_page | int  | 10      | Items per page (max 100) |

### Car Endpoints

| Method | Endpoint           | Auth | Description            |
|--------|--------------------|------|------------------------|
| GET    | `/car/`            | JWT  | List cars (paginated)  |
| POST   | `/car/`            | JWT  | Create a car           |
| GET    | `/car/{car_id}`    | JWT  | Get a car by ID        |
| PUT    | `/car/{car_id}`    | JWT  | Update a car           |
| DELETE | `/car/{car_id}`    | JWT  | Soft-delete a car      |

**Query params (GET `/car/`):**
| Param       | Type   | Default | Description              |
|-------------|--------|---------|--------------------------|
| customer_id | string | ""      | Filter by customer UUID  |
| page        | int    | 1       | Page number              |
| per_page    | int    | 10      | Items per page           |

### Customer Create/Update Schema

```json
{
  "customer_code": "CUST-001",
  "full_name": "Somchai Jaidee",
  "display_name": "Somchai",
  "customer_type": "INDIVIDUAL",
  "status": "ACTIVE",
  "tax_id": "1234567890123",
  "email": "somchai@example.com",
  "phone_number": "0812345678",
  "secondary_phone": "",
  "address": "123 Main St",
  "province": "Bangkok",
  "city": "Bangkok",
  "district": "Chatuchak",
  "postal_code": "10900",
  "country": "Thailand",
  "contact_person": "",
  "contact_phone": "",
  "notes": ""
}
```

### Car Create/Update Schema

```json
{
  "customer_id": "uuid",
  "license_plate": "กก 1234",
  "province": "Bangkok",
  "brand": "Toyota",
  "model": "Corolla Altis",
  "sub_model": "1.8 VVT-i",
  "year": 2022,
  "color": "White",
  "engine_number": "ENG12345",
  "chassis_number": "CHS12345",
  "fuel_type": "Gasoline",
  "transmission_type": "Automatic",
  "engine_cc": 1800,
  "seating_capacity": 5,
  "mileage": 25000,
  "notes": ""
}
```

### Paginated Response

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "per_page": 10,
  "total_pages": 15
}
```

---

## 4. Item

Base prefix: `/item`

| Method | Endpoint      | Auth | Description            |
|--------|---------------|------|------------------------|
| GET    | `/`           | JWT  | List items (paginated) |
| POST   | `/`           | JWT  | Create an item         |
| GET    | `/{item_id}`  | JWT  | Get an item by ID      |
| PUT    | `/{item_id}`  | JWT  | Update an item         |
| DELETE | `/{item_id}`  | JWT  | Soft-delete an item    |

### Item Schema

```json
{
  "title": "Oil Filter",
  "description": "Standard oil filter for passenger vehicles"
}
```

---

## 5. IoT (MQTT3)

Base prefix: `/mqtt3`

### Connection & Status

| Method | Endpoint               | Description                       |
|--------|------------------------|-----------------------------------|
| GET    | `/status`              | MQTT connection + cache status    |

### Device Management

| Method | Endpoint                                | Description                        |
|--------|-----------------------------------------|------------------------------------|
| GET    | `/devices`                              | List devices (paginated)           |
| GET    | `/devices/page`                         | List devices (page-based)          |
| GET    | `/devices/buckets/{bucket}`             | List devices in a bucket           |
| GET    | `/devices/location/{location_id}`       | List devices by location           |
| GET    | `/devices/{device_id}/status`           | Get device status                  |
| PUT    | `/devices/{device_id}/status`           | Update device status               |
| GET    | `/devices/{device_id}/config`           | Get device config                  |
| PUT    | `/devices/{device_id}/config`           | Update device config               |
| GET    | `/devices/{device_id}/stats`            | Get device statistics              |

### Sensor Data & Charts

| Method | Endpoint                    | Description                             |
|--------|-----------------------------|-----------------------------------------|
| GET    | `/senser-charts`            | Get sensor chart data                   |
| GET    | `/senser-data-chart`        | Get sensor data chart                   |
| GET    | `/senser-data`              | Get sensor data                         |
| GET    | `/device-senser-charts`     | Get device-specific sensor charts       |
| GET    | `/monitor-device-chart`     | Get monitor device chart                |
| GET    | `/topic-data-device-chart`  | Get topic data device chart             |
| POST   | `/topic-data`               | Get topic data by topic name            |

### Data Management

| Method | Endpoint            | Description                         |
|--------|---------------------|-------------------------------------|
| GET    | `/data/latest`      | Get latest IoT data                 |
| GET    | `/data/date-range`  | Get data by date range              |
| GET    | `/data/list`        | List IoT data (paginated)           |
| POST   | `/export`           | Export IoT data (CSV/JSON)          |
| DELETE | `/cleanup`          | Cleanup old data (by days)          |

### Device Control

| Method | Endpoint        | Description                |
|--------|-----------------|----------------------------|
| POST   | `/control`      | Send control to a device   |
| POST   | `/controls`     | Send control to multiple   |

### Alarms & Monitoring

| Method | Endpoint                       | Description                     |
|--------|--------------------------------|---------------------------------|
| POST   | `/alarm-device-status`         | Get alarm device status         |
| POST   | `/alarm-device-status-control` | Get alarm device status control |
| POST   | `/monitor-device-group`        | Get monitor device group        |

### MQTT Data Processing

| Method | Endpoint              | Description                    |
|--------|-----------------------|--------------------------------|
| POST   | `/process-mqtt-data`  | Process incoming MQTT payload  |

### WebSocket

| Method | Endpoint                    | Description                  |
|--------|-----------------------------|------------------------------|
| WS     | `/ws/{room}`                | WebSocket connection         |
| GET    | `/ws/rooms`                 | List active rooms            |
| GET    | `/ws/rooms/{room}/stats`    | Get room stats               |

**WebSocket messages:**
```json
{"type": "subscribe", "topic": "device/123"}
{"type": "unsubscribe", "topic": "device/123"}
{"type": "join_room", "room": "monitoring"}
{"type": "message", "topic": "device/123", "data": {...}}
```

### Batch Operations

| Method | Endpoint           | Description                    |
|--------|--------------------|--------------------------------|
| POST   | `/batch/process`   | Process multiple MQTT payloads |
| POST   | `/batch/control`   | Send batch control commands    |

---

## 6. Batch

Base prefix: `/batch`

| Method | Endpoint                 | Auth | Description              |
|--------|--------------------------|------|--------------------------|
| GET    | `/jobs`                  | JWT  | List batch jobs          |
| POST   | `/jobs`                  | JWT  | Create a batch job       |
| GET    | `/jobs/{job_id}`         | JWT  | Get a batch job by ID    |
| PUT    | `/jobs/{job_id}`         | JWT  | Update a batch job       |
| DELETE | `/jobs/{job_id}`         | JWT  | Delete a batch job       |
| POST   | `/jobs/{job_id}/run`     | JWT  | Execute a batch job      |
| GET    | `/jobs/{job_id}/logs`    | JWT  | Get job execution logs   |

### Batch Job Schema

```json
{
  "name": "Daily Data Sync",
  "type": "data_sync",
  "config": {"source": "influxdb", "target": "postgres"},
  "schedule": "0 2 * * *"
}
```

### Batch Job Response

```json
{
  "id": "uuid",
  "name": "Daily Data Sync",
  "type": "data_sync",
  "status": "completed",
  "config": {...},
  "schedule": "0 2 * * *",
  "total_count": 100,
  "success_count": 98,
  "fail_count": 2,
  "started_at": "2026-07-21T02:00:00Z",
  "finished_at": "2026-07-21T02:05:30Z",
  "created_at": "2026-07-20T10:00:00Z",
  "updated_at": "2026-07-21T02:05:30Z"
}
```

---

## 7. Dashboard

Base prefix: `/dashboard`

| Method | Endpoint       | Auth | Description                       |
|--------|----------------|------|-----------------------------------|
| GET    | `/stats`       | JWT  | Dashboard overview statistics     |
| GET    | `/revenue`     | JWT  | Revenue chart data                |
| GET    | `/top-parts`   | JWT  | Top selling parts                 |
| GET    | `/job-status`  | JWT  | Job/work order status summary     |

### Query params

| Endpoint     | Param  | Type   | Default | Description                         |
|-------------|--------|--------|---------|-------------------------------------|
| `/revenue`  | period | string | daily   | `daily`, `weekly`, or `monthly`     |
| `/top-parts`| limit  | int    | 5       | Number of top parts (1-50)          |

---

## 8. Document

Base prefix: `/document`

| Method | Endpoint          | Auth | Description              |
|--------|-------------------|------|--------------------------|
| GET    | `/`               | JWT  | List documents           |
| POST   | `/`               | JWT  | Upload/register document |
| GET    | `/{document_id}`  | JWT  | Get document metadata    |
| DELETE | `/{document_id}`  | JWT  | Delete a document        |

---

## 9. Email

Base prefix: `/email`

| Method | Endpoint            | Auth | Description              |
|--------|---------------------|------|--------------------------|
| POST   | `/send`             | JWT  | Send an email            |
| GET    | `/logs`             | JWT  | List email logs          |
| GET    | `/logs/{log_id}`    | JWT  | Get an email log         |
| GET    | `/config`           | JWT  | Get SMTP config          |
| PUT    | `/config`           | JWT  | Update SMTP config       |

### Send Email Schema

```json
{
  "to": "recipient@example.com",
  "subject": "Invoice #12345",
  "body": "<h1>Thank you for your business</h1>",
  "cc": "",
  "bcc": ""
}
```

### Email Config Schema

```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "noreply@icmon.com",
  "from_email": "noreply@icmon.com",
  "from_name": "ICMON Auto Repair",
  "is_active": true
}
```

---

## 10. I18n (Internationalization)

Base prefix: `/i18n`

| Method | Endpoint                      | Auth | Description              |
|--------|-------------------------------|------|--------------------------|
| GET    | `/translations`               | JWT  | List translations        |
| POST   | `/translations`               | JWT  | Create a translation     |
| GET    | `/translations/{key}`         | JWT  | Get translation by key   |
| PUT    | `/translations/{key}`         | JWT  | Update translation       |
| DELETE | `/translations/{key}`         | JWT  | Delete translation       |

**Query params:** `locale` (required for GET/PUT/DELETE by key)

### Translation Schema

```json
{
  "locale": "th",
  "key": "customer.greeting",
  "value": "สวัสดีครับ"
}
```

---

## 11. Payment

Base prefix: `/payment`

| Method | Endpoint                                  | Auth | Description                      |
|--------|-------------------------------------------|------|----------------------------------|
| POST   | `/payments/`                              | JWT  | Record a new payment             |
| POST   | `/payments/search`                        | JWT  | Search payments (POST body)      |
| GET    | `/payments/outstanding/{customer_id}`     | JWT  | Get outstanding balance          |
| GET    | `/payments/history/{customer_id}`         | JWT  | Get payment history with status changes |
| GET    | `/payments/{payment_id}`                  | JWT  | Get a payment by ID              |
| POST   | `/payments/{payment_id}/refund`           | JWT  | Process a refund                 |
| PUT    | `/payments/{payment_id}/cancel`           | JWT  | Cancel a payment                 |
| GET    | `/payments/invoice/{invoice_id}`          | JWT  | Get payments by invoice          |
| GET    | `/receipts/{receipt_id}`                  | JWT  | Get a receipt by ID              |
| GET    | `/receipts/payment/{payment_id}`          | JWT  | Get receipt by payment ID        |
| PUT    | `/receipts/{receipt_id}/cancel`           | JWT  | Cancel a receipt                 |

### Payment Record Schema

```json
{
  "invoice_id": "uuid",
  "job_id": "uuid",
  "customer_id": "uuid",
  "payment_method_id": "uuid",
  "amount": 1500.00,
  "amount_received": 2000.00,
  "currency": "THB",
  "reference_number": "TXN-12345",
  "bank_name": "Kasikorn Bank",
  "notes": "Cash payment"
}
```

### Refund Schema

```json
{
  "amount": 500.00,
  "reason": "Customer returned defective part"
}
```

---

## 12. Purchase Order

Base prefix: `/purchase-order`

| Method | Endpoint                    | Auth | Description                    |
|--------|-----------------------------|------|--------------------------------|
| GET    | `/`                         | JWT  | List POs (paginated, filterable)|
| POST   | `/`                         | JWT  | Create a purchase order        |
| GET    | `/{po_id}`                  | JWT  | Get PO with details + history  |
| PUT    | `/{po_id}`                  | JWT  | Update PO (DRAFT only)         |
| DELETE | `/{po_id}`                  | JWT  | Delete PO (DRAFT only)         |
| POST   | `/{po_id}/send`             | JWT  | Send PO to supplier            |
| PUT    | `/{po_id}/confirm`          | JWT  | Confirm PO                     |
| POST   | `/{po_id}/receive`          | JWT  | Receive goods                  |
| PUT    | `/{po_id}/cancel`           | JWT  | Cancel PO                      |
| GET    | `/{po_id}/history`          | JWT  | Get PO status change history   |

**Query params (GET `/`):**
| Param       | Type   | Description              |
|-------------|--------|--------------------------|
| page        | int    | Page number              |
| per_page    | int    | Items per page           |
| supplier_id | string | Filter by supplier UUID  |
| status      | string | Filter by status         |
| date_from   | string | Filter from date         |
| date_to     | string | Filter to date           |

**PO Status Flow:** `draft` -> `sent` -> `confirmed` -> `received` | `cancelled`

### PO Create Schema

```json
{
  "po_no": "PO-2026-001",
  "supplier_id": "uuid",
  "po_date": "2026-07-21",
  "expected_delivery_date": "2026-07-28",
  "status": "draft",
  "tax_rate": 7.0,
  "currency": "THB",
  "payment_terms": "Net 30",
  "delivery_address": "123 Workshop Rd, Bangkok",
  "notes": "Urgent order",
  "items": [
    {
      "part_id": "uuid",
      "quantity_ordered": 10,
      "unit_price": 250.00,
      "discount": 0
    }
  ]
}
```

### Receive Schema

```json
{
  "items": [
    {
      "part_id": "uuid",
      "quantity_received": 10
    }
  ]
}
```

---

## 13. Quotation

Base prefix: `/quotation`

| Method | Endpoint              | Auth | Description              |
|--------|-----------------------|------|--------------------------|
| GET    | `/`                   | JWT  | List quotations          |
| POST   | `/`                   | JWT  | Create a quotation       |
| GET    | `/{quotation_id}`     | JWT  | Get quotation by ID      |
| PUT    | `/{quotation_id}`     | JWT  | Update a quotation       |
| DELETE | `/{quotation_id}`     | JWT  | Delete a quotation       |

### Quotation Schema

```json
{
  "quotation_no": "QT-2026-001",
  "job_id": "uuid",
  "customer_id": "uuid",
  "quotation_date": "2026-07-21",
  "expiry_date": "2026-08-20",
  "subtotal": 5000.00,
  "tax_rate": 7.0,
  "tax_amount": 350.00,
  "total": 5350.00,
  "currency": "THB",
  "notes": "Includes labor and parts",
  "terms_and_conditions": "Valid for 30 days"
}
```

---

## 14. Report

Base prefix: `/report`

| Method | Endpoint                 | Auth | Description              |
|--------|--------------------------|------|--------------------------|
| GET    | `/daily-sales/pdf`       | JWT  | Daily sales report (PDF) |
| GET    | `/inventory-summary/pdf` | JWT  | Inventory summary (PDF)  |
| GET    | `/customer-list/pdf`     | JWT  | Customer list (PDF)      |
| GET    | `/invoice/pdf`           | JWT  | Invoice report (PDF)     |
| GET    | `/credit-note/pdf`       | JWT  | Credit note (PDF)        |
| GET    | `/debit-note/pdf`        | JWT  | Debit note (PDF)         |

**Query params:** `date` (for daily-sales), `source` (for invoice).

> **Note:** PDF generation is pending implementation. Endpoints return placeholder responses.

---

## 15. WOS (Web Order System)

Base prefix: `/wos`

| Method | Endpoint                  | Auth | Description              |
|--------|---------------------------|------|--------------------------|
| GET    | `/orders`                 | JWT  | List orders (paginated)  |
| POST   | `/orders`                 | JWT  | Create an order          |
| GET    | `/orders/{order_id}`      | JWT  | Get order by ID          |
| PUT    | `/orders/{order_id}/status`| JWT | Update order status      |

### Order Create Schema

```json
{
  "customer_name": "Somchai Jaidee",
  "customer_email": "somchai@example.com",
  "customer_phone": "0812345678",
  "items": [
    {"name": "Oil Change", "quantity": 1, "price": 800}
  ],
  "total_amount": 800.00,
  "notes": "Preferred morning slot"
}
```

**Status transitions:** `pending` -> `processing` -> `completed` | `cancelled`

---

## 16. Health

Base prefix: `/` (root)

| Method | Endpoint              | Auth     | Description              |
|--------|-----------------------|----------|--------------------------|
| GET    | `/health/`            | Public   | Health check             |
| GET    | `/`                   | Public   | Redirect to `/docs`      |
| GET    | `/api/v1/alembic-version/` | Admin | Current DB migration version |

### Health Response

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "dev",
  "database": "connected"
}
```

---

## 17. Example

Base prefix: `/api/v1/example`

| Method | Endpoint | Auth   | Description                     |
|--------|----------|--------|---------------------------------|
| POST   | `/`      | Public | Hello world (demonstrates DDD)  |

---

## Error Response Format

All errors follow the standard format:

```json
{
  "status_code": 422,
  "message": "Validation error",
  "detail": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### Common HTTP Codes

| Code | Meaning               |
|------|-----------------------|
| 200  | Success               |
| 201  | Created               |
| 400  | Bad Request           |
| 401  | Unauthorized          |
| 403  | Forbidden             |
| 404  | Not Found             |
| 409  | Conflict              |
| 422  | Validation Error      |
| 429  | Rate Limit Exceeded   |
| 500  | Internal Server Error |
