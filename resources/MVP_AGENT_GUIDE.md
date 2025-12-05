# MVP Construction Guide: Beauty Salon Manager

This document serves as a step-by-step guide for an AI agent (or developer) to build the MVP of the Beauty Salon Manager application.

> **Deployment Model**: This application is designed for a **single business** (self-hosted on a dedicated server). There is no multi-tenant architecture or external user management—all users belong to the same salon organization.

## 1. Technology Stack & Setup
**Goal**: Initialize the project with a modern, robust Python backend stack.

*   **Language**: Python 3.10+
*   **Framework**: **FastAPI** (Chosen for performance, automatic documentation, and ease of building REST APIs).
*   **Database**: **SQLite** (for MVP simplicity), scalable to PostgreSQL.
*   **ORM**: **SQLAlchemy (Async)** 2.0+.
*   **Migrations**: **Alembic**.
*   **Validation**: **Pydantic** v2.
*   **Authentication**: Simple session-based or basic password authentication (no OAuth/JWT overhead for single-tenant use).

### Agent Task 1: Project Initialization
1.  Create a standard FastAPI project structure:
    ```text
    app/
    ├── api/            # Route handlers (endpoints)
    │   ├── v1/
    │   │   ├── endpoints/
    │   │   └── api.py
    ├── core/           # Config, security, exceptions
    ├── db/             # Database session, base class
    ├── models/         # SQLAlchemy models
    ├── schemas/        # Pydantic models (request/response)
    ├── services/       # Business logic (scheduling, reporting)
    ├── main.py         # App entry point
    └── tests/          # Pytest tests
    ```
2.  Set up `pyproject.toml` or `requirements.txt` with dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pydantic-settings`, `passlib[bcrypt]`, `pytest`.

## 2. Database Modeling
**Goal**: Define the data structure to support users, services, and complex scheduling.

### Agent Task 2: Implement Core Models
Create the following SQLAlchemy models in `app/models/`:

1.  **User**
    *   `id`: Integer/UUID, PK
    *   `email`: String, Unique, Index
    *   `hashed_password`: String
    *   `full_name`: String
    *   `role`: Enum ("admin", "employee")
    *   `is_active`: Boolean

2.  **Service**
    *   `id`: Integer, PK
    *   `name`: String (e.g., "Haircut")
    *   `duration_minutes`: Integer (e.g., 30, 60, 90)
    *   `price`: Decimal/Float
    *   `is_active`: Boolean

3.  **Customer** (Salon clients database)
    *   `id`: Integer, PK
    *   `full_name`: String
    *   `phone`: String (Optional, for contact/reminders)
    *   `email`: String (Optional)
    *   `notes`: Text (Optional, e.g., preferences, allergies)
    *   `created_at`: DateTime

4.  **WorkSchedule** (Defines standard working hours per day, **per employee**)
    *   `id`: Integer, PK
    *   `employee_id`: FK to User (each employee has their own schedule)
    *   `day_of_week`: Enum ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
    *   `start_time`: Time (e.g., 08:00)
    *   `end_time`: Time (e.g., 16:00)

5.  **WorkBreak** (Specific breaks within a schedule)
    *   `id`: Integer, PK
    *   `schedule_id`: FK to WorkSchedule
    *   `start_time`: Time
    *   `end_time`: Time
    *   *Constraint*: Must fall within the `WorkSchedule` hours.

6.  **Visit** (The appointment)
    *   `id`: Integer, PK
    *   `customer_id`: FK to Customer
    *   `employee_id`: FK to User
    *   `service_id`: FK to Service
    *   `start_datetime`: DateTime
    *   `end_datetime`: DateTime (Calculated: start + service.duration)
    *   `price`: Decimal (Snapshot of service price at booking)
    *   `comment`: Text (Optional)
    *   `status`: Enum ("scheduled", "completed", "cancelled")

## 3. Authentication & User Management
**Goal**: Secure the system with simple internal authentication (single-tenant, no external identity providers).

### Agent Task 3: Auth Implementation
1.  Implement `app/core/security.py` for password hashing.
2.  Create `POST /login` endpoint (simple username/password, returns session cookie or basic token).
3.  Create `get_current_user` and `get_current_admin` dependencies.

> **Note**: Since this is a self-hosted, single-business app, there's no need for OAuth2 flows or external user management. Users are created directly in the database by the Admin.

### Agent Task 4: Employee (User) Endpoints
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/employees` | Create new employee | Admin |
| `GET` | `/employees` | List all employees | Authenticated |
| `GET` | `/employees/{id}` | Get employee details | Authenticated |
| `PUT` | `/employees/{id}` | Update employee | Admin |
| `DELETE` | `/employees/{id}` | Deactivate employee | Admin |

## 4. Customer Management
**Goal**: Maintain a database of salon clients.

### Agent Task 5: Customer CRUD
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/customers` | Create new customer | Authenticated |
| `GET` | `/customers` | List customers (with search/filter) | Authenticated |
| `GET` | `/customers/{id}` | Get customer details | Authenticated |
| `PUT` | `/customers/{id}` | Update customer info | Authenticated |
| `DELETE` | `/customers/{id}` | Remove customer | Admin |

## 5. Service Management
**Goal**: Allow Admin to configure the service catalog.

### Agent Task 6: Service CRUD
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/services` | Create new service | Admin |
| `GET` | `/services` | List all services | Authenticated |
| `GET` | `/services/{id}` | Get service details | Authenticated |
| `PUT` | `/services/{id}` | Update service | Admin |
| `DELETE` | `/services/{id}` | Deactivate service | Admin |

## 6. Scheduling Logic (The Core Complexity)
**Goal**: Ensure visits are only booked when employees are actually available.

### Agent Task 7: Schedule Configuration
Schedules are **sub-resources** of employees:

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/employees/{id}/schedules` | Create schedule for a day | Owner/Admin |
| `GET` | `/employees/{id}/schedules` | Get employee's weekly schedule | Authenticated |
| `PUT` | `/employees/{id}/schedules/{schedule_id}` | Update schedule | Owner/Admin |
| `DELETE` | `/employees/{id}/schedules/{schedule_id}` | Remove schedule | Owner/Admin |

**Breaks** are sub-resources of schedules:

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/employees/{id}/schedules/{schedule_id}/breaks` | Add break | Owner/Admin |
| `GET` | `/employees/{id}/schedules/{schedule_id}/breaks` | List breaks | Authenticated |
| `DELETE` | `/employees/{id}/breaks/{break_id}` | Remove break | Owner/Admin |

### Agent Task 8: Availability Validation Service
Implement a service function `is_slot_available(employee_id, start_dt, duration_minutes)`:
1.  **Work Hours Check**: Does `start_dt` and `end_dt` fall within the employee's `WorkSchedule` for that day?
2.  **Break Check**: Does the interval overlap with any `WorkBreak`?
3.  **Conflict Check**: Does the interval overlap with any existing `Visit` (status="scheduled")?

## 7. Visit Management
**Goal**: Booking appointments with validation.

### Agent Task 9: Visit Endpoints
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/visits` | Book a new visit | Authenticated |
| `GET` | `/visits` | List visits (query: `date`, `employee_id`, `customer_id`) | Authenticated |
| `GET` | `/visits/{id}` | Get visit details | Authenticated |
| `PUT` | `/visits/{id}` | Update visit (reschedule) | Authenticated |
| `PATCH` | `/visits/{id}/status` | Change status (complete/cancel) | Authenticated |
| `DELETE` | `/visits/{id}` | Cancel and remove visit | Owner/Admin |

**POST /visits Request Body**:
```json
{
  "customer_id": 1,
  "employee_id": 2,
  "service_id": 3,
  "start_datetime": "2024-01-15T10:00:00",
  "comment": "Optional notes"
}
```
*Logic*: Fetch Service duration → Calculate `end_datetime` → Run `is_slot_available` → Save or return 400 Error.

## 8. Calendar & Reporting
**Goal**: Visualization and business intelligence.

### Agent Task 10: Calendar Endpoint
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/calendar` | Aggregated view for frontend calendars |

**Query Params**: `start_date`, `end_date` (ISO Date), `employee_id` (Optional)
*   **Response Structure**:
    ```json
    [
      {
        "type": "visit",
        "id": 1,
        "title": "Haircut - John Doe",
        "start": "2023-10-27T10:00:00",
        "end": "2023-10-27T10:30:00",
        "color": "blue"
      },
      {
        "type": "break",
        "start": "2023-10-27T12:00:00",
        "end": "2023-10-27T12:30:00",
        "color": "gray"
      }
    ]
    ```
    *Note: This flat structure is compatible with most frontend calendar libraries (e.g., FullCalendar).*

### Agent Task 11: Reporting Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/reports/income` | Total income for date range |
| `GET` | `/reports/services` | Service popularity breakdown |
| `GET` | `/reports/employees` | Per-employee performance |

---

## 9. Containerization (Docker)
**Goal**: Easy deployment and environment consistency.

### Agent Task 12: Docker Setup
1.  Create `Dockerfile`:
    ```dockerfile
    FROM python:3.11-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY ./app ./app
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```

2.  Create `docker-compose.yml`:
    ```yaml
    version: '3.8'
    services:
      api:
        build: .
        ports:
          - "8000:8000"
        volumes:
          - ./data:/app/data  # SQLite persistence
        environment:
          - DATABASE_URL=sqlite:///./data/salon.db
    ```

---

## 10. CI/CD (GitHub Actions)
**Goal**: Automated testing and deployment pipeline.

### Agent Task 13: GitHub Actions Workflow
Create `.github/workflows/ci.yml`:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app tests/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: false  # Set to true when ready to push to registry
          tags: beauty-salon-api:latest
```

> **Deployment Options**:
> - **Simple**: SSH into server, `docker-compose pull && docker-compose up -d`
> - **Advanced**: Push to Docker Hub/GitHub Container Registry, then deploy via Watchtower or similar

---

## 11. Verification
**Goal**: Ensure correctness without a frontend.

> 📋 **See [TESTS_PLAN.md](./TESTS_PLAN.md)** for the complete testing strategy (TDD-lite approach).

### Agent Task 14: Testing
1.  Write `pytest` cases for the scheduling logic (critical path).
    *   Test: Booking during a break (Should Fail).
    *   Test: Booking overlapping another visit (Should Fail).
    *   Test: Booking outside working hours (Should Fail).
    *   Test: Valid booking (Should Succeed).
2.  Run tests locally: `pytest -v`
3.  Verify Docker build: `docker-compose up --build`
