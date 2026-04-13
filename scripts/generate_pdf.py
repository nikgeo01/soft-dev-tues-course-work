#!/usr/bin/env python3
"""Generate the project PDF documentation (Phase 9 deliverable).

Run:  python scripts/generate_pdf.py
Output: docs/Doctor_Visit_Booking_API_Documentation.pdf
"""

from __future__ import annotations

import os
import textwrap

from fpdf import FPDF


class PDF(FPDF):  # type: ignore[misc]
    MARGIN = 15
    COL_LIGHT = (245, 245, 250)
    COL_HEADER = (50, 60, 80)
    COL_ACCENT = (70, 130, 180)
    COL_CODE_BG = (240, 240, 240)

    def __init__(self) -> None:
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(self.MARGIN, self.MARGIN, self.MARGIN)

    # ── helpers ──────────────────────────────────────────────────────

    def _heading(self, level: int, text: str) -> None:
        sizes = {1: 22, 2: 16, 3: 13}
        self.ln(4 if level > 1 else 8)
        self.set_font("Helvetica", "B", sizes.get(level, 12))
        self.set_text_color(*self.COL_HEADER)
        self.multi_cell(0, 8, text)
        if level == 1:
            self.set_draw_color(*self.COL_ACCENT)
            self.set_line_width(0.6)
            self.line(self.MARGIN, self.get_y(), self.w - self.MARGIN, self.get_y())
            self.ln(3)
        self.ln(2)

    def _body(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def _bold_body(self, text: str) -> None:
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def _bullet(self, text: str, indent: int = 6) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        x = self.get_x()
        self.set_x(x + indent)
        self.multi_cell(0, 5, f"-  {text}")
        self.ln(0.5)

    def _code_block(self, code: str) -> None:
        self.set_font("Courier", "", 8.5)
        self.set_fill_color(*self.COL_CODE_BG)
        self.set_text_color(30, 30, 30)
        for raw_line in code.strip().split("\n"):
            line = raw_line.replace("\t", "    ")
            self.cell(0, 4.2, f"  {line}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def _table(self, headers: list[str], rows: list[list[str]], col_widths: list[int] | None = None) -> None:
        usable = self.w - 2 * self.MARGIN
        if col_widths is None:
            cw = [usable / len(headers)] * len(headers)
        else:
            total = sum(col_widths)
            cw = [usable * w / total for w in col_widths]

        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(*self.COL_HEADER)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(cw[i], 7, f" {h}", border=1, fill=True)
        self.ln()

        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(30, 30, 30)
        for ri, row in enumerate(rows):
            if ri % 2 == 0:
                self.set_fill_color(*self.COL_LIGHT)
            else:
                self.set_fill_color(255, 255, 255)
            max_h = 6
            for ci, cell in enumerate(row):
                txt = f" {cell}"
                self.cell(cw[ci], max_h, txt, border=1, fill=True)
            self.ln()
        self.ln(3)

    # ── page header / footer ─────────────────────────────────────────

    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, "Doctor Visit Booking API  -  Technical Documentation", align="C")
        self.ln(10)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def build_pdf(output_path: str) -> None:
    pdf = PDF()
    pdf.alias_nb_pages()

    # ═══════════════════════════════════════════════════════════════════
    # TITLE PAGE
    # ═══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.ln(45)
    pdf.set_font("Helvetica", "B", 30)
    pdf.set_text_color(*PDF.COL_HEADER)
    pdf.cell(0, 14, "Doctor Visit Booking API", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(*PDF.COL_ACCENT)
    pdf.cell(0, 10, "Technical Documentation", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(12)
    pdf.set_draw_color(*PDF.COL_ACCENT)
    pdf.set_line_width(0.5)
    mid = pdf.w / 2
    pdf.line(mid - 40, pdf.get_y(), mid + 40, pdf.get_y())
    pdf.ln(12)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 7, "REST API for managing doctor visit bookings", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "FastAPI  |  SQLAlchemy 2.0  |  SQLite  |  JWT Auth", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(40)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Version 0.1.0", align="C", new_x="LMARGIN", new_y="NEXT")

    # ═══════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf._heading(1, "Table of Contents")
    toc = [
        "1. API Usage Guide",
        "   1.1 Authentication",
        "   1.2 Doctors",
        "   1.3 Patients",
        "   1.4 Working Hours & Schedules",
        "   1.5 Appointments",
        "   1.6 Error Codes Reference",
        "2. Architecture Description",
        "   2.1 High-Level Architecture",
        "   2.2 Project Structure",
        "   2.3 Database Schema (ER Diagram)",
        "   2.4 Class Diagram",
        "   2.5 Sequence Diagrams",
        "3. Self-Analysis",
        "   3.1 SOLID Principles Adherence",
        "   3.2 Design Trade-offs",
        "   3.3 Areas for Improvement",
    ]
    for entry in toc:
        pdf._body(entry)

    # ═══════════════════════════════════════════════════════════════════
    # 1. API USAGE GUIDE
    # ═══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf._heading(1, "1. API Usage Guide")
    pdf._body(
        "The API is served at http://localhost:8000 by default. Interactive Swagger UI "
        "is available at /docs and ReDoc at /redoc. All request and response bodies use JSON. "
        "Protected endpoints require an Authorization: Bearer <token> header."
    )

    # ── 1.1 Authentication ───────────────────────────────────────────
    pdf._heading(2, "1.1 Authentication")
    pdf._body(
        "The system uses JWT (JSON Web Tokens) for authentication. "
        "Tokens are obtained via the login endpoint and expire after 60 minutes (configurable). "
        "Doctors and patients register separately; both receive a token on successful registration."
    )

    pdf._heading(3, "POST /auth/register/doctor")
    pdf._body("Register a new doctor account with initial working hours.")
    pdf._bold_body("Request:")
    pdf._code_block(textwrap.dedent("""\
        POST /auth/register/doctor
        Content-Type: application/json

        {
          "name": "Dr. Smith",
          "email": "smith@clinic.com",
          "password": "securepass123",
          "address": "123 Medical Ave",
          "working_hours": [
            {
              "day_of_week": 0,
              "start_time": "09:00:00",
              "end_time": "17:00:00",
              "is_break": false
            }
          ]
        }"""))
    pdf._bold_body("Response (201 Created):")
    pdf._code_block(textwrap.dedent("""\
        {
          "access_token": "eyJhbGciOiJIUzI1NiIs...",
          "token_type": "bearer"
        }"""))

    pdf._heading(3, "POST /auth/register/patient")
    pdf._body("Register a new patient account linked to a personal doctor.")
    pdf._bold_body("Request:")
    pdf._code_block(textwrap.dedent("""\
        POST /auth/register/patient
        Content-Type: application/json

        {
          "name": "Jane Doe",
          "email": "jane@example.com",
          "password": "securepass123",
          "phone": "+359888000000",
          "doctor_id": 1
        }"""))
    pdf._bold_body("Response (201 Created):")
    pdf._code_block(textwrap.dedent("""\
        {
          "access_token": "eyJhbGciOiJIUzI1NiIs...",
          "token_type": "bearer"
        }"""))

    pdf._heading(3, "POST /auth/login")
    pdf._body("Authenticate with email and password.")
    pdf._bold_body("Request:")
    pdf._code_block(textwrap.dedent("""\
        POST /auth/login
        Content-Type: application/json

        {
          "email": "smith@clinic.com",
          "password": "securepass123"
        }"""))
    pdf._bold_body("Response (200 OK):")
    pdf._code_block(textwrap.dedent("""\
        {
          "access_token": "eyJhbGciOiJIUzI1NiIs...",
          "token_type": "bearer"
        }"""))
    pdf._bold_body("Error (401 Unauthorized):")
    pdf._code_block(textwrap.dedent("""\
        {
          "detail": {
            "code": "INVALID_CREDENTIALS",
            "message": "Incorrect email or password."
          }
        }"""))

    # ── 1.2 Doctors ──────────────────────────────────────────────────
    pdf._heading(2, "1.2 Doctors")

    pdf._heading(3, "GET /doctors")
    pdf._body("List all registered doctors (public, paginated).")
    pdf._bold_body("Query Parameters: skip (default 0), limit (default 20, max 100)")
    pdf._bold_body("Response (200 OK):")
    pdf._code_block(textwrap.dedent("""\
        {
          "items": [
            {
              "id": 1,
              "name": "Dr. Smith",
              "email": "smith@clinic.com",
              "address": "123 Medical Ave",
              "working_hours": [
                {
                  "id": 1,
                  "day_of_week": 0,
                  "start_time": "09:00:00",
                  "end_time": "17:00:00",
                  "is_break": false
                }
              ]
            }
          ],
          "total": 1,
          "skip": 0,
          "limit": 20
        }"""))

    pdf._heading(3, "GET /doctors/{id}")
    pdf._body("Get a specific doctor's profile and working hours.")
    pdf._bold_body("Response (200 OK): Same structure as a single item above.")
    pdf._bold_body("Error (404 Not Found):")
    pdf._code_block(textwrap.dedent("""\
        {
          "detail": {
            "code": "DOCTOR_NOT_FOUND",
            "message": "No doctor found with the given id."
          }
        }"""))

    # ── 1.3 Patients ─────────────────────────────────────────────────
    pdf._heading(2, "1.3 Patients")

    pdf._heading(3, "GET /patients/me")
    pdf._body("Get the authenticated patient's own profile. Requires patient role.")
    pdf._bold_body("Headers: Authorization: Bearer <token>")
    pdf._bold_body("Response (200 OK):")
    pdf._code_block(textwrap.dedent("""\
        {
          "id": 2,
          "name": "Jane Doe",
          "email": "jane@example.com",
          "phone": "+359888000000",
          "doctor_id": 1
        }"""))

    # ── 1.4 Working Hours & Schedules ────────────────────────────────
    pdf.add_page()
    pdf._heading(2, "1.4 Working Hours & Schedules")
    pdf._body(
        "Doctors manage three layers of schedule data. "
        "When resolving the effective schedule for a given date, the system checks in order: "
        "(1) active temporary override covering the date, "
        "(2) latest permanent change with effective_date <= the date, "
        "(3) base working hours. The first match wins."
    )

    pdf._heading(3, "PUT /doctors/me/schedule")
    pdf._body("Replace the doctor's base working hours (doctor only).")
    pdf._bold_body("Request:")
    pdf._code_block(textwrap.dedent("""\
        PUT /doctors/me/schedule
        Authorization: Bearer <doctor_token>

        {
          "slots": [
            {"day_of_week": 0, "start_time": "09:00:00",
             "end_time": "12:00:00", "is_break": false},
            {"day_of_week": 0, "start_time": "12:00:00",
             "end_time": "13:00:00", "is_break": true},
            {"day_of_week": 0, "start_time": "13:00:00",
             "end_time": "17:00:00", "is_break": false}
          ]
        }"""))
    pdf._body(
        "Returns 200 with the updated WeeklyScheduleResponse. "
        "Returns 422 SCHEDULE_CONFLICTS_APPOINTMENT if existing appointments "
        "would fall outside the new hours."
    )

    pdf._heading(3, "GET /doctors/{id}/schedule?date=YYYY-MM-DD")
    pdf._body(
        "Get the effective schedule for a doctor on a specific date. "
        "Defaults to today if date is omitted. Returns a list of TimeSlotResponse objects."
    )

    pdf._heading(3, "POST /doctors/me/schedule/temporary")
    pdf._body("Create a temporary schedule override (max 1 per doctor).")
    pdf._bold_body("Request:")
    pdf._code_block(textwrap.dedent("""\
        {
          "start_datetime": "2025-06-01T00:00:00Z",
          "end_datetime": "2025-06-08T00:00:00Z",
          "schedule": [
            {"day_of_week": 0, "start_time": "10:00:00",
             "end_time": "14:00:00", "is_break": false}
          ]
        }"""))
    pdf._body(
        "Returns 201 with TemporaryOverrideResponse. "
        "Returns 409 OVERRIDE_EXISTS if the doctor already has one. "
        "Returns 422 SCHEDULE_CONFLICTS_APPOINTMENT if existing appointments conflict."
    )

    pdf._heading(3, "DELETE /doctors/me/schedule/temporary")
    pdf._body("Remove the active temporary override. Returns 204 No Content.")

    pdf._heading(3, "POST /doctors/me/schedule/permanent")
    pdf._body("Schedule a permanent working-hours replacement (effective_date >= today + 7 days).")
    pdf._bold_body("Request:")
    pdf._code_block(textwrap.dedent("""\
        {
          "effective_date": "2025-07-01",
          "schedule": [
            {"day_of_week": 0, "start_time": "08:00:00",
             "end_time": "16:00:00", "is_break": false}
          ]
        }"""))
    pdf._body(
        "Returns 201 with PermanentChangeResponse. "
        "Returns 422 EFFECTIVE_DATE_TOO_SOON if the date is less than 7 days away. "
        "Returns 422 SCHEDULE_CONFLICTS_APPOINTMENT if existing appointments conflict. "
        "Pending permanent changes are automatically promoted to base working_hours "
        "on application startup and before each schedule resolution."
    )

    # ── 1.5 Appointments ─────────────────────────────────────────────
    pdf.add_page()
    pdf._heading(2, "1.5 Appointments")

    pdf._heading(3, "POST /appointments")
    pdf._body("Create an appointment (patient only). Business rules enforced:")
    pdf._bullet("Doctor must be the patient's personal doctor (403 NOT_PERSONAL_DOCTOR)")
    pdf._bullet("Start must be at least 24 hours in the future (422 TOO_SOON)")
    pdf._bullet("Start and end must be on the same calendar day (422 INVALID_TIME_RANGE)")
    pdf._bullet("Interval must fit within a non-break working slot (422 OUTSIDE_WORKING_HOURS)")
    pdf._bullet("No overlap with other scheduled appointments (409 APPOINTMENT_OVERLAP)")
    pdf._bold_body("Request:")
    pdf._code_block(textwrap.dedent("""\
        POST /appointments
        Authorization: Bearer <patient_token>

        {
          "doctor_id": 1,
          "start_datetime": "2025-06-15T10:00:00Z",
          "end_datetime": "2025-06-15T11:00:00Z"
        }"""))
    pdf._bold_body("Response (201 Created):")
    pdf._code_block(textwrap.dedent("""\
        {
          "id": 1,
          "doctor_id": 1,
          "patient_id": 2,
          "start_datetime": "2025-06-15T10:00:00+00:00",
          "end_datetime": "2025-06-15T11:00:00+00:00",
          "status": "scheduled",
          "cancelled_by": null
        }"""))

    pdf._heading(3, "DELETE /appointments/{id}")
    pdf._body("Cancel an appointment (patient or doctor). Rules:")
    pdf._bullet("User must be the appointment's doctor or patient (403 NOT_APPOINTMENT_OWNER)")
    pdf._bullet("Cancellation at least 12 hours before start (422 CANCELLATION_TOO_LATE)")
    pdf._bullet("Cannot cancel an already-cancelled appointment (409 ALREADY_CANCELLED)")
    pdf._body("Returns 204 No Content on success.")

    pdf._heading(3, "GET /appointments")
    pdf._body(
        "List the authenticated user's own appointments. Doctors see appointments "
        "where they are the doctor; patients see theirs."
    )
    pdf._bold_body("Query Parameters:")
    pdf._bullet("skip, limit - pagination (defaults: 0, 20)")
    pdf._bullet("date_from, date_to - filter by date range (ISO format)")
    pdf._bullet("status - filter by 'scheduled' or 'cancelled'")
    pdf._bold_body("Response (200 OK):")
    pdf._code_block(textwrap.dedent("""\
        {
          "items": [ ... ],
          "total": 5,
          "skip": 0,
          "limit": 20
        }"""))

    # ── 1.6 Error Codes Reference ────────────────────────────────────
    pdf.add_page()
    pdf._heading(2, "1.6 Error Codes Reference")
    pdf._body("All application errors return a consistent JSON structure:")
    pdf._code_block(textwrap.dedent("""\
        {
          "detail": {
            "code": "ERROR_CODE",
            "message": "Human-readable description."
          }
        }"""))

    pdf._table(
        ["HTTP", "Code", "Description"],
        [
            ["401", "INVALID_CREDENTIALS", "Wrong email or password"],
            ["401", "INVALID_TOKEN", "Missing, expired, or malformed JWT"],
            ["403", "NOT_PERSONAL_DOCTOR", "Doctor is not the patient's assigned doctor"],
            ["403", "NOT_APPOINTMENT_OWNER", "User is not party to the appointment"],
            ["403", "DOCTOR_REQUIRED", "Endpoint requires doctor role"],
            ["403", "PATIENT_REQUIRED", "Endpoint requires patient role"],
            ["404", "DOCTOR_NOT_FOUND", "No doctor with the given ID"],
            ["404", "PATIENT_NOT_FOUND", "No patient profile for the user"],
            ["404", "APPOINTMENT_NOT_FOUND", "No appointment with the given ID"],
            ["404", "OVERRIDE_NOT_FOUND", "No active temporary override"],
            ["409", "EMAIL_EXISTS", "Email already registered"],
            ["409", "APPOINTMENT_OVERLAP", "Time slot overlaps existing appointment"],
            ["409", "OVERRIDE_EXISTS", "Doctor already has a temp override"],
            ["409", "ALREADY_CANCELLED", "Appointment was already cancelled"],
            ["422", "TOO_SOON", "Appointment less than 24h in the future"],
            ["422", "CANCELLATION_TOO_LATE", "Less than 12h before appointment"],
            ["422", "OUTSIDE_WORKING_HOURS", "Appointment outside effective hours"],
            ["422", "INVALID_TIME_RANGE", "End before start, or cross-day"],
            ["422", "EFFECTIVE_DATE_TOO_SOON", "Permanent change < 7 days ahead"],
            ["422", "SCHEDULE_CONFLICTS_APPOINTMENT", "Schedule change conflicts with bookings"],
            ["422", "INVALID_OVERRIDE_WINDOW", "Override end before start"],
        ],
        col_widths=[8, 40, 52],
    )

    pdf._heading(2, "HTTP Status Code Summary")
    pdf._table(
        ["Code", "Meaning", "Used For"],
        [
            ["200", "OK", "Successful GET, PUT"],
            ["201", "Created", "Successful POST that creates a resource"],
            ["204", "No Content", "Successful DELETE"],
            ["400", "Bad Request", "Malformed JSON / missing fields (Pydantic)"],
            ["401", "Unauthorized", "Missing or invalid JWT"],
            ["403", "Forbidden", "Wrong role or not the resource owner"],
            ["404", "Not Found", "Resource does not exist"],
            ["409", "Conflict", "Duplicate / overlap / already exists"],
            ["422", "Unprocessable Entity", "Business rule violation"],
        ],
        col_widths=[8, 22, 70],
    )

    # ═══════════════════════════════════════════════════════════════════
    # 2. ARCHITECTURE DESCRIPTION
    # ═══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf._heading(1, "2. Architecture Description")

    # ── 2.1 High-Level Architecture ──────────────────────────────────
    pdf._heading(2, "2.1 High-Level Architecture")
    pdf._body(
        "The application follows a layered architecture with clear separation between "
        "HTTP concerns, business logic, and data persistence:"
    )
    pdf._code_block(textwrap.dedent("""\
        +-------------------+
        |  HTTP Client      |
        +--------+----------+
                 |  JSON over HTTP
        +--------v----------+
        |  FastAPI Routers  |   Thin HTTP adapters: parse request,
        |  (auth, doctors,  |   call service, return response.
        |   patients,       |   No business logic here.
        |   schedules,      |
        |   appointments)   |
        +--------+----------+
                 |
        +--------v----------+
        |  Service Layer    |   All business rules, validations,
        |  (**/service.py)  |   and orchestration live here.
        +--------+----------+   Raises custom AppException subclasses.
                 |
        +--------v----------+
        |  SQLAlchemy ORM   |   Declarative models define tables,
        |  (**/models.py)   |   relationships, and constraints.
        +--------+----------+
                 |
        +--------v----------+
        |  SQLite (async)   |   aiosqlite driver; Alembic migrations
        +-------------------+   manage schema evolution.

        Cross-cutting:
        - Pydantic schemas (**/schemas.py) define API contracts
        - Custom exceptions (common/exceptions.py)
        - Global error handlers (common/error_handlers.py)
        - JWT middleware (dependencies.py + auth/security.py)"""))

    # ── 2.2 Project Structure ────────────────────────────────────────
    pdf._heading(2, "2.2 Project Structure")
    pdf._body(
        "The codebase uses feature-based module organization. Each domain concept "
        "(auth, doctors, patients, schedules, appointments) has its own package with "
        "router, service, schemas, and models. Shared utilities live in common/."
    )
    pdf._code_block(textwrap.dedent("""\
        app/
        +-- main.py              App factory, lifespan, router mounting
        +-- config.py            Pydantic-settings (.env loading)
        +-- database.py          Async engine, session factory, Base
        +-- dependencies.py      get_db, get_current_user, role guards
        +-- auth/
        |   +-- router.py        POST register/doctor, register/patient, login
        |   +-- service.py       Registration, login logic
        |   +-- schemas.py       Request/response Pydantic models
        |   +-- security.py      JWT create/decode, password hash/verify
        |   +-- models.py        User model (shared auth identity)
        +-- doctors/
        |   +-- router.py        GET /doctors, GET /doctors/{id}
        |   +-- service.py       List + detail with eager-loaded hours
        |   +-- schemas.py       DoctorResponse, DoctorListResponse
        |   +-- models.py        Doctor model (1:1 FK to users)
        +-- patients/
        |   +-- router.py        GET /patients/me
        |   +-- service.py       Profile retrieval
        |   +-- schemas.py       PatientResponse
        |   +-- models.py        Patient model (FK to users + doctors)
        +-- schedules/
        |   +-- router.py        Schedule CRUD endpoints
        |   +-- service.py       CRUD + effective schedule resolution
        |   +-- schemas.py       TimeSlot, Override, PermanentChange DTOs
        |   +-- models.py        WorkingHours, TempOverride, PermanentChange
        |   +-- slot_fitting.py  Shared interval-in-slot predicate
        |   +-- appointment_conflicts.py  Pre-commit conflict check
        +-- appointments/
        |   +-- router.py        POST, DELETE, GET /appointments
        |   +-- service.py       Create, cancel, list + validations
        |   +-- schemas.py       AppointmentCreate/Response/ListFilters
        |   +-- models.py        Appointment model
        +-- common/
            +-- exceptions.py    AppException hierarchy
            +-- error_handlers.py  Global exception -> JSON handlers"""))

    # ── 2.3 Database Schema ──────────────────────────────────────────
    pdf.add_page()
    pdf._heading(2, "2.3 Database Schema (ER Diagram)")
    pdf._body(
        "Seven tables with referential integrity enforced via foreign keys. "
        "SQLite PRAGMA foreign_keys=ON is set on every connection."
    )
    pdf._code_block(textwrap.dedent("""\
        +------------------+          +------------------+
        |     users        |          |     doctors      |
        +------------------+          +------------------+
        | PK id            |<---+  +->| PK id (FK users) |
        | email (UNIQUE)   |    |  |  | name             |
        | hashed_password  |    |  |  | address          |
        | role (doctor|    |    |  |  | created_at       |
        |   patient)       |    |  |  | updated_at       |
        | created_at       |    |  |  +------------------+
        | updated_at       |    |  |         |
        +------------------+    |  |         | 1
                                |  |         |
        +------------------+    |  |    +----v-----------+
        |    patients      |    |  |    | working_hours  |
        +------------------+    |  |    +----------------+
        | PK id (FK users) |----+  |    | PK id          |
        | name             |       |    | FK doctor_id   |
        | phone            |       |    | day_of_week    |
        | FK doctor_id  ---+-------+    | start_time     |
        | created_at       |            | end_time       |
        | updated_at       |            | is_break       |
        +------------------+            +----------------+
               |
               | 1                 +---------------------+
               |                   | temporary_overrides  |
        +------v-----------+       +---------------------+
        |  appointments    |       | PK id               |
        +------------------+       | FK doctor_id (UNQ)  |
        | PK id            |       | start_datetime      |
        | FK doctor_id     |       | end_datetime        |
        | FK patient_id    |       | created_at          |
        | start_datetime   |       | updated_at          |
        | end_datetime     |       +---------------------+
        | status           |              |
        | cancelled_by     |              | 1
        | created_at       |              |
        | updated_at       |    +---------v--------------+
        +------------------+    | temp_override_hours    |
                                +------------------------+
                                | PK id                  |
        +-------------------+   | FK override_id         |
        | permanent_changes |   | day_of_week            |
        +-------------------+   | start_time, end_time   |
        | PK id             |   | is_break               |
        | FK doctor_id      |   +------------------------+
        | effective_date    |
        | applied           |   +------------------------+
        | created_at        |   | perm_change_hours      |
        +-------------------+   +------------------------+
               |                | PK id                  |
               +--------------->| FK change_id           |
                     1          | day_of_week            |
                                | start_time, end_time   |
                                | is_break               |
                                +------------------------+"""))

    pdf._body("Key constraints:")
    pdf._bullet("users.email has a UNIQUE index")
    pdf._bullet("temporary_overrides.doctor_id is UNIQUE (max 1 per doctor)")
    pdf._bullet("working_hours has UNIQUE(doctor_id, day_of_week, start_time)")
    pdf._bullet("Appointments have a composite index on (doctor_id, start_datetime, end_datetime)")
    pdf._bullet("CHECK constraints enforce valid role, status, and day_of_week values")

    # ── 2.4 Class Diagram ────────────────────────────────────────────
    pdf.add_page()
    pdf._heading(2, "2.4 Class Diagram (UML)")
    pdf._body(
        "The class diagram below shows the main domain models and their relationships. "
        "All models inherit from SQLAlchemy's DeclarativeBase. Models with timestamps "
        "mix in TimestampMixin."
    )
    pdf._code_block(textwrap.dedent("""\
        +===============================+
        |         <<mixin>>             |
        |       TimestampMixin          |
        +-------------------------------+
        | + created_at: datetime        |
        | + updated_at: datetime        |
        +===============================+
              ^        ^        ^
              |        |        |
        +-----+--+ +---+----+ ++--------+--------+
        |  User  | | Doctor | |       Patient     |
        +--------+ +--------+ +------------------+
        |id (PK) | |id (PK, | |id (PK,FK->users)|
        |email   | | FK->   | |name              |
        |hashed_ | | users) | |phone             |
        | password| |name   | |doctor_id (FK)    |
        |role    | |address | +------------------+
        +--------+ +--------+        |
             |          |             |
             |     +----+----+       |
             |     |         |       |
             |  +--v------+  |  +----v---------+
             |  |Working  |  |  | Appointment  |
             |  |Hours    |  |  +--------------+
             |  +---------+  |  |id (PK)       |
             |  |id       |  |  |doctor_id(FK) |
             |  |doctor_id|  |  |patient_id(FK)|
             |  |day_of_  |  |  |start_datetime|
             |  | week    |  |  |end_datetime  |
             |  |start_   |  |  |status        |
             |  | time    |  |  |cancelled_by  |
             |  |end_time |  |  +--------------+
             |  |is_break |  |
             |  +---------+  |
             |               |
             |  +------------v---------+
             |  | TemporaryOverride    |
             |  +----------------------+
             |  |id, doctor_id (UNQ)   |
             |  |start/end_datetime    |
             |  +----------------------+
             |         | 1..*
             |  +------v---------------+
             |  | TempOverrideHours    |
             |  +----------------------+
             |  |override_id (FK)      |
             |  |day, start, end, break|
             |  +----------------------+
             |
             |  +-----------------------+
             |  | PermanentChange       |
             |  +-----------------------+
             |  |id, doctor_id (FK)     |
             |  |effective_date, applied|
             |  +-----------------------+
             |         | 1..*
             |  +------v----------------+
             |  | PermanentChangeHours  |
             |  +-----------------------+
             |  |change_id (FK)         |
             |  |day, start, end, break |
             |  +-----------------------+

        Service Layer (key classes / functions):
        +--------------------------------------------+
        | auth/service.py                            |
        |   register_doctor(), register_patient(),   |
        |   authenticate()                           |
        +--------------------------------------------+
        | schedules/service.py                       |
        |   get_effective_schedule()                  |
        |   update_working_hours()                   |
        |   create_temporary_override()              |
        |   create_permanent_change()                |
        |   apply_pending_permanent_changes()        |
        +--------------------------------------------+
        | appointments/service.py                    |
        |   create_appointment()                     |
        |   cancel_appointment()                     |
        |   list_appointments()                      |
        +--------------------------------------------+
        | dependencies.py                            |
        |   get_db(), get_current_user()             |
        |   require_doctor(), require_patient()      |
        +--------------------------------------------+"""))

    # ── 2.5 Sequence Diagrams ────────────────────────────────────────
    pdf.add_page()
    pdf._heading(2, "2.5 Sequence Diagrams")

    pdf._heading(3, "2.5.1 Create Appointment Flow")
    pdf._code_block(textwrap.dedent("""\
        Patient              Router             Service             DB
          |                    |                   |                 |
          |-- POST /appt ----->|                   |                 |
          |                    |-- create_appt --->|                 |
          |                    |                   |-- SELECT patient|
          |                    |                   |<-- patient row -|
          |                    |                   |                 |
          |                    |                   | [check personal doctor]
          |                    |                   | [check 24h rule]
          |                    |                   | [check same day]
          |                    |                   |                 |
          |                    |                   |-- get_effective |
          |                    |                   |   _schedule  -->|
          |                    |                   |<-- slots -------|
          |                    |                   |                 |
          |                    |                   | [check fits in slot]
          |                    |                   |                 |
          |                    |                   |-- SELECT count  |
          |                    |                   |   (overlap)  -->|
          |                    |                   |<-- count -------|
          |                    |                   |                 |
          |                    |                   | [check no overlap]
          |                    |                   |                 |
          |                    |                   |-- INSERT appt ->|
          |                    |                   |-- COMMIT ------>|
          |                    |                   |<-- appt row ----|
          |                    |<-- AppointmentResponse -------------|
          |<-- 201 Created ----|                   |                 |"""))

    pdf._heading(3, "2.5.2 Schedule Resolution (get_effective_schedule)")
    pdf._code_block(textwrap.dedent("""\
        Caller               Service                   DB
          |                    |                         |
          |-- get_effective -->|                         |
          |   (doctor, date)   |                         |
          |                    |-- apply_pending         |
          |                    |   (separate session) -->|
          |                    |<-- committed -----------|
          |                    |                         |
          |                    |-- SELECT temp_override  |
          |                    |   WHERE covers date  -->|
          |                    |<-- override or NULL ----|
          |                    |                         |
          |             [if override found: return override slots]
          |                    |                         |
          |                    |-- SELECT perm_change    |
          |                    |   WHERE eff_date<=date->|
          |                    |<-- change or NULL ------|
          |                    |                         |
          |             [if perm change found: return its slots]
          |                    |                         |
          |                    |-- SELECT working_hours  |
          |                    |   WHERE weekday ------->|
          |                    |<-- base slots ----------|
          |                    |                         |
          |<-- list[TimeSlot] -|                         |"""))

    pdf._heading(3, "2.5.3 Schedule Update with Conflict Check")
    pdf._code_block(textwrap.dedent("""\
        Doctor               Router             Service             DB
          |                    |                   |                 |
          |-- PUT schedule --->|                   |                 |
          |                    |-- update_wh ----->|                 |
          |                    |                   |-- DELETE old -->|
          |                    |                   |-- INSERT new -->|
          |                    |                   |-- FLUSH ------->|
          |                    |                   |                 |
          |                    |                   |-- assert_no     |
          |                    |                   |   conflicts --->|
          |                    |                   |  (for each      |
          |                    |                   |   scheduled     |
          |                    |                   |   appointment:  |
          |                    |                   |   check fits    |
          |                    |                   |   new slots)    |
          |                    |                   |                 |
          |              [if conflict: ROLLBACK, raise 422]
          |              [if ok: COMMIT]
          |                    |                   |                 |
          |<-- 200 OK ---------|                   |                 |"""))

    # ═══════════════════════════════════════════════════════════════════
    # 3. SELF-ANALYSIS
    # ═══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf._heading(1, "3. Self-Analysis")

    # ── 3.1 SOLID ────────────────────────────────────────────────────
    pdf._heading(2, "3.1 SOLID Principles Adherence")

    pdf._heading(3, "Single Responsibility Principle (SRP)")
    pdf._body(
        "Each module handles exactly one domain concept. Within a module, "
        "responsibilities are further separated:"
    )
    pdf._bullet("Routers handle HTTP parsing and response formatting only.")
    pdf._bullet("Services contain all business logic, validation, and orchestration.")
    pdf._bullet("Models define persistence structure and database constraints.")
    pdf._bullet("Schemas define the API contract (request validation, response shape).")
    pdf._bullet(
        "The common/ package centralizes cross-cutting concerns: exception classes "
        "in exceptions.py and global error handlers in error_handlers.py."
    )
    pdf._body(
        "Example: appointments/service.py owns all booking rules (24h, overlap, working hours). "
        "The router never checks business rules; it delegates entirely to the service."
    )

    pdf._heading(3, "Open/Closed Principle (OCP)")
    pdf._body(
        "The schedule resolution system demonstrates OCP. The get_effective_schedule() function "
        "checks three schedule layers in priority order (temporary override > permanent change > "
        "base working hours). Adding a new layer (e.g., holiday calendars) requires adding a new "
        "model and inserting one more check step, without modifying the existing override or "
        "permanent-change logic."
    )
    pdf._body(
        "The exception hierarchy (AppException -> BusinessRuleException, ConflictException, etc.) "
        "is also open for extension. New error types can be added without changing the global "
        "error handler, which catches the base AppException class."
    )

    pdf._heading(3, "Liskov Substitution Principle (LSP)")
    pdf._body(
        "Both Doctor and Patient link to User via a 1:1 foreign key. Any code that operates on "
        "a User (authentication, token creation, get_current_user dependency) works identically "
        "regardless of whether the user is a doctor or patient. The role field is used for "
        "authorization checks (require_doctor, require_patient), but the authentication flow "
        "itself is fully substitutable."
    )

    pdf._heading(3, "Interface Segregation Principle (ISP)")
    pdf._body(
        "Pydantic schemas are scoped per operation. DoctorRegisterRequest, PatientRegisterRequest, "
        "LoginRequest, and TokenResponse are all separate models. The appointment module has "
        "distinct AppointmentCreateRequest, AppointmentResponse, and AppointmentListFilters. "
        "No client is forced to deal with fields irrelevant to their operation."
    )
    pdf._body(
        "FastAPI dependencies (get_current_user, require_doctor, require_patient) are "
        "fine-grained. Endpoints declare exactly the auth level they need."
    )

    pdf._heading(3, "Dependency Inversion Principle (DIP)")
    pdf._body(
        "Services depend on the AsyncSession abstraction, never on concrete engine details. "
        "This is demonstrated by the test suite, which seamlessly swaps the production SQLite "
        "file for an in-memory database by overriding the get_db dependency. "
        "No service code changes are needed."
    )
    pdf._body(
        "The dependency injection pattern via FastAPI's Depends() mechanism decouples "
        "request handling from database session management and authentication."
    )

    # ── 3.2 Design Trade-offs ────────────────────────────────────────
    pdf._heading(2, "3.2 Design Trade-offs")

    pdf._heading(3, "SQLite vs. PostgreSQL")
    pdf._body(
        "SQLite was chosen for simplicity (zero-config, file-based). This suits the project "
        "scope perfectly but limits concurrent write throughput and advanced features like "
        "LISTEN/NOTIFY. The async driver (aiosqlite) wraps synchronous SQLite in a thread pool. "
        "Migration to PostgreSQL requires only changing DATABASE_URL and installing asyncpg; "
        "all queries use the ORM and are database-agnostic."
    )

    pdf._heading(3, "Eager Promotion of Permanent Changes")
    pdf._body(
        "Permanent schedule changes are promoted to base working_hours both at startup (lifespan) "
        "and on-demand before each get_effective_schedule() call. This is simple and correct but "
        "performs a global scan of all unapplied changes on every schedule read. For a "
        "course-scale application this is negligible; at scale, a background scheduler (e.g., "
        "Celery beat, APScheduler, or a cron job) would be more appropriate."
    )

    pdf._heading(3, "Appointment Conflict Check on Schedule Mutation")
    pdf._body(
        "When a doctor updates their schedule, the system checks all scheduled appointments "
        "against the new effective hours and rejects the change if any appointment would be "
        "orphaned. An alternative design would flag or auto-cancel conflicting appointments, "
        "but the reject-with-422 approach was chosen for safety: no patient loses a booking "
        "without explicit action."
    )

    pdf._heading(3, "JWT Without Refresh Tokens")
    pdf._body(
        "The current auth system issues a single access token with a 60-minute expiry. "
        "There is no refresh token flow. This simplifies the implementation but means "
        "clients must re-authenticate after expiry. Adding refresh tokens would be a "
        "natural enhancement for production use."
    )

    # ── 3.3 Areas for Improvement ────────────────────────────────────
    pdf._heading(2, "3.3 Areas for Improvement")

    pdf._bullet(
        "Pagination consistency: Use cursor-based pagination instead of offset/limit "
        "for better performance on large datasets."
    )
    pdf._bullet(
        "Rate limiting: No rate limiting is implemented. Production deployments should "
        "add middleware or reverse-proxy-level throttling."
    )
    pdf._bullet(
        "Refresh tokens: Implement a token refresh flow to improve UX without "
        "compromising security."
    )
    pdf._bullet(
        "Email notifications: Notify patients and doctors on appointment creation, "
        "cancellation, and schedule changes."
    )
    pdf._bullet(
        "Admin endpoints: No admin role exists. Adding one would enable centralized "
        "management of users, appointments, and schedules."
    )
    pdf._bullet(
        "Soft-delete and audit trail: Cancelled appointments set a status flag, but "
        "other entities use hard deletes. A comprehensive audit log would improve "
        "traceability."
    )
    pdf._bullet(
        "Timezone handling: All datetimes are stored and processed in UTC. "
        "Client-side timezone conversion is left to the consumer. An explicit "
        "timezone-aware API (accepting IANA tz names) would improve usability."
    )
    pdf._bullet(
        "Background job for promotions: Replace the on-demand "
        "apply_pending_permanent_changes with a dedicated scheduler to avoid "
        "per-request overhead at scale."
    )
    pdf._bullet(
        "Docker health checks: The Dockerfile and docker-compose.yml do not include "
        "a HEALTHCHECK directive. Adding one would improve container orchestration."
    )
    pdf._bullet(
        "API versioning: All routes are currently unversioned (/auth, /doctors, etc.). "
        "Prefixing with /v1/ would enable backward-compatible evolution."
    )

    # ── Output ───────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    build_pdf("docs/Doctor_Visit_Booking_API_Documentation.pdf")
