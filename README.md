# Event-Driven Notification System

## 🚀 Overview

This project implements a fully containerized **Event-Driven Notification System** using:

- FastAPI (Backend API - Event Publisher)
- RabbitMQ (Message Broker)
- PostgreSQL (Database)
- Python Consumer Service (Event Processor)
- Docker & Docker Compose (Orchestration)

The system follows **Event-Driven Architecture (EDA)** principles to ensure:

- Asynchronous processing
- Loose coupling between services
- High reliability
- Idempotent message handling
- Fault tolerance

---

## 🏗 Architecture Overview

```

Client
|
| POST /api/events
v
Backend API (Publisher)
|
| Publishes event (JSON)
v
RabbitMQ (Message Broker)
|
| Delivers message
v
Consumer Service
|
| Stores processed event
v
PostgreSQL Database

```

### Key Design Decisions

- API does NOT write to DB directly.
- Messages are persistent.
- Queue is durable.
- Consumer acknowledges only after successful DB commit.
- Idempotency enforced via database unique constraint.
- All services are containerized.
- Health checks ensure proper startup order.

---

## 📂 Project Structure

```

backend/               # FastAPI Event Publisher
consumer/              # Python Consumer Service
db/init.sql            # PostgreSQL schema & seed
docker-compose.yml     # Service orchestration
.env.example           # Environment variables template
README.md

````

---

## 🧰 Tech Stack

- Python 3.11
- FastAPI
- RabbitMQ (3-management)
- PostgreSQL 13+
- Pika (RabbitMQ client)
- psycopg2
- Docker
- Docker Compose
- Pytest

---

## ⚙️ Environment Variables

Create `.env` from `.env.example`:

```bash
cp .env.example .env
````

### Example `.env`

```
# Database
DB_NAME=notification_db
DB_USER=notiuser
DB_PASSWORD=notipassword

# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
```

---

## 🐳 Running the Application

### 1️⃣ Build & Start

```bash
docker-compose up --build
```

All services will start:

* API → [http://localhost:8000](http://localhost:8000)
* RabbitMQ UI → [http://localhost:15672](http://localhost:15672)
* PostgreSQL → internal container
* Consumer → background worker

---

## 🏥 Health Checks

Check API health:

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok"}
```

---

## 📤 API Documentation

### POST `/api/events`

Publishes a notification event asynchronously.

### Request Body

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "user_registered",
  "message": "Welcome!",
  "payload": {
    "email": "test@example.com"
  }
}
```

### Success Response

```
202 Accepted
```

```json
{
  "message": "Event published successfully"
}
```

### Validation Failure

Returns:

```
400 Bad Request
```

---

## 📥 Consumer Behavior

The consumer:

* Subscribes to `notification_events`
* Parses JSON event
* Logs event processing
* Stores processed event in PostgreSQL
* Acknowledges message only after DB commit

---

## 🗄 Database Schema

Defined in `db/init.sql`

```sql
CREATE TABLE processed_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    payload JSONB,
    status VARCHAR(50) DEFAULT 'PROCESSED',
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);
```

---

## 🔁 Idempotency Strategy

The consumer prevents duplicate processing using:

* Database-level unique constraint
* `ON CONFLICT DO NOTHING` insertion logic

If the same event is processed multiple times:

* It is ignored
* No duplicate rows are inserted
* System remains consistent

---

## ❗ Error Handling

### API

* Validates input using Pydantic
* Returns 400 for invalid payload
* Logs publishing errors

### Consumer

* Invalid JSON → message discarded
* Database error → message requeued
* General errors → safe retry
* Messages acknowledged only after successful processing

---

## 🧪 Running Tests

### Backend Tests

```bash
docker-compose exec backend_api pytest
```

### Consumer Tests

```bash
docker-compose exec consumer_service pytest
```

All tests must pass before submission.

---

## 🔍 Verifying System Works

### Publish Event

```bash
curl -X POST http://localhost:8000/api/events \
-H "Content-Type: application/json" \
-d '{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "user_registered",
  "message": "Welcome!",
  "payload": {"email": "test@example.com"}
}'
```

### Check Database

```bash
docker-compose exec db psql -U notiuser -d notification_db \
-c "SELECT * FROM processed_events;"
```

---

## 🛡 Reliability Guarantees

* Durable queue
* Persistent messages
* Idempotent consumer
* Atomic DB transactions
* Container health checks
* Restart policy for consumer

---

## 🧠 Why Event-Driven Architecture?

Event-driven systems provide:

* Loose coupling
* Scalability
* Resilience
* Asynchronous processing
* Fault isolation

This architecture ensures the API remains responsive even under heavy load.

---

## 📌 Common Pitfalls Avoided

✔ API does NOT write to DB directly
✔ No blocking API calls
✔ Proper message acknowledgment
✔ No hardcoded credentials
✔ Fully containerized setup
✔ Environment variable configuration
✔ Automated unit testing

---

## 🏁 One-Command Setup

```bash
docker-compose up --build
```

System is fully operational.
