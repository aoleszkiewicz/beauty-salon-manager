# Tests Plan: Beauty Salon Manager

> **Approach**: TDD-lite — write tests for critical business logic *before* implementation, but allow flexibility for exploratory development on straightforward CRUD operations.

## Testing Strategy

### When to Write Tests First (TDD)
- ✅ Scheduling logic (availability validation)
- ✅ Booking conflict detection
- ✅ Business rules (e.g., breaks within work hours)
- ✅ Edge cases in date/time handling

### When Tests Can Follow Implementation
- CRUD endpoints (straightforward database operations)
- Authentication flows (after initial setup)
- Reporting aggregations

---

## Test Structure

```text
tests/
├── conftest.py              # Fixtures (test client, db session, sample data)
├── unit/
│   ├── test_availability.py # Core scheduling logic
│   ├── test_models.py       # Model validations
│   └── test_security.py     # Password hashing
├── integration/
│   ├── test_employees.py
│   ├── test_customers.py
│   ├── test_services.py
│   ├── test_schedules.py
│   ├── test_visits.py
│   └── test_auth.py
└── e2e/
    └── test_booking_flow.py  # Full booking scenario
```

---

## 1. Unit Tests (Write First — TDD)

### `test_availability.py` — Core Business Logic

| Test Case | Expected Result |
|-----------|-----------------|
| `test_slot_within_working_hours` | ✅ Available |
| `test_slot_outside_working_hours` | ❌ Unavailable |
| `test_slot_overlaps_break` | ❌ Unavailable |
| `test_slot_overlaps_existing_visit` | ❌ Unavailable |
| `test_slot_adjacent_to_visit_no_gap` | ✅ Available (back-to-back is OK) |
| `test_slot_on_day_off` | ❌ Unavailable |
| `test_slot_spans_midnight` | ❌ Invalid request |
| `test_slot_duration_exceeds_remaining_hours` | ❌ Unavailable |

### `test_models.py` — Validation Rules

| Test Case | Expected Result |
|-----------|-----------------|
| `test_break_within_schedule_hours` | ✅ Valid |
| `test_break_outside_schedule_hours` | ❌ Validation error |
| `test_service_duration_positive` | ✅ Valid |
| `test_service_duration_zero_or_negative` | ❌ Validation error |
| `test_visit_end_after_start` | ✅ Valid |

---

## 2. Integration Tests

### `test_employees.py`

| Endpoint | Test Case |
|----------|-----------|
| `POST /employees` | Create employee (admin) → 201 |
| `POST /employees` | Create employee (non-admin) → 403 |
| `GET /employees` | List employees → returns array |
| `GET /employees/{id}` | Get existing → 200 |
| `GET /employees/{id}` | Get non-existing → 404 |
| `PUT /employees/{id}` | Update as admin → 200 |
| `DELETE /employees/{id}` | Deactivate → is_active=false |

### `test_customers.py`

| Endpoint | Test Case |
|----------|-----------|
| `POST /customers` | Create customer → 201 |
| `GET /customers?search=` | Search by name → filtered results |
| `PUT /customers/{id}` | Update phone/email → 200 |

### `test_services.py`

| Endpoint | Test Case |
|----------|-----------|
| `POST /services` | Create service (admin) → 201 |
| `GET /services` | List active services only |
| `PUT /services/{id}` | Update price → 200 |

### `test_schedules.py`

| Endpoint | Test Case |
|----------|-----------|
| `POST /employees/{id}/schedules` | Add Monday 9-17 → 201 |
| `POST /employees/{id}/schedules` | Duplicate day → 400 (conflict) |
| `POST .../breaks` | Add lunch break → 201 |
| `POST .../breaks` | Break outside hours → 400 |

### `test_visits.py`

| Endpoint | Test Case |
|----------|-----------|
| `POST /visits` | Valid booking → 201 |
| `POST /visits` | Overlapping booking → 400 |
| `POST /visits` | Outside work hours → 400 |
| `POST /visits` | During break → 400 |
| `PATCH /visits/{id}/status` | Complete visit → status=completed |
| `GET /visits?employee_id=&date=` | Filter works correctly |

### `test_auth.py`

| Endpoint | Test Case |
|----------|-----------|
| `POST /login` | Valid credentials → session/token |
| `POST /login` | Invalid password → 401 |
| Protected endpoint | No auth → 401 |
| Admin endpoint | Non-admin user → 403 |

---

## 3. E2E Tests

### `test_booking_flow.py` — Complete Scenario

```python
def test_full_booking_flow():
    """
    1. Admin creates employee
    2. Employee sets schedule (Mon-Fri 9-17)
    3. Employee adds lunch break (12-13)
    4. Admin creates service "Haircut" (30 min)
    5. User creates customer
    6. User books visit for Monday 10:00
    7. Verify visit appears in calendar
    8. Complete the visit
    9. Verify it appears in income report
    """
```

---

## 4. Fixtures (`conftest.py`)

```python
@pytest.fixture
def db_session():
    """In-memory SQLite for test isolation"""
    
@pytest.fixture
def client(db_session):
    """TestClient with overridden DB dependency"""
    
@pytest.fixture
def admin_user(db_session):
    """Pre-created admin for auth tests"""
    
@pytest.fixture
def employee_with_schedule(db_session):
    """Employee with Mon-Fri 9-17 schedule"""
    
@pytest.fixture
def sample_service(db_session):
    """Haircut service, 30 min, $25"""
```

---

## 5. Running Tests

```bash
# All tests
pytest -v

# With coverage
pytest --cov=app --cov-report=html

# Only unit tests (fast, run during TDD)
pytest tests/unit -v

# Only integration tests
pytest tests/integration -v

# Specific test file
pytest tests/unit/test_availability.py -v
```

---

## Priority Order for TDD

1. **`test_availability.py`** — Write these FIRST, before implementing `is_slot_available()`
2. **`test_visits.py`** — Booking validation tests before POST /visits
3. **`test_schedules.py`** — Break validation before schedule endpoints
4. Everything else can follow implementation
