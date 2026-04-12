# Implementation Plan — Doctor Visit Booking System

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Tech Stack & Tooling](#2-tech-stack--tooling)
- [3. Project Structure](#3-project-structure)
- [4. Database Design](#4-database-design)
- [5. Phase 1 — Project Scaffolding & Infrastructure](#5-phase-1--project-scaffolding--infrastructure)
- [6. Phase 2 — Database Schema & Migrations](#6-phase-2--database-schema--migrations)
- [7. Phase 3 — Authentication & Authorization](#7-phase-3--authentication--authorization)
- [8. Phase 4 — Doctor Module](#8-phase-4--doctor-module)
- [9. Phase 5 — Patient Module](#9-phase-5--patient-module)
- [10. Phase 6 — Working Hours & Schedule Management](#10-phase-6--working-hours--schedule-management)
- [11. Phase 7 — Appointments Module](#11-phase-7--appointments-module)
- [12. Phase 8 — Testing](#12-phase-8--testing)
- [13. Phase 9 — Documentation & Delivery](#13-phase-9--documentation--delivery)
- [14. API Contract Overview](#14-api-contract-overview)
- [15. Coding Standards & Principles](#15-coding-standards--principles)

---

## 1. Project Overview

A REST API system for managing doctor visit bookings. Patients can register, associate with a personal doctor, and book/cancel appointments. Doctors manage their working hours, including temporary and permanent schedule overrides.

### Core Domain Entities

| Entity | Key Attributes |
|---|---|
| **Doctor** | name, email, address, weekly working hours |
| **Patient** | name, email, phone, personal doctor (exactly one) |
| **Appointment** | start datetime, end datetime, patient, doctor |
| **Working Hours** | day-of-week schedules with break support |
| **Temporary Override** | start/end datetime + replacement schedule (max 1 per doctor) |
| **Permanent Change** | effective date + new weekly schedule |

### Key Business Rules

- A patient has exactly one personal doctor.
- Appointments can only be created with the patient's personal doctor.
- Appointments must fall entirely within the doctor's working hours.
- Appointments must be created at least **24 hours** before the start time.
- Appointments must not overlap with other appointments of the same doctor.
- Cancellation is allowed no later than **12 hours** before the appointment start.
- A doctor can have at most **1 active temporary schedule override**.
- Permanent schedule changes must have an effective date at least **1 week** in the future.

---

## 2. Tech Stack & Tooling

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Framework | FastAPI |
| Database | SQLite (via `aiosqlite`) |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 (built into FastAPI) |
| Auth | JWT (via `python-jose` + `passlib[bcrypt]`) |
| Testing | pytest + pytest-asyncio + httpx (AsyncClient) |
| Linting | ruff |
| Type Checking | mypy (strict mode) |
| Formatting | ruff format |
| Task Runner | Makefile |
| Containerization | Docker + docker-compose (optional) |

---

## 3. Project Structure

```
.
├── alembic/                    # Migration environment
│   ├── versions/               # Individual migration files
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app factory, lifespan, router mounting
│   ├── config.py               # Settings via pydantic-settings (env vars)
│   ├── database.py             # Engine, session factory, Base
│   ├── dependencies.py         # Shared FastAPI dependencies (get_db, get_current_user)
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py           # POST /auth/register/doctor, /auth/register/patient, /auth/login
│   │   ├── service.py          # Registration & login logic
│   │   ├── schemas.py          # Request/response Pydantic models
│   │   ├── security.py         # JWT creation, password hashing, token verification
│   │   └── models.py           # User SQLAlchemy model (polymorphic or role-based)
│   ├── doctors/
│   │   ├── __init__.py
│   │   ├── router.py           # Doctor-specific endpoints
│   │   ├── service.py          # Business logic
│   │   ├── schemas.py          # DTOs
│   │   └── models.py           # Doctor SQLAlchemy model
│   ├── patients/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── models.py
│   ├── appointments/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py          # All booking/cancellation logic + validation
│   │   ├── schemas.py
│   │   └── models.py
│   ├── schedules/
│   │   ├── __init__.py
│   │   ├── router.py           # Working hours endpoints
│   │   ├── service.py          # Schedule resolution (base + overrides)
│   │   ├── schemas.py
│   │   └── models.py           # WorkingHours, TemporaryOverride, PermanentChange
│   └── common/
│       ├── __init__.py
│       ├── exceptions.py       # Custom exception classes
│       └── error_handlers.py   # FastAPI exception handlers → consistent JSON errors
├── tests/
│   ├── conftest.py             # Fixtures: test DB, async client, factory helpers
│   ├── factories.py            # Test data factories
│   ├── test_auth/
│   │   ├── test_register.py
│   │   └── test_login.py
│   ├── test_doctors/
│   ├── test_patients/
│   ├── test_appointments/
│   │   ├── test_create.py
│   │   ├── test_cancel.py
│   │   └── test_list.py
│   └── test_schedules/
│       ├── test_working_hours.py
│       ├── test_temporary_override.py
│       └── test_permanent_change.py
├── Makefile
├── pyproject.toml              # Project metadata, dependencies, tool config
├── requirements.txt            # Pinned production deps (generated from pyproject.toml)
├── requirements-dev.txt        # Dev/test deps
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Rationale

- **Feature-based modules** (`doctors/`, `patients/`, `appointments/`, `schedules/`) — each with its own router, service, schemas, and models. This follows the **Separation of Concerns** principle and keeps related code co-located.
- **Service layer** — all business logic lives in `service.py`, never in routers. Routers are thin HTTP adapters.
- **Schema/Model split** — SQLAlchemy models define persistence; Pydantic schemas define the API contract. They never leak into each other's layer.
- **Centralized error handling** — custom exceptions raised in services, caught by FastAPI exception handlers, returned as consistent JSON.

---

## 4. Database Design

### Entity-Relationship Diagram (Textual)

```
users
  ├── id (PK, INTEGER)
  ├── email (UNIQUE, NOT NULL)
  ├── hashed_password (NOT NULL)
  ├── role (ENUM: 'doctor' | 'patient', NOT NULL)
  ├── created_at (TIMESTAMP, NOT NULL)
  └── updated_at (TIMESTAMP, NOT NULL)

doctors
  ├── id (PK, INTEGER, FK → users.id)
  ├── name (TEXT, NOT NULL)
  ├── address (TEXT, NOT NULL)
  ├── created_at (TIMESTAMP, NOT NULL)
  └── updated_at (TIMESTAMP, NOT NULL)

patients
  ├── id (PK, INTEGER, FK → users.id)
  ├── name (TEXT, NOT NULL)
  ├── phone (TEXT, NOT NULL)
  ├── doctor_id (FK → doctors.id, NOT NULL)
  ├── created_at (TIMESTAMP, NOT NULL)
  └── updated_at (TIMESTAMP, NOT NULL)

working_hours
  ├── id (PK, INTEGER)
  ├── doctor_id (FK → doctors.id, NOT NULL)
  ├── day_of_week (INTEGER 0-6, NOT NULL)  -- 0=Monday
  ├── start_time (TIME, NOT NULL)
  ├── end_time (TIME, NOT NULL)
  ├── is_break (BOOLEAN, DEFAULT FALSE)
  └── UNIQUE(doctor_id, day_of_week, start_time)

temporary_overrides
  ├── id (PK, INTEGER)
  ├── doctor_id (FK → doctors.id, UNIQUE, NOT NULL)  -- max 1 per doctor
  ├── start_datetime (TIMESTAMP, NOT NULL)
  ├── end_datetime (TIMESTAMP, NOT NULL)
  ├── created_at (TIMESTAMP, NOT NULL)
  └── updated_at (TIMESTAMP, NOT NULL)

temporary_override_hours
  ├── id (PK, INTEGER)
  ├── override_id (FK → temporary_overrides.id, NOT NULL, ON DELETE CASCADE)
  ├── day_of_week (INTEGER 0-6, NOT NULL)
  ├── start_time (TIME, NOT NULL)
  ├── end_time (TIME, NOT NULL)
  ├── is_break (BOOLEAN, DEFAULT FALSE)
  └── UNIQUE(override_id, day_of_week, start_time)

permanent_changes
  ├── id (PK, INTEGER)
  ├── doctor_id (FK → doctors.id, NOT NULL)
  ├── effective_date (DATE, NOT NULL)       -- must be >= now + 7 days
  ├── created_at (TIMESTAMP, NOT NULL)
  └── applied (BOOLEAN, DEFAULT FALSE)      -- set TRUE once promoted to working_hours

permanent_change_hours
  ├── id (PK, INTEGER)
  ├── change_id (FK → permanent_changes.id, NOT NULL, ON DELETE CASCADE)
  ├── day_of_week (INTEGER 0-6, NOT NULL)
  ├── start_time (TIME, NOT NULL)
  ├── end_time (TIME, NOT NULL)
  ├── is_break (BOOLEAN, DEFAULT FALSE)
  └── UNIQUE(change_id, day_of_week, start_time)

appointments
  ├── id (PK, INTEGER)
  ├── doctor_id (FK → doctors.id, NOT NULL)
  ├── patient_id (FK → patients.id, NOT NULL)
  ├── start_datetime (TIMESTAMP, NOT NULL)
  ├── end_datetime (TIMESTAMP, NOT NULL)
  ├── status (ENUM: 'scheduled' | 'cancelled', DEFAULT 'scheduled')
  ├── cancelled_by (ENUM: 'doctor' | 'patient', NULLABLE)
  ├── created_at (TIMESTAMP, NOT NULL)
  └── updated_at (TIMESTAMP, NOT NULL)
```

### Design Decisions

- **Shared `users` table for auth** — both doctors and patients authenticate via the same table. Role-specific data lives in `doctors`/`patients` tables (1:1 FK to `users`). This avoids duplicating auth logic.
- **Working hours modeled as interval rows** — each row is a time slot for a specific day. Breaks are "negative" slots (`is_break = TRUE`). This allows querying "is time T within working hours?" with simple SQL.
- **Temporary override is UNIQUE per doctor** — enforced at the DB level.
- **Permanent changes tracked separately** — an `applied` flag and a background/on-request promotion mechanism moves them into the base `working_hours` table once the effective date arrives.

---

## 5. Phase 1 — Project Scaffolding & Infrastructure

**Goal:** Runnable empty FastAPI app with dev tooling configured.

### Tasks

- [ ] Initialize `pyproject.toml` with project metadata and dependencies
- [ ] Generate `requirements.txt` and `requirements-dev.txt`
- [ ] Create `app/main.py` with FastAPI app factory and health-check endpoint (`GET /health`)
- [ ] Create `app/config.py` using `pydantic-settings` (DATABASE_URL, SECRET_KEY, etc.)
- [ ] Create `.env.example`
- [ ] Create `Makefile` with targets: `install`, `dev`, `test`, `lint`, `format`, `migrate`, `migration`
- [ ] Configure `ruff` and `mypy` in `pyproject.toml`
- [ ] Create `Dockerfile` and `docker-compose.yml`
- [ ] Create `README.md` with setup instructions
- [ ] Verify: `make dev` starts the server, `make test` runs (empty) test suite

### Acceptance Criteria

- `GET /health` returns `200 {"status": "ok"}`
- `make lint` and `make format` pass with zero issues
- CI-ready project structure

---

## 6. Phase 2 — Database Schema & Migrations

**Goal:** All tables created via Alembic migrations, no raw SQL or `create_all()` in production code.

### Tasks

- [ ] Create `app/database.py` — async engine, async session factory, declarative Base
- [ ] Initialize Alembic (`alembic init alembic`), configure `env.py` for async SQLAlchemy
- [ ] Define SQLAlchemy models:
  - `app/auth/models.py` → `User`
  - `app/doctors/models.py` → `Doctor`
  - `app/patients/models.py` → `Patient`
  - `app/schedules/models.py` → `WorkingHours`, `TemporaryOverride`, `TemporaryOverrideHours`, `PermanentChange`, `PermanentChangeHours`
  - `app/appointments/models.py` → `Appointment`
- [ ] Generate initial migration: `alembic revision --autogenerate -m "initial_schema"`
- [ ] Review generated migration SQL, ensure indexes and constraints are correct
- [ ] Run migration: `alembic upgrade head`
- [ ] Add seed data script (optional, for dev convenience)

### Migration Discipline

- Every schema change gets its own migration file with a descriptive message.
- Migrations are reviewed before applying — never blindly trust autogenerate.
- Down-migrations (`downgrade()`) must be implemented for reversibility.
- Migration files are committed alongside the code changes that require them.

### Acceptance Criteria

- `alembic upgrade head` creates all tables from an empty database
- `alembic downgrade base` cleanly drops everything
- All foreign keys, unique constraints, and indexes are in place

---

## 7. Phase 3 — Authentication & Authorization

**Goal:** JWT-based auth. Doctors and patients register separately and receive tokens.

### Tasks

- [ ] Implement `app/auth/security.py`:
  - `hash_password(plain) → hashed`
  - `verify_password(plain, hashed) → bool`
  - `create_access_token(data, expires_delta) → str`
  - `decode_access_token(token) → payload`
- [ ] Implement `app/auth/schemas.py`:
  - `DoctorRegisterRequest` (name, email, password, address, working_hours)
  - `PatientRegisterRequest` (name, email, password, phone, doctor_id)
  - `LoginRequest` (email, password)
  - `TokenResponse` (access_token, token_type)
- [ ] Implement `app/auth/service.py`:
  - `register_doctor(db, data) → Doctor`
  - `register_patient(db, data) → Patient`
  - `authenticate(db, email, password) → User`
- [ ] Implement `app/auth/router.py`:
  - `POST /auth/register/doctor`
  - `POST /auth/register/patient`
  - `POST /auth/login`
- [ ] Implement `app/dependencies.py`:
  - `get_db()` — yields async DB session
  - `get_current_user(token)` — decodes JWT, fetches user, raises 401 if invalid
  - `require_doctor(user)` — raises 403 if user is not a doctor
  - `require_patient(user)` — raises 403 if user is not a patient

### Auth Flow

```
Register → hash password → store in users + doctors/patients → return 201
Login    → verify password → create JWT → return {access_token, token_type}
Protected endpoints → Authorization: Bearer <token> → decode → inject user
```

### Acceptance Criteria

- Registration creates the user and the role-specific record in a single transaction
- Duplicate email returns `409 Conflict`
- Login with wrong credentials returns `401 Unauthorized`
- Protected endpoints return `401` without a token and `403` with the wrong role

---

## 8. Phase 4 — Doctor Module

**Goal:** Doctor profile retrieval (used by patients to find their doctor).

### Tasks

- [ ] Implement `app/doctors/schemas.py`:
  - `DoctorResponse` (id, name, email, address, working_hours)
  - `DoctorListResponse` (list of doctors with pagination)
- [ ] Implement `app/doctors/service.py`:
  - `get_doctor(db, doctor_id) → Doctor`
  - `list_doctors(db, skip, limit) → list[Doctor]`
- [ ] Implement `app/doctors/router.py`:
  - `GET /doctors` — list all doctors (public, for patient registration)
  - `GET /doctors/{id}` — get doctor details including working hours

### Acceptance Criteria

- List endpoint returns paginated results
- Detail endpoint includes full weekly schedule
- Non-existent doctor returns `404`

---

## 9. Phase 5 — Patient Module

**Goal:** Patient profile management.

### Tasks

- [ ] Implement `app/patients/schemas.py`:
  - `PatientResponse` (id, name, email, phone, doctor_id)
- [ ] Implement `app/patients/service.py`:
  - `get_patient(db, patient_id) → Patient`
- [ ] Implement `app/patients/router.py`:
  - `GET /patients/me` — get own profile (requires auth)

### Acceptance Criteria

- Patients can view their own profile
- Response includes the personal doctor's ID

---

## 10. Phase 6 — Working Hours & Schedule Management

**Goal:** Full schedule management — base hours, temporary overrides, and permanent changes.

### Sub-phase 6a — Base Working Hours

- [ ] Implement `app/schedules/schemas.py`:
  - `DaySchedule` (day_of_week, intervals: list of {start_time, end_time, is_break})
  - `WeeklySchedule` (list of DaySchedule)
  - `WorkingHoursUpdateRequest`
- [ ] Implement `app/schedules/service.py`:
  - `get_working_hours(db, doctor_id) → WeeklySchedule`
  - `update_working_hours(db, doctor_id, schedule) → WeeklySchedule`
- [ ] Implement `app/schedules/router.py`:
  - `PUT /doctors/me/schedule` — update base working hours (doctor only)
  - `GET /doctors/{id}/schedule` — get current effective schedule

### Sub-phase 6b — Temporary Override

- [ ] Add to schemas: `TemporaryOverrideRequest` (start_datetime, end_datetime, schedule)
- [ ] Add to service:
  - `create_temporary_override(db, doctor_id, data)` — validates max 1 per doctor
  - `delete_temporary_override(db, doctor_id)` — remove active override
  - `get_effective_schedule(db, doctor_id, date) → DaySchedule` — resolves base vs. override
- [ ] Add to router:
  - `POST /doctors/me/schedule/temporary` — create override (doctor only)
  - `DELETE /doctors/me/schedule/temporary` — remove override (doctor only)

### Sub-phase 6c — Permanent Change

- [ ] Add to schemas: `PermanentChangeRequest` (effective_date, schedule)
- [ ] Add to service:
  - `create_permanent_change(db, doctor_id, data)` — validates effective_date >= now + 7 days
  - `apply_pending_permanent_changes(db)` — promotes changes whose effective_date has arrived
- [ ] Add to router:
  - `POST /doctors/me/schedule/permanent` — create change (doctor only)

### Schedule Resolution Logic

When determining the effective schedule for a doctor on a given date:

```
1. Check if a temporary override covers the date → use override schedule
2. Check if any permanent change has effective_date <= date → use the latest one
3. Fall back to base working_hours
```

### Acceptance Criteria

- Base schedule CRUD works correctly
- Temporary override enforces the "max 1 per doctor" constraint (DB-level UNIQUE)
- Permanent change rejects effective dates less than 7 days in the future
- Schedule resolution correctly prioritizes: temporary > permanent > base
- Existing appointments that conflict with a new schedule are handled (either rejected or flagged — decide during implementation)

---

## 11. Phase 7 — Appointments Module

**Goal:** Full appointment lifecycle — create, cancel, list.

### Tasks

- [ ] Implement `app/appointments/schemas.py`:
  - `AppointmentCreateRequest` (doctor_id, start_datetime, end_datetime)
  - `AppointmentResponse` (id, doctor_id, patient_id, start, end, status)
  - `AppointmentListResponse` (list with pagination + filters)
- [ ] Implement `app/appointments/service.py`:
  - `create_appointment(db, patient_id, data)` with validations:
    1. Doctor is the patient's personal doctor
    2. Appointment is entirely within effective working hours
    3. `start_datetime >= now + 24 hours`
    4. No time overlap with existing (non-cancelled) appointments for the same doctor
  - `cancel_appointment(db, user, appointment_id)` with validations:
    1. User is the doctor or patient of the appointment
    2. `start_datetime - now >= 12 hours`
  - `list_appointments(db, user, filters)` — returns appointments for the current user
- [ ] Implement `app/appointments/router.py`:
  - `POST /appointments` — create (patient only)
  - `DELETE /appointments/{id}` — cancel (patient or doctor)
  - `GET /appointments` — list own appointments (patient or doctor, with query filters)

### Overlap Detection Query

```sql
SELECT COUNT(*) FROM appointments
WHERE doctor_id = :doctor_id
  AND status = 'scheduled'
  AND start_datetime < :new_end
  AND end_datetime > :new_start
```

### Working Hours Validation

For each minute of the proposed appointment:
1. Resolve the effective schedule for that date (temporary > permanent > base).
2. Confirm the time falls within a working interval and not within a break.

Simplified: confirm `start_datetime` and `end_datetime` both fall on the same day and the entire `[start, end)` interval is within a working slot and outside all break slots.

### Acceptance Criteria

- All 4 business rules are enforced with descriptive error messages
- Cancellation respects the 12-hour rule
- Cancelled appointments don't block new bookings (overlap check excludes `status = 'cancelled'`)
- List endpoint supports filtering by date range and status

---

## 12. Phase 8 — Testing

**Goal:** Comprehensive automated test coverage.

### Test Strategy

| Layer | Tool | Scope |
|---|---|---|
| Unit tests | pytest | Service functions, validation logic, schedule resolution |
| Integration tests | pytest + httpx AsyncClient | Full request/response cycle through the API |
| DB tests | pytest + real SQLite (in-memory) | Migration verification, constraint enforcement |

### Test Infrastructure

- [ ] `tests/conftest.py`:
  - In-memory SQLite async engine
  - Fresh DB per test (run migrations via `alembic upgrade head`)
  - `AsyncClient` fixture pointed at test app
  - Auth helper: `authenticated_client(role, **user_data)` → client with valid JWT
- [ ] `tests/factories.py`:
  - `create_doctor(**overrides) → Doctor` with sensible defaults
  - `create_patient(**overrides) → Patient`
  - `create_appointment(**overrides) → Appointment`
  - `create_working_hours(doctor_id, ...) → list[WorkingHours]`

### Test Cases (Minimum)

**Auth (6+ tests)**
- [ ] Register doctor — success
- [ ] Register patient — success
- [ ] Register with duplicate email — 409
- [ ] Login — success
- [ ] Login with wrong password — 401
- [ ] Access protected endpoint without token — 401

**Appointments (10+ tests)**
- [ ] Create appointment — success
- [ ] Create with non-personal doctor — 403
- [ ] Create outside working hours — 422
- [ ] Create less than 24h before start — 422
- [ ] Create overlapping appointment — 409
- [ ] Cancel by patient — success
- [ ] Cancel by doctor — success
- [ ] Cancel less than 12h before — 422
- [ ] Cancel already cancelled — 409
- [ ] List appointments — returns own only

**Schedules (8+ tests)**
- [ ] Update base schedule — success
- [ ] Create temporary override — success
- [ ] Create second temporary override — 409
- [ ] Delete temporary override — success
- [ ] Create permanent change — success
- [ ] Permanent change with date < 7 days — 422
- [ ] Schedule resolution with override active
- [ ] Schedule resolution with permanent change applied

### Acceptance Criteria

- All tests pass with `make test`
- No test relies on external state or ordering (each test is isolated)
- Business rule violations return appropriate HTTP status codes and error messages

---

## 13. Phase 9 — Documentation & Delivery

**Goal:** Complete deliverables as specified.

### Tasks

- [ ] **README.md** — setup instructions, prerequisites, how to run, how to test
- [ ] **API documentation** — auto-generated OpenAPI/Swagger (FastAPI provides this at `/docs`)
- [ ] **PDF document** containing:
  - API usage guide (request/response examples, error codes)
  - Architecture description (class diagrams, sequence diagrams in UML)
  - Self-analysis (SOLID principles adherence, trade-offs, areas for improvement)
- [ ] **Clean git history** — meaningful commit messages, no large binary blobs
- [ ] Final review:
  - [ ] All tests pass
  - [ ] Linter and type checker pass
  - [ ] No hardcoded secrets
  - [ ] `.env.example` is up to date
  - [ ] README instructions work from a clean clone

---

## 14. API Contract Overview

### Endpoints Summary

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/auth/register/doctor` | No | — | Register a new doctor |
| `POST` | `/auth/register/patient` | No | — | Register a new patient |
| `POST` | `/auth/login` | No | — | Login, receive JWT |
| `GET` | `/doctors` | No | — | List all doctors |
| `GET` | `/doctors/{id}` | No | — | Get doctor details + schedule |
| `GET` | `/patients/me` | Yes | Patient | Get own profile |
| `PUT` | `/doctors/me/schedule` | Yes | Doctor | Update base working hours |
| `POST` | `/doctors/me/schedule/temporary` | Yes | Doctor | Create temporary override |
| `DELETE` | `/doctors/me/schedule/temporary` | Yes | Doctor | Remove temporary override |
| `POST` | `/doctors/me/schedule/permanent` | Yes | Doctor | Create permanent schedule change |
| `POST` | `/appointments` | Yes | Patient | Create appointment |
| `DELETE` | `/appointments/{id}` | Yes | Both | Cancel appointment |
| `GET` | `/appointments` | Yes | Both | List own appointments |

### Standard Error Response Format

```json
{
  "detail": {
    "code": "APPOINTMENT_OVERLAP",
    "message": "The requested time slot overlaps with an existing appointment."
  }
}
```

### HTTP Status Code Usage

| Code | Meaning |
|---|---|
| `200` | Success (GET, PUT) |
| `201` | Created (POST that creates a resource) |
| `204` | No Content (DELETE success) |
| `400` | Bad Request (malformed input) |
| `401` | Unauthorized (missing/invalid token) |
| `403` | Forbidden (wrong role or not the owner) |
| `404` | Not Found |
| `409` | Conflict (duplicate email, overlapping appointment, existing override) |
| `422` | Unprocessable Entity (business rule violation) |

---

## 15. Coding Standards & Principles

### SOLID Principles Application

- **Single Responsibility**: Each module handles one domain concept. Services contain business logic; routers handle HTTP concerns; models handle persistence.
- **Open/Closed**: New schedule types (e.g., holiday calendars) can be added without modifying existing schedule resolution logic — use a chain-of-responsibility pattern.
- **Liskov Substitution**: Doctor and Patient both conform to the `User` interface for auth purposes.
- **Interface Segregation**: Pydantic schemas are scoped per operation (create request ≠ response ≠ update request).
- **Dependency Inversion**: Services depend on the DB session abstraction, not concrete engine details. This enables swapping SQLite for PostgreSQL with zero service changes.

### Code Quality Rules

1. **No business logic in routers** — routers call services and return responses.
2. **No raw SQL in services** — use SQLAlchemy ORM queries.
3. **All datetimes in UTC** — convert to local time only at the API boundary if needed.
4. **Type hints everywhere** — enforced by mypy strict mode.
5. **No `# type: ignore`** without a comment explaining why.
6. **Explicit over implicit** — no magic; prefer readable code over clever code.
7. **Fail fast** — validate inputs at the API boundary (Pydantic) and business rules in services (raise exceptions early).
8. **Transactions** — each service operation runs in a single DB transaction. If any step fails, the entire operation rolls back.

### Git Workflow

- `main` branch is always deployable
- Feature branches: `feature/<phase>-<description>` (e.g., `feature/phase-3-auth`)
- Commit message format: `<type>(<scope>): <description>` (e.g., `feat(auth): add JWT token creation`)
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

---

## Phase Dependency Graph

```
Phase 1 (Scaffolding)
  └── Phase 2 (Database & Migrations)
        ├── Phase 3 (Auth)
        │     ├── Phase 4 (Doctors)
        │     └── Phase 5 (Patients)
        │           └── Phase 7 (Appointments) ←── Phase 6 (Schedules)
        └── Phase 6 (Schedules)
              └── Phase 7 (Appointments)
                    └── Phase 8 (Testing)
                          └── Phase 9 (Documentation)
```

> Phases 4, 5, and 6 can be partially parallelized since they are independent of each other. Phase 7 depends on all three.
