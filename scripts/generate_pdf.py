#!/usr/bin/env python3
"""Generate the project PDF documentation (Phase 9 deliverable).

Run:  python scripts/generate_pdf.py
Output: docs/Doctor_Visit_Booking_API_Documentation.pdf
"""

from __future__ import annotations

import os
import textwrap

from fpdf import FPDF  # type: ignore[misc]


FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


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
        self.add_font("ArialUni", "", FONT_PATH)
        self.add_font("ArialUni", "B", FONT_PATH)
        self.add_font("ArialUni", "I", FONT_PATH)
        self.add_font("ArialUni", "BI", FONT_PATH)

    def _heading(self, level: int, text: str) -> None:
        sizes = {1: 22, 2: 16, 3: 13}
        self.ln(4 if level > 1 else 8)
        self.set_font("ArialUni", "B", sizes.get(level, 12))
        self.set_text_color(*self.COL_HEADER)
        self.multi_cell(0, 8, text)
        if level == 1:
            self.set_draw_color(*self.COL_ACCENT)
            self.set_line_width(0.6)
            self.line(self.MARGIN, self.get_y(), self.w - self.MARGIN, self.get_y())
            self.ln(3)
        self.ln(2)

    def _body(self, text: str) -> None:
        self.set_font("ArialUni", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def _bold_body(self, text: str) -> None:
        self.set_font("ArialUni", "B", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def _bullet(self, text: str, indent: int = 6) -> None:
        self.set_font("ArialUni", "", 10)
        self.set_text_color(30, 30, 30)
        x = self.get_x()
        self.set_x(x + indent)
        self.multi_cell(0, 5, f"\u2022  {text}")
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

        self.set_font("ArialUni", "B", 9)
        self.set_fill_color(*self.COL_HEADER)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(cw[i], 7, f" {h}", border=1, fill=True)
        self.ln()

        self.set_font("ArialUni", "", 8.5)
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

    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("ArialUni", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, "Doctor Visit Booking API \u2014 \u0422\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0430 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430\u0446\u0438\u044f", align="C")
        self.ln(10)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("ArialUni", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"\u0421\u0442\u0440\u0430\u043d\u0438\u0446\u0430 {self.page_no()}/{{nb}}", align="C")


def build_pdf(output_path: str) -> None:
    pdf = PDF()
    pdf.alias_nb_pages()

    # ═══════════════════════════════════════════════════════════════════
    # TITLE PAGE
    # ═══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.ln(45)
    pdf.set_font("ArialUni", "B", 30)
    pdf.set_text_color(*PDF.COL_HEADER)
    pdf.cell(0, 14, "Doctor Visit Booking API", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("ArialUni", "", 16)
    pdf.set_text_color(*PDF.COL_ACCENT)
    pdf.cell(0, 10, "\u0422\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0430 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430\u0446\u0438\u044f", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(12)
    pdf.set_draw_color(*PDF.COL_ACCENT)
    pdf.set_line_width(0.5)
    mid = pdf.w / 2
    pdf.line(mid - 40, pdf.get_y(), mid + 40, pdf.get_y())
    pdf.ln(12)
    pdf.set_font("ArialUni", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 7, "REST API \u0437\u0430 \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043d\u0430 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f \u043d\u0430 \u043f\u0430\u0446\u0438\u0435\u043d\u0442\u0438 \u043f\u0440\u0438 \u043b\u0435\u043a\u0430\u0440\u0438", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "FastAPI  |  SQLAlchemy 2.0  |  SQLite  |  JWT Auth", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(40)
    pdf.set_font("ArialUni", "I", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "\u0412\u0435\u0440\u0441\u0438\u044f 0.1.0", align="C", new_x="LMARGIN", new_y="NEXT")

    # ═══════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf._heading(1, "\u0421\u044a\u0434\u044a\u0440\u0436\u0430\u043d\u0438\u0435")
    toc = [
        "1. \u0420\u044a\u043a\u043e\u0432\u043e\u0434\u0441\u0442\u0432\u043e \u0437\u0430 \u0438\u0437\u043f\u043e\u043b\u0437\u0432\u0430\u043d\u0435 \u043d\u0430 API",
        "   1.1 \u0410\u0443\u0442\u0435\u043d\u0442\u0438\u043a\u0430\u0446\u0438\u044f",
        "   1.2 \u041b\u0435\u043a\u0430\u0440\u0438",
        "   1.3 \u041f\u0430\u0446\u0438\u0435\u043d\u0442\u0438",
        "   1.4 \u0420\u0430\u0431\u043e\u0442\u043d\u043e \u0432\u0440\u0435\u043c\u0435 \u0438 \u0433\u0440\u0430\u0444\u0438\u0446\u0438",
        "   1.5 \u0417\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f (\u0447\u0430\u0441\u043e\u0432\u0435)",
        "   1.6 \u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a \u043d\u0430 \u043a\u043e\u0434\u043e\u0432\u0435 \u0437\u0430 \u0433\u0440\u0435\u0448\u043a\u0438",
        "2. \u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u043d\u0430 \u0430\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u0430\u0442\u0430",
        "   2.1 \u0410\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u0430 \u043d\u0430 \u0432\u0438\u0441\u043e\u043a\u043e \u043d\u0438\u0432\u043e",
        "   2.2 \u0421\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430 \u043d\u0430 \u043f\u0440\u043e\u0435\u043a\u0442\u0430",
        "   2.3 \u0421\u0445\u0435\u043c\u0430 \u043d\u0430 \u0431\u0430\u0437\u0430\u0442\u0430 \u0434\u0430\u043d\u043d\u0438 (ER \u0434\u0438\u0430\u0433\u0440\u0430\u043c\u0430)",
        "   2.4 \u041a\u043b\u0430\u0441\u043e\u0432\u0430 \u0434\u0438\u0430\u0433\u0440\u0430\u043c\u0430",
        "   2.5 \u0414\u0438\u0430\u0433\u0440\u0430\u043c\u0438 \u043d\u0430 \u043f\u043e\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u0442\u0435\u043b\u043d\u043e\u0441\u0442\u0442\u0430",
        "3. \u0421\u0430\u043c\u043e\u0430\u043d\u0430\u043b\u0438\u0437",
        "   3.1 \u0421\u043f\u0430\u0437\u0432\u0430\u043d\u0435 \u043d\u0430 SOLID \u043f\u0440\u0438\u043d\u0446\u0438\u043f\u0438\u0442\u0435",
        "   3.2 \u041f\u0440\u043e\u0435\u043a\u0442\u043d\u0438 \u043a\u043e\u043c\u043f\u0440\u043e\u043c\u0438\u0441\u0438",
        "   3.3 \u041e\u0431\u043b\u0430\u0441\u0442\u0438 \u0437\u0430 \u043f\u043e\u0434\u043e\u0431\u0440\u0435\u043d\u0438\u0435",
    ]
    for entry in toc:
        pdf._body(entry)

    # ═══════════════════════════════════════════════════════════════════
    # 1. API USAGE GUIDE
    # ═══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf._heading(1, "1. \u0420\u044a\u043a\u043e\u0432\u043e\u0434\u0441\u0442\u0432\u043e \u0437\u0430 \u0438\u0437\u043f\u043e\u043b\u0437\u0432\u0430\u043d\u0435 \u043d\u0430 API")
    pdf._body(
        "API-\u0442\u043e \u0441\u0435 \u0441\u0435\u0440\u0432\u0438\u0440\u0430 \u043d\u0430 http://localhost:8000 \u043f\u043e \u043f\u043e\u0434\u0440\u0430\u0437\u0431\u0438\u0440\u0430\u043d\u0435. \u0418\u043d\u0442\u0435\u0440\u0430\u043a\u0442\u0438\u0432\u0435\u043d Swagger UI "
        "\u0435 \u043d\u0430\u043b\u0438\u0447\u0435\u043d \u043d\u0430 /docs, \u0430 ReDoc \u043d\u0430 /redoc. \u0412\u0441\u0438\u0447\u043a\u0438 \u0442\u0435\u043b\u0430 \u043d\u0430 \u0437\u0430\u044f\u0432\u043a\u0438 \u0438 \u043e\u0442\u0433\u043e\u0432\u043e\u0440\u0438 \u0441\u0430 \u0432 JSON \u0444\u043e\u0440\u043c\u0430\u0442. "
        "\u0417\u0430\u0449\u0438\u0442\u0435\u043d\u0438\u0442\u0435 \u043a\u0440\u0430\u0439\u043d\u0438 \u0442\u043e\u0447\u043a\u0438 \u0438\u0437\u0438\u0441\u043a\u0432\u0430\u0442 \u0445\u0435\u0434\u044a\u0440 Authorization: Bearer <token>."
    )

    # -- 1.1 Authentication
    pdf._heading(2, "1.1 \u0410\u0443\u0442\u0435\u043d\u0442\u0438\u043a\u0430\u0446\u0438\u044f")
    pdf._body(
        "\u0421\u0438\u0441\u0442\u0435\u043c\u0430\u0442\u0430 \u0438\u0437\u043f\u043e\u043b\u0437\u0432\u0430 JWT (JSON Web Tokens) \u0437\u0430 \u0430\u0443\u0442\u0435\u043d\u0442\u0438\u043a\u0430\u0446\u0438\u044f. "
        "\u0422\u043e\u043a\u0435\u043d\u0438\u0442\u0435 \u0441\u0435 \u043f\u043e\u043b\u0443\u0447\u0430\u0432\u0430\u0442 \u0447\u0440\u0435\u0437 \u043a\u0440\u0430\u0439\u043d\u0430\u0442\u0430 \u0442\u043e\u0447\u043a\u0430 \u0437\u0430 \u0432\u0445\u043e\u0434 \u0438 \u0438\u0437\u0442\u0438\u0447\u0430\u0442 \u0441\u043b\u0435\u0434 60 \u043c\u0438\u043d\u0443\u0442\u0438 (\u043a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0438\u0440\u0443\u0435\u043c\u043e). "
        "\u041b\u0435\u043a\u0430\u0440\u0438 \u0438 \u043f\u0430\u0446\u0438\u0435\u043d\u0442\u0438 \u0441\u0435 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0438\u0440\u0430\u0442 \u043e\u0442\u0434\u0435\u043b\u043d\u043e; \u0438 \u0434\u0432\u0430\u0442\u0430 \u043f\u043e\u043b\u0443\u0447\u0430\u0432\u0430\u0442 \u0442\u043e\u043a\u0435\u043d \u043f\u0440\u0438 \u0443\u0441\u043f\u0435\u0448\u043d\u0430 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044f."
    )

    pdf._heading(3, "POST /auth/register/doctor")
    pdf._body("\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0438\u0440\u0430\u043d\u0435 \u043d\u0430 \u043d\u043e\u0432 \u043b\u0435\u043a\u0430\u0440\u0441\u043a\u0438 \u0430\u043a\u0430\u0443\u043d\u0442 \u0441 \u043d\u0430\u0447\u0430\u043b\u043d\u043e \u0440\u0430\u0431\u043e\u0442\u043d\u043e \u0432\u0440\u0435\u043c\u0435.")
    pdf._bold_body("\u0417\u0430\u044f\u0432\u043a\u0430:")
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
    pdf._bold_body("\u041e\u0442\u0433\u043e\u0432\u043e\u0440 (201 Created):")
    pdf._code_block(textwrap.dedent("""\
        {
          "access_token": "eyJhbGciOiJIUzI1NiIs...",
          "token_type": "bearer"
        }"""))

    pdf._heading(3, "POST /auth/register/patient")
    pdf._body("\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0438\u0440\u0430\u043d\u0435 \u043d\u0430 \u043d\u043e\u0432 \u043f\u0430\u0446\u0438\u0435\u043d\u0442\u0441\u043a\u0438 \u0430\u043a\u0430\u0443\u043d\u0442, \u0441\u0432\u044a\u0440\u0437\u0430\u043d \u0441 \u043b\u0438\u0447\u0435\u043d \u043b\u0435\u043a\u0430\u0440.")
    pdf._bold_body("\u0417\u0430\u044f\u0432\u043a\u0430:")
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
    pdf._bold_body("\u041e\u0442\u0433\u043e\u0432\u043e\u0440 (201 Created):")
    pdf._code_block(textwrap.dedent("""\
        {
          "access_token": "eyJhbGciOiJIUzI1NiIs...",
          "token_type": "bearer"
        }"""))

    pdf._heading(3, "POST /auth/login")
    pdf._body("\u0410\u0443\u0442\u0435\u043d\u0442\u0438\u043a\u0430\u0446\u0438\u044f \u0441 \u0438\u043c\u0435\u0439\u043b \u0438 \u043f\u0430\u0440\u043e\u043b\u0430.")
    pdf._bold_body("\u0417\u0430\u044f\u0432\u043a\u0430:")
    pdf._code_block(textwrap.dedent("""\
        POST /auth/login
        Content-Type: application/json

        {
          "email": "smith@clinic.com",
          "password": "securepass123"
        }"""))
    pdf._bold_body("\u041e\u0442\u0433\u043e\u0432\u043e\u0440 (200 OK):")
    pdf._code_block(textwrap.dedent("""\
        {
          "access_token": "eyJhbGciOiJIUzI1NiIs...",
          "token_type": "bearer"
        }"""))
    pdf._bold_body("\u0413\u0440\u0435\u0448\u043a\u0430 (401 Unauthorized):")
    pdf._code_block(textwrap.dedent("""\
        {
          "detail": {
            "code": "INVALID_CREDENTIALS",
            "message": "Incorrect email or password."
          }
        }"""))

    # -- 1.2 Doctors
    pdf._heading(2, "1.2 \u041b\u0435\u043a\u0430\u0440\u0438")

    pdf._heading(3, "GET /doctors")
    pdf._body("\u0421\u043f\u0438\u0441\u044a\u043a \u043d\u0430 \u0432\u0441\u0438\u0447\u043a\u0438 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0438\u0440\u0430\u043d\u0438 \u043b\u0435\u043a\u0430\u0440\u0438 (\u043f\u0443\u0431\u043b\u0438\u0447\u0435\u043d, \u0441 \u043f\u0430\u0433\u0438\u043d\u0430\u0446\u0438\u044f).")
    pdf._bold_body("\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u0438: skip (\u043f\u043e \u043f\u043e\u0434\u0440\u0430\u0437\u0431\u0438\u0440\u0430\u043d\u0435 0), limit (\u043f\u043e \u043f\u043e\u0434\u0440\u0430\u0437\u0431\u0438\u0440\u0430\u043d\u0435 20, \u043c\u0430\u043a\u0441. 100)")
    pdf._bold_body("\u041e\u0442\u0433\u043e\u0432\u043e\u0440 (200 OK):")
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
    pdf._body("\u0418\u0437\u0432\u043b\u0438\u0447\u0430\u043d\u0435 \u043d\u0430 \u043f\u0440\u043e\u0444\u0438\u043b\u0430 \u0438 \u0440\u0430\u0431\u043e\u0442\u043d\u043e\u0442\u043e \u0432\u0440\u0435\u043c\u0435 \u043d\u0430 \u043a\u043e\u043d\u043a\u0440\u0435\u0442\u0435\u043d \u043b\u0435\u043a\u0430\u0440.")
    pdf._bold_body("\u041e\u0442\u0433\u043e\u0432\u043e\u0440 (200 OK): \u0421\u044a\u0449\u0430\u0442\u0430 \u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430 \u043a\u0430\u0442\u043e \u0435\u0434\u0438\u043d \u0435\u043b\u0435\u043c\u0435\u043d\u0442 \u043e\u0442 \u0433\u043e\u0440\u043d\u0438\u044f \u0441\u043f\u0438\u0441\u044a\u043a.")
    pdf._bold_body("\u0413\u0440\u0435\u0448\u043a\u0430 (404 Not Found):")
    pdf._code_block(textwrap.dedent("""\
        {
          "detail": {
            "code": "DOCTOR_NOT_FOUND",
            "message": "No doctor found with the given id."
          }
        }"""))

    # -- 1.3 Patients
    pdf._heading(2, "1.3 \u041f\u0430\u0446\u0438\u0435\u043d\u0442\u0438")

    pdf._heading(3, "GET /patients/me")
    pdf._body("\u0418\u0437\u0432\u043b\u0438\u0447\u0430\u043d\u0435 \u043d\u0430 \u043f\u0440\u043e\u0444\u0438\u043b\u0430 \u043d\u0430 \u0430\u0443\u0442\u0435\u043d\u0442\u0438\u043a\u0438\u0440\u0430\u043d\u0438\u044f \u043f\u0430\u0446\u0438\u0435\u043d\u0442. \u0418\u0437\u0438\u0441\u043a\u0432\u0430 \u0440\u043e\u043b\u044f \u043d\u0430 \u043f\u0430\u0446\u0438\u0435\u043d\u0442.")
    pdf._bold_body("\u0425\u0435\u0434\u044a\u0440\u0438: Authorization: Bearer <token>")
    pdf._bold_body("\u041e\u0442\u0433\u043e\u0432\u043e\u0440 (200 OK):")
    pdf._code_block(textwrap.dedent("""\
        {
          "id": 2,
          "name": "Jane Doe",
          "email": "jane@example.com",
          "phone": "+359888000000",
          "doctor_id": 1
        }"""))

    # -- 1.4 Working Hours & Schedules
    pdf.add_page()
    pdf._heading(2, "1.4 \u0420\u0430\u0431\u043e\u0442\u043d\u043e \u0432\u0440\u0435\u043c\u0435 \u0438 \u0433\u0440\u0430\u0444\u0438\u0446\u0438")
    pdf._body(
        "\u041b\u0435\u043a\u0430\u0440\u0438\u0442\u0435 \u0443\u043f\u0440\u0430\u0432\u043b\u044f\u0432\u0430\u0442 \u0442\u0440\u0438 \u043d\u0438\u0432\u0430 \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u0447\u043d\u0438 \u0434\u0430\u043d\u043d\u0438. "
        "\u041f\u0440\u0438 \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u044f\u043d\u0435 \u043d\u0430 \u0435\u0444\u0435\u043a\u0442\u0438\u0432\u043d\u0438\u044f \u0433\u0440\u0430\u0444\u0438\u043a \u0437\u0430 \u0434\u0430\u0434\u0435\u043d\u0430 \u0434\u0430\u0442\u0430 \u0441\u0438\u0441\u0442\u0435\u043c\u0430\u0442\u0430 \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0432\u0430 \u0432 \u0440\u0435\u0434: "
        "(1) \u0430\u043a\u0442\u0438\u0432\u043d\u043e \u0432\u0440\u0435\u043c\u0435\u043d\u043d\u043e \u043f\u0440\u0435\u0434\u0435\u0444\u0438\u043d\u0438\u0440\u0430\u043d\u0435, \u043f\u043e\u043a\u0440\u0438\u0432\u0430\u0449\u043e \u0434\u0430\u0442\u0430\u0442\u0430; "
        "(2) \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0430 \u043f\u043e\u0441\u0442\u043e\u044f\u043d\u043d\u0430 \u043f\u0440\u043e\u043c\u044f\u043d\u0430 \u0441 effective_date <= \u0434\u0430\u0442\u0430\u0442\u0430; "
        "(3) \u0431\u0430\u0437\u043e\u0432\u043e \u0440\u0430\u0431\u043e\u0442\u043d\u043e \u0432\u0440\u0435\u043c\u0435. \u041f\u044a\u0440\u0432\u043e\u0442\u043e \u0441\u044a\u0432\u043f\u0430\u0434\u0435\u043d\u0438\u0435 \u043f\u0435\u0447\u0435\u043b\u0438."
    )

    pdf._heading(3, "PUT /doctors/me/schedule")
    pdf._body("\u0417\u0430\u043c\u044f\u043d\u0430 \u043d\u0430 \u0431\u0430\u0437\u043e\u0432\u043e\u0442\u043e \u0440\u0430\u0431\u043e\u0442\u043d\u043e \u0432\u0440\u0435\u043c\u0435 \u043d\u0430 \u043b\u0435\u043a\u0430\u0440\u044f (\u0441\u0430\u043c\u043e \u0437\u0430 \u043b\u0435\u043a\u0430\u0440\u0438).")
    pdf._bold_body("\u0417\u0430\u044f\u0432\u043a\u0430:")
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
        "\u0412\u0440\u044a\u0449\u0430 200 \u0441 \u0430\u043a\u0442\u0443\u0430\u043b\u0438\u0437\u0438\u0440\u0430\u043d WeeklyScheduleResponse. "
        "\u0412\u0440\u044a\u0449\u0430 422 SCHEDULE_CONFLICTS_APPOINTMENT \u0430\u043a\u043e \u0441\u044a\u0449\u0435\u0441\u0442\u0432\u0443\u0432\u0430\u0449\u0438 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f "
        "\u0431\u0438\u0445\u0430 \u043f\u043e\u043f\u0430\u0434\u043d\u0430\u043b\u0438 \u0438\u0437\u0432\u044a\u043d \u043d\u043e\u0432\u0438\u0442\u0435 \u0447\u0430\u0441\u043e\u0432\u0435."
    )

    pdf._heading(3, "GET /doctors/{id}/schedule?date=YYYY-MM-DD")
    pdf._body(
        "\u0418\u0437\u0432\u043b\u0438\u0447\u0430\u043d\u0435 \u043d\u0430 \u0435\u0444\u0435\u043a\u0442\u0438\u0432\u043d\u0438\u044f \u0433\u0440\u0430\u0444\u0438\u043a \u043d\u0430 \u043b\u0435\u043a\u0430\u0440 \u0437\u0430 \u043a\u043e\u043d\u043a\u0440\u0435\u0442\u043d\u0430 \u0434\u0430\u0442\u0430. "
        "\u041f\u043e \u043f\u043e\u0434\u0440\u0430\u0437\u0431\u0438\u0440\u0430\u043d\u0435 \u0435 \u0434\u043d\u0435\u0448\u043d\u0430\u0442\u0430 \u0434\u0430\u0442\u0430. \u0412\u0440\u044a\u0449\u0430 \u0441\u043f\u0438\u0441\u044a\u043a \u043e\u0442 TimeSlotResponse \u043e\u0431\u0435\u043a\u0442\u0438."
    )

    pdf._heading(3, "POST /doctors/me/schedule/temporary")
    pdf._body("\u0421\u044a\u0437\u0434\u0430\u0432\u0430\u043d\u0435 \u043d\u0430 \u0432\u0440\u0435\u043c\u0435\u043d\u043d\u043e \u043f\u0440\u0435\u0434\u0435\u0444\u0438\u043d\u0438\u0440\u0430\u043d\u0435 \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u043a\u0430 (\u043c\u0430\u043a\u0441. 1 \u043d\u0430 \u043b\u0435\u043a\u0430\u0440).")
    pdf._bold_body("\u0417\u0430\u044f\u0432\u043a\u0430:")
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
        "\u0412\u0440\u044a\u0449\u0430 201 \u0441 TemporaryOverrideResponse. "
        "\u0412\u0440\u044a\u0449\u0430 409 OVERRIDE_EXISTS \u0430\u043a\u043e \u043b\u0435\u043a\u0430\u0440\u044f\u0442 \u0432\u0435\u0447\u0435 \u0438\u043c\u0430 \u0435\u0434\u043d\u043e. "
        "\u0412\u0440\u044a\u0449\u0430 422 SCHEDULE_CONFLICTS_APPOINTMENT \u0430\u043a\u043e \u0441\u044a\u0449\u0435\u0441\u0442\u0432\u0443\u0432\u0430\u0449\u0438 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f \u043a\u043e\u043d\u0444\u043b\u0438\u043a\u0442\u0443\u0432\u0430\u0442."
    )

    pdf._heading(3, "DELETE /doctors/me/schedule/temporary")
    pdf._body("\u041f\u0440\u0435\u043c\u0430\u0445\u0432\u0430\u043d\u0435 \u043d\u0430 \u0430\u043a\u0442\u0438\u0432\u043d\u043e\u0442\u043e \u0432\u0440\u0435\u043c\u0435\u043d\u043d\u043e \u043f\u0440\u0435\u0434\u0435\u0444\u0438\u043d\u0438\u0440\u0430\u043d\u0435. \u0412\u0440\u044a\u0449\u0430 204 No Content.")

    pdf._heading(3, "POST /doctors/me/schedule/permanent")
    pdf._body("\u041f\u043b\u0430\u043d\u0438\u0440\u0430\u043d\u0435 \u043d\u0430 \u043f\u043e\u0441\u0442\u043e\u044f\u043d\u043d\u0430 \u0441\u043c\u044f\u043d\u0430 \u043d\u0430 \u0440\u0430\u0431\u043e\u0442\u043d\u043e\u0442\u043e \u0432\u0440\u0435\u043c\u0435 (effective_date >= \u0434\u043d\u0435\u0441 + 7 \u0434\u043d\u0438).")
    pdf._bold_body("\u0417\u0430\u044f\u0432\u043a\u0430:")
    pdf._code_block(textwrap.dedent("""\
        {
          "effective_date": "2025-07-01",
          "schedule": [
            {"day_of_week": 0, "start_time": "08:00:00",
             "end_time": "16:00:00", "is_break": false}
          ]
        }"""))
    pdf._body(
        "\u0412\u0440\u044a\u0449\u0430 201 \u0441 PermanentChangeResponse. "
        "\u0412\u0440\u044a\u0449\u0430 422 EFFECTIVE_DATE_TOO_SOON \u0430\u043a\u043e \u0434\u0430\u0442\u0430\u0442\u0430 \u0435 \u043f\u043e-\u043c\u0430\u043b\u043a\u043e \u043e\u0442 7 \u0434\u043d\u0438 \u043d\u0430\u043f\u0440\u0435\u0434. "
        "\u0412\u0440\u044a\u0449\u0430 422 SCHEDULE_CONFLICTS_APPOINTMENT \u0430\u043a\u043e \u0441\u044a\u0449\u0435\u0441\u0442\u0432\u0443\u0432\u0430\u0449\u0438 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f \u043a\u043e\u043d\u0444\u043b\u0438\u043a\u0442\u0443\u0432\u0430\u0442. "
        "\u0427\u0430\u043a\u0430\u0449\u0438\u0442\u0435 \u043f\u043e\u0441\u0442\u043e\u044f\u043d\u043d\u0438 \u043f\u0440\u043e\u043c\u0435\u043d\u0438 \u0441\u0435 \u043f\u0440\u0438\u043b\u0430\u0433\u0430\u0442 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u043d\u043e \u043a\u044a\u043c \u0431\u0430\u0437\u043e\u0432\u043e\u0442\u043e \u0440\u0430\u0431\u043e\u0442\u043d\u043e \u0432\u0440\u0435\u043c\u0435 "
        "\u043f\u0440\u0438 \u0441\u0442\u0430\u0440\u0442\u0438\u0440\u0430\u043d\u0435 \u043d\u0430 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435\u0442\u043e \u0438 \u043f\u0440\u0435\u0434\u0438 \u0432\u0441\u044f\u043a\u043e \u0440\u0430\u0437\u0440\u0435\u0448\u0430\u0432\u0430\u043d\u0435 \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u043a."
    )

    # -- 1.5 Appointments
    pdf.add_page()
    pdf._heading(2, "1.5 \u0417\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f (\u0447\u0430\u0441\u043e\u0432\u0435)")

    pdf._heading(3, "POST /appointments")
    pdf._body("\u0421\u044a\u0437\u0434\u0430\u0432\u0430\u043d\u0435 \u043d\u0430 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0435 (\u0441\u0430\u043c\u043e \u0437\u0430 \u043f\u0430\u0446\u0438\u0435\u043d\u0442\u0438). \u041f\u0440\u0438\u043b\u0430\u0433\u0430\u043d\u0438 \u0431\u0438\u0437\u043d\u0435\u0441 \u043f\u0440\u0430\u0432\u0438\u043b\u0430:")
    pdf._bullet("\u041b\u0435\u043a\u0430\u0440\u044f\u0442 \u0442\u0440\u044f\u0431\u0432\u0430 \u0434\u0430 \u0435 \u043b\u0438\u0447\u043d\u0438\u044f\u0442 \u043b\u0435\u043a\u0430\u0440 \u043d\u0430 \u043f\u0430\u0446\u0438\u0435\u043d\u0442\u0430 (403 NOT_PERSONAL_DOCTOR)")
    pdf._bullet("\u041d\u0430\u0447\u0430\u043b\u043e\u0442\u043e \u0442\u0440\u044f\u0431\u0432\u0430 \u0434\u0430 \u0435 \u043f\u043e\u043d\u0435 24 \u0447\u0430\u0441\u0430 \u0432 \u0431\u044a\u0434\u0435\u0449\u0435\u0442\u043e (422 TOO_SOON)")
    pdf._bullet("\u041d\u0430\u0447\u0430\u043b\u043e \u0438 \u043a\u0440\u0430\u0439 \u0442\u0440\u044f\u0431\u0432\u0430 \u0434\u0430 \u0441\u0430 \u0432 \u0435\u0434\u0438\u043d \u0438 \u0441\u044a\u0449 \u043a\u0430\u043b\u0435\u043d\u0434\u0430\u0440\u0435\u043d \u0434\u0435\u043d (422 INVALID_TIME_RANGE)")
    pdf._bullet("\u0418\u043d\u0442\u0435\u0440\u0432\u0430\u043b\u044a\u0442 \u0442\u0440\u044f\u0431\u0432\u0430 \u0434\u0430 \u043f\u043e\u043f\u0430\u0434\u0430 \u0432 \u0440\u0430\u0431\u043e\u0442\u0435\u043d \u0441\u043b\u043e\u0442 \u0431\u0435\u0437 \u043f\u043e\u0447\u0438\u0432\u043a\u0430 (422 OUTSIDE_WORKING_HOURS)")
    pdf._bullet("\u0411\u0435\u0437 \u043f\u0440\u0435\u043f\u043e\u043a\u0440\u0438\u0432\u0430\u043d\u0435 \u0441 \u0434\u0440\u0443\u0433\u0438 \u043f\u043b\u0430\u043d\u0438\u0440\u0430\u043d\u0438 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f (409 APPOINTMENT_OVERLAP)")
    pdf._bold_body("\u0417\u0430\u044f\u0432\u043a\u0430:")
    pdf._code_block(textwrap.dedent("""\
        POST /appointments
        Authorization: Bearer <patient_token>

        {
          "doctor_id": 1,
          "start_datetime": "2025-06-15T10:00:00Z",
          "end_datetime": "2025-06-15T11:00:00Z"
        }"""))
    pdf._bold_body("\u041e\u0442\u0433\u043e\u0432\u043e\u0440 (201 Created):")
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
    pdf._body("\u041e\u0442\u043c\u044f\u043d\u0430 \u043d\u0430 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0435 (\u043f\u0430\u0446\u0438\u0435\u043d\u0442 \u0438\u043b\u0438 \u043b\u0435\u043a\u0430\u0440). \u041f\u0440\u0430\u0432\u0438\u043b\u0430:")
    pdf._bullet("\u041f\u043e\u0442\u0440\u0435\u0431\u0438\u0442\u0435\u043b\u044f\u0442 \u0442\u0440\u044f\u0431\u0432\u0430 \u0434\u0430 \u0435 \u043b\u0435\u043a\u0430\u0440\u044f\u0442 \u0438\u043b\u0438 \u043f\u0430\u0446\u0438\u0435\u043d\u0442\u044a\u0442 (403 NOT_APPOINTMENT_OWNER)")
    pdf._bullet("\u041e\u0442\u043c\u044f\u043d\u0430 \u043f\u043e\u043d\u0435 12 \u0447\u0430\u0441\u0430 \u043f\u0440\u0435\u0434\u0438 \u043d\u0430\u0447\u0430\u043b\u043e\u0442\u043e (422 CANCELLATION_TOO_LATE)")
    pdf._bullet("\u041d\u0435 \u043c\u043e\u0436\u0435 \u0434\u0430 \u0441\u0435 \u043e\u0442\u043c\u0435\u043d\u0438 \u0432\u0435\u0447\u0435 \u043e\u0442\u043c\u0435\u043d\u0435\u043d\u043e \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0435 (409 ALREADY_CANCELLED)")
    pdf._body("\u0412\u0440\u044a\u0449\u0430 204 No Content \u043f\u0440\u0438 \u0443\u0441\u043f\u0435\u0445.")

    pdf._heading(3, "GET /appointments")
    pdf._body(
        "\u0421\u043f\u0438\u0441\u044a\u043a \u043d\u0430 \u0441\u043e\u0431\u0441\u0442\u0432\u0435\u043d\u0438\u0442\u0435 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f \u043d\u0430 \u0430\u0443\u0442\u0435\u043d\u0442\u0438\u043a\u0438\u0440\u0430\u043d\u0438\u044f \u043f\u043e\u0442\u0440\u0435\u0431\u0438\u0442\u0435\u043b. \u041b\u0435\u043a\u0430\u0440\u0438\u0442\u0435 \u0432\u0438\u0436\u0434\u0430\u0442 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f\u0442\u0430, "
        "\u043a\u044a\u0434\u0435\u0442\u043e \u0441\u0430 \u043b\u0435\u043a\u0430\u0440; \u043f\u0430\u0446\u0438\u0435\u043d\u0442\u0438\u0442\u0435 \u0432\u0438\u0436\u0434\u0430\u0442 \u0441\u0432\u043e\u0438\u0442\u0435."
    )
    pdf._bold_body("\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u0438:")
    pdf._bullet("skip, limit \u2014 \u043f\u0430\u0433\u0438\u043d\u0430\u0446\u0438\u044f (\u043f\u043e \u043f\u043e\u0434\u0440\u0430\u0437\u0431\u0438\u0440\u0430\u043d\u0435: 0, 20)")
    pdf._bullet("date_from, date_to \u2014 \u0444\u0438\u043b\u0442\u044a\u0440 \u043f\u043e \u043f\u0435\u0440\u0438\u043e\u0434 (ISO \u0444\u043e\u0440\u043c\u0430\u0442)")
    pdf._bullet("status \u2014 \u0444\u0438\u043b\u0442\u044a\u0440 \u043f\u043e 'scheduled' \u0438\u043b\u0438 'cancelled'")
    pdf._bold_body("\u041e\u0442\u0433\u043e\u0432\u043e\u0440 (200 OK):")
    pdf._code_block(textwrap.dedent("""\
        {
          "items": [ ... ],
          "total": 5,
          "skip": 0,
          "limit": 20
        }"""))

    # -- 1.6 Error Codes Reference
    pdf.add_page()
    pdf._heading(2, "1.6 \u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a \u043d\u0430 \u043a\u043e\u0434\u043e\u0432\u0435 \u0437\u0430 \u0433\u0440\u0435\u0448\u043a\u0438")
    pdf._body("\u0412\u0441\u0438\u0447\u043a\u0438 \u0433\u0440\u0435\u0448\u043a\u0438 \u0432\u0440\u044a\u0449\u0430\u0442 \u0435\u0434\u0438\u043d\u043d\u0430 JSON \u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430:")
    pdf._code_block(textwrap.dedent("""\
        {
          "detail": {
            "code": "ERROR_CODE",
            "message": "Human-readable description."
          }
        }"""))

    pdf._table(
        ["HTTP", "\u041a\u043e\u0434", "\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435"],
        [
            ["401", "INVALID_CREDENTIALS", "\u0413\u0440\u0435\u0448\u0435\u043d \u0438\u043c\u0435\u0439\u043b \u0438\u043b\u0438 \u043f\u0430\u0440\u043e\u043b\u0430"],
            ["401", "INVALID_TOKEN", "\u041b\u0438\u043f\u0441\u0432\u0430\u0449, \u0438\u0437\u0442\u0435\u043a\u044a\u043b \u0438\u043b\u0438 \u043d\u0435\u0432\u0430\u043b\u0438\u0434\u0435\u043d JWT"],
            ["403", "NOT_PERSONAL_DOCTOR", "\u041b\u0435\u043a\u0430\u0440\u044f\u0442 \u043d\u0435 \u0435 \u043b\u0438\u0447\u0435\u043d \u043b\u0435\u043a\u0430\u0440 \u043d\u0430 \u043f\u0430\u0446\u0438\u0435\u043d\u0442\u0430"],
            ["403", "NOT_APPOINTMENT_OWNER", "\u041f\u043e\u0442\u0440\u0435\u0431\u0438\u0442\u0435\u043b\u044f\u0442 \u043d\u0435 \u0435 \u0441\u0442\u0440\u0430\u043d\u0430 \u043f\u043e \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0435\u0442\u043e"],
            ["403", "DOCTOR_REQUIRED", "\u041a\u0440\u0430\u0439\u043d\u0430\u0442\u0430 \u0442\u043e\u0447\u043a\u0430 \u0438\u0437\u0438\u0441\u043a\u0432\u0430 \u0440\u043e\u043b\u044f \u043d\u0430 \u043b\u0435\u043a\u0430\u0440"],
            ["403", "PATIENT_REQUIRED", "\u041a\u0440\u0430\u0439\u043d\u0430\u0442\u0430 \u0442\u043e\u0447\u043a\u0430 \u0438\u0437\u0438\u0441\u043a\u0432\u0430 \u0440\u043e\u043b\u044f \u043d\u0430 \u043f\u0430\u0446\u0438\u0435\u043d\u0442"],
            ["404", "DOCTOR_NOT_FOUND", "\u041d\u044f\u043c\u0430 \u043b\u0435\u043a\u0430\u0440 \u0441 \u0442\u043e\u0432\u0430 ID"],
            ["404", "PATIENT_NOT_FOUND", "\u041d\u044f\u043c\u0430 \u043f\u0430\u0446\u0438\u0435\u043d\u0442\u0441\u043a\u0438 \u043f\u0440\u043e\u0444\u0438\u043b"],
            ["404", "APPOINTMENT_NOT_FOUND", "\u041d\u044f\u043c\u0430 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0435 \u0441 \u0442\u043e\u0432\u0430 ID"],
            ["404", "OVERRIDE_NOT_FOUND", "\u041d\u044f\u043c\u0430 \u0430\u043a\u0442\u0438\u0432\u043d\u043e \u0432\u0440\u0435\u043c\u0435\u043d\u043d\u043e \u043f\u0440\u0435\u0434\u0435\u0444\u0438\u043d\u0438\u0440\u0430\u043d\u0435"],
            ["409", "EMAIL_EXISTS", "\u0418\u043c\u0435\u0439\u043b\u044a\u0442 \u0432\u0435\u0447\u0435 \u0435 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0438\u0440\u0430\u043d"],
            ["409", "APPOINTMENT_OVERLAP", "\u0417\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0435\u0442\u043e \u0441\u0435 \u043f\u0440\u0435\u043f\u043e\u043a\u0440\u0438\u0432\u0430"],
            ["409", "OVERRIDE_EXISTS", "\u041b\u0435\u043a\u0430\u0440\u044f\u0442 \u0432\u0435\u0447\u0435 \u0438\u043c\u0430 \u043f\u0440\u0435\u0434\u0435\u0444\u0438\u043d\u0438\u0440\u0430\u043d\u0435"],
            ["409", "ALREADY_CANCELLED", "\u0417\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0435\u0442\u043e \u0432\u0435\u0447\u0435 \u0435 \u043e\u0442\u043c\u0435\u043d\u0435\u043d\u043e"],
            ["422", "TOO_SOON", "\u041f\u043e-\u043c\u0430\u043b\u043a\u043e \u043e\u0442 24\u0447 \u0434\u043e \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0435\u0442\u043e"],
            ["422", "CANCELLATION_TOO_LATE", "\u041f\u043e-\u043c\u0430\u043b\u043a\u043e \u043e\u0442 12\u0447 \u0434\u043e \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0435\u0442\u043e"],
            ["422", "OUTSIDE_WORKING_HOURS", "\u0417\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0435\u0442\u043e \u0435 \u0438\u0437\u0432\u044a\u043d \u0440\u0430\u0431. \u0432\u0440\u0435\u043c\u0435"],
            ["422", "INVALID_TIME_RANGE", "\u041a\u0440\u0430\u044f\u0442 \u0435 \u043f\u0440\u0435\u0434\u0438 \u043d\u0430\u0447\u0430\u043b\u043e\u0442\u043e \u0438\u043b\u0438 \u043f\u0440\u0435\u043c\u0438\u043d\u0430\u0432\u0430 \u0434\u0435\u043d"],
            ["422", "EFFECTIVE_DATE_TOO_SOON", "\u041f\u043e\u0441\u0442. \u043f\u0440\u043e\u043c\u044f\u043d\u0430 < 7 \u0434\u043d\u0438 \u043d\u0430\u043f\u0440\u0435\u0434"],
            ["422", "SCHEDULE_CONFLICTS_APPOINTMENT", "\u0413\u0440\u0430\u0444\u0438\u043a\u044a\u0442 \u043a\u043e\u043d\u0444\u043b\u0438\u043a\u0442\u0443\u0432\u0430 \u0441\u044a\u0441 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f"],
            ["422", "INVALID_OVERRIDE_WINDOW", "\u041a\u0440\u0430\u044f\u0442 \u043d\u0430 \u043f\u0440\u0435\u0434\u0435\u0444\u0438\u043d\u0438\u0440\u0430\u043d\u0435\u0442\u043e \u0435 \u043f\u0440\u0435\u0434\u0438 \u043d\u0430\u0447\u0430\u043b\u043e\u0442\u043e"],
        ],
        col_widths=[8, 40, 52],
    )

    pdf._heading(2, "\u041e\u0431\u043e\u0431\u0449\u0435\u043d\u0438\u0435 \u043d\u0430 HTTP \u0441\u0442\u0430\u0442\u0443\u0441 \u043a\u043e\u0434\u043e\u0432\u0435")
    pdf._table(
        ["\u041a\u043e\u0434", "\u0417\u043d\u0430\u0447\u0435\u043d\u0438\u0435", "\u0418\u0437\u043f\u043e\u043b\u0437\u0432\u0430 \u0441\u0435 \u0437\u0430"],
        [
            ["200", "OK", "\u0423\u0441\u043f\u0435\u0448\u043d\u043e GET, PUT"],
            ["201", "Created", "\u0423\u0441\u043f\u0435\u0448\u043d\u043e POST, \u0441\u044a\u0437\u0434\u0430\u0432\u0430\u0449\u043e \u0440\u0435\u0441\u0443\u0440\u0441"],
            ["204", "No Content", "\u0423\u0441\u043f\u0435\u0448\u043d\u043e DELETE"],
            ["400", "Bad Request", "\u041d\u0435\u0432\u0430\u043b\u0438\u0434\u0435\u043d JSON / \u043b\u0438\u043f\u0441\u0432\u0430\u0449\u0438 \u043f\u043e\u043b\u0435\u0442\u0430 (Pydantic)"],
            ["401", "Unauthorized", "\u041b\u0438\u043f\u0441\u0432\u0430\u0449 \u0438\u043b\u0438 \u043d\u0435\u0432\u0430\u043b\u0438\u0434\u0435\u043d JWT"],
            ["403", "Forbidden", "\u0413\u0440\u0435\u0448\u043d\u0430 \u0440\u043e\u043b\u044f \u0438\u043b\u0438 \u043d\u0435 \u0435 \u0441\u043e\u0431\u0441\u0442\u0432\u0435\u043d\u0438\u043a\u044a\u0442 \u043d\u0430 \u0440\u0435\u0441\u0443\u0440\u0441\u0430"],
            ["404", "Not Found", "\u0420\u0435\u0441\u0443\u0440\u0441\u044a\u0442 \u043d\u0435 \u0441\u044a\u0449\u0435\u0441\u0442\u0432\u0443\u0432\u0430"],
            ["409", "Conflict", "\u0414\u0443\u0431\u043b\u0438\u0440\u0430\u043d\u0435 / \u043f\u0440\u0435\u043f\u043e\u043a\u0440\u0438\u0432\u0430\u043d\u0435 / \u0432\u0435\u0447\u0435 \u0441\u044a\u0449\u0435\u0441\u0442\u0432\u0443\u0432\u0430"],
            ["422", "Unprocessable Entity", "\u041d\u0430\u0440\u0443\u0448\u0435\u043d\u043e \u0431\u0438\u0437\u043d\u0435\u0441 \u043f\u0440\u0430\u0432\u0438\u043b\u043e"],
        ],
        col_widths=[8, 22, 70],
    )

    # ═══════════════════════════════════════════════════════════════════
    # 2. ARCHITECTURE DESCRIPTION
    # ═══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf._heading(1, "2. \u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u043d\u0430 \u0430\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u0430\u0442\u0430")

    pdf._heading(2, "2.1 \u0410\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u0430 \u043d\u0430 \u0432\u0438\u0441\u043e\u043a\u043e \u043d\u0438\u0432\u043e")
    pdf._body(
        "\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435\u0442\u043e \u0441\u043b\u0435\u0434\u0432\u0430 \u0441\u043b\u043e\u0439\u043d\u0430 \u0430\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u0430 \u0441 \u044f\u0441\u043d\u043e \u0440\u0430\u0437\u0434\u0435\u043b\u0435\u043d\u0438\u0435 \u043c\u0435\u0436\u0434\u0443 "
        "HTTP \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0430, \u0431\u0438\u0437\u043d\u0435\u0441 \u043b\u043e\u0433\u0438\u043a\u0430 \u0438 \u043f\u0435\u0440\u0441\u0438\u0441\u0442\u0435\u043d\u0442\u043d\u043e\u0441\u0442 \u043d\u0430 \u0434\u0430\u043d\u043d\u0438\u0442\u0435:"
    )
    pdf._code_block(textwrap.dedent("""\
        +-------------------+
        |  HTTP Client      |
        +--------+----------+
                 |  JSON over HTTP
        +--------v----------+
        |  FastAPI Routers  |   Tonki HTTP adapteri: parsirovat
        |  (auth, doctors,  |   zayavka, vikat servis, vrashtat
        |   patients,       |   otgovor. Nyama biznes logika.
        |   schedules,      |
        |   appointments)   |
        +--------+----------+
                 |
        +--------v----------+
        |  Service Layer    |   Vsichki biznes pravila, validacii
        |  (**/service.py)  |   i orkestraciya zhiveyat tuk.
        +--------+----------+   Hvarlya AppException.
                 |
        +--------v----------+
        |  SQLAlchemy ORM   |   Deklarativni modeli definirat
        |  (**/models.py)   |   tablici, relacii i ogranich.
        +--------+----------+
                 |
        +--------v----------+
        |  SQLite (async)   |   aiosqlite drayver; Alembic
        +-------------------+   upravlyava migracii.

        Kros-sechenie:
        - Pydantic shemi (**/schemas.py) definirat API kontrakta
        - Izklycheniya (common/exceptions.py)
        - Globalni error handlers (common/error_handlers.py)
        - JWT middleware (dependencies.py + auth/security.py)"""))

    pdf._heading(2, "2.2 \u0421\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430 \u043d\u0430 \u043f\u0440\u043e\u0435\u043a\u0442\u0430")
    pdf._body(
        "\u041a\u043e\u0434\u043e\u0432\u0430\u0442\u0430 \u0431\u0430\u0437\u0430 \u0438\u0437\u043f\u043e\u043b\u0437\u0432\u0430 \u043c\u043e\u0434\u0443\u043b\u043d\u0430 \u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0446\u0438\u044f \u043f\u043e \u0444\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0430\u043b\u043d\u043e\u0441\u0442. \u0412\u0441\u044f\u043a\u0430 \u0434\u043e\u043c\u0435\u0439\u043d\u043d\u0430 \u043a\u043e\u043d\u0446\u0435\u043f\u0446\u0438\u044f "
        "(auth, doctors, patients, schedules, appointments) \u0438\u043c\u0430 \u0441\u043e\u0431\u0441\u0442\u0432\u0435\u043d \u043f\u0430\u043a\u0435\u0442 \u0441 "
        "router, service, schemas \u0438 models. \u0421\u043f\u043e\u0434\u0435\u043b\u0435\u043d\u0438\u0442\u0435 \u0443\u0442\u0438\u043b\u0438\u0442\u0438 \u0441\u0430 \u0432 common/."
    )
    pdf._code_block(textwrap.dedent("""\
        app/
        +-- main.py              App factory, lifespan, router mounting
        +-- config.py            Pydantic-settings (.env loading)
        +-- database.py          Async engine, session factory, Base
        +-- dependencies.py      get_db, get_current_user, role guards
        +-- auth/                Registraciya, login, JWT
        +-- doctors/             Spisak i detayli na lekari
        +-- patients/            Profil na pacienta
        +-- schedules/           Grafici, overrides, permanentni promeni
        +-- appointments/        Zapisvaniya: sazdavane, otmyana, spisak
        +-- common/              Izklyucheniya i error handlers"""))

    # -- 2.3 Database Schema
    pdf.add_page()
    pdf._heading(2, "2.3 \u0421\u0445\u0435\u043c\u0430 \u043d\u0430 \u0431\u0430\u0437\u0430\u0442\u0430 \u0434\u0430\u043d\u043d\u0438 (ER \u0434\u0438\u0430\u0433\u0440\u0430\u043c\u0430)")
    pdf._body(
        "\u0421\u0435\u0434\u0435\u043c \u0442\u0430\u0431\u043b\u0438\u0446\u0438 \u0441 \u0440\u0435\u0444\u0435\u0440\u0435\u043d\u0442\u043d\u0430 \u0446\u044f\u043b\u043e\u0441\u0442, \u043e\u0441\u0438\u0433\u0443\u0440\u0435\u043d\u0430 \u0447\u0440\u0435\u0437 \u0432\u044a\u043d\u0448\u043d\u0438 \u043a\u043b\u044e\u0447\u043e\u0432\u0435. "
        "SQLite PRAGMA foreign_keys=ON \u0441\u0435 \u0437\u0430\u0434\u0430\u0432\u0430 \u043f\u0440\u0438 \u0432\u0441\u044f\u043a\u0430 \u0432\u0440\u044a\u0437\u043a\u0430."
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
        | FK patient_id    |       +---------------------+
        | start_datetime   |              |
        | end_datetime     |              | 1
        | status           |    +---------v--------------+
        | cancelled_by     |    | temp_override_hours    |
        +------------------+    +------------------------+
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

    pdf._body("\u041a\u043b\u044e\u0447\u043e\u0432\u0438 \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u044f:")
    pdf._bullet("users.email \u0438\u043c\u0430 UNIQUE \u0438\u043d\u0434\u0435\u043a\u0441")
    pdf._bullet("temporary_overrides.doctor_id \u0435 UNIQUE (\u043c\u0430\u043a\u0441. 1 \u043d\u0430 \u043b\u0435\u043a\u0430\u0440)")
    pdf._bullet("working_hours \u0438\u043c\u0430 UNIQUE(doctor_id, day_of_week, start_time)")
    pdf._bullet("\u0417\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f\u0442\u0430 \u0438\u043c\u0430\u0442 \u0441\u044a\u0441\u0442\u0430\u0432\u0435\u043d \u0438\u043d\u0434\u0435\u043a\u0441 \u043d\u0430 (doctor_id, start_datetime, end_datetime)")
    pdf._bullet("CHECK \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u044f \u0437\u0430 \u0432\u0430\u043b\u0438\u0434\u043d\u0438 \u0441\u0442\u043e\u0439\u043d\u043e\u0441\u0442\u0438 \u043d\u0430 role, status \u0438 day_of_week")

    # -- 2.4 Class Diagram
    pdf.add_page()
    pdf._heading(2, "2.4 \u041a\u043b\u0430\u0441\u043e\u0432\u0430 \u0434\u0438\u0430\u0433\u0440\u0430\u043c\u0430 (UML)")
    pdf._body(
        "\u041a\u043b\u0430\u0441\u043e\u0432\u0430\u0442\u0430 \u0434\u0438\u0430\u0433\u0440\u0430\u043c\u0430 \u043f\u043e-\u0434\u043e\u043b\u0443 \u043f\u043e\u043a\u0430\u0437\u0432\u0430 \u043e\u0441\u043d\u043e\u0432\u043d\u0438\u0442\u0435 \u0434\u043e\u043c\u0435\u0439\u043d\u043d\u0438 \u043c\u043e\u0434\u0435\u043b\u0438 \u0438 \u0442\u0435\u0445\u043d\u0438\u0442\u0435 \u0432\u0440\u044a\u0437\u043a\u0438. "
        "\u0412\u0441\u0438\u0447\u043a\u0438 \u043c\u043e\u0434\u0435\u043b\u0438 \u043d\u0430\u0441\u043b\u0435\u0434\u044f\u0432\u0430\u0442 DeclarativeBase \u043d\u0430 SQLAlchemy. \u041c\u043e\u0434\u0435\u043b\u0438\u0442\u0435 \u0441 \u0432\u0440\u0435\u043c\u0435\u0432\u0438 \u043f\u0435\u0447\u0430\u0442\u0438 "
        "\u0438\u0437\u043f\u043e\u043b\u0437\u0432\u0430\u0442 TimestampMixin."
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
             |  +-----------------------+"""))

    # -- 2.5 Sequence Diagrams
    pdf.add_page()
    pdf._heading(2, "2.5 \u0414\u0438\u0430\u0433\u0440\u0430\u043c\u0438 \u043d\u0430 \u043f\u043e\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u0442\u0435\u043b\u043d\u043e\u0441\u0442\u0442\u0430")

    pdf._heading(3, "2.5.1 \u041f\u043e\u0442\u043e\u043a \u043d\u0430 \u0441\u044a\u0437\u0434\u0430\u0432\u0430\u043d\u0435 \u043d\u0430 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0435")
    pdf._code_block(textwrap.dedent("""\
        Pacient              Router             Service             DB
          |                    |                   |                 |
          |-- POST /appt ----->|                   |                 |
          |                    |-- create_appt --->|                 |
          |                    |                   |-- SELECT patient|
          |                    |                   |<-- patient row -|
          |                    |                   |                 |
          |                    |                   | [lichen lekar?]
          |                    |                   | [24ch pravilo?]
          |                    |                   | [edin den?]
          |                    |                   |                 |
          |                    |                   |-- get_effective |
          |                    |                   |   _schedule  -->|
          |                    |                   |<-- slotove -----|
          |                    |                   |                 |
          |                    |                   | [vpasva li v slot?]
          |                    |                   |                 |
          |                    |                   |-- SELECT count  |
          |                    |                   |   (overlap)  -->|
          |                    |                   |<-- count -------|
          |                    |                   |                 |
          |                    |                   | [nyama li prekritie?]
          |                    |                   |                 |
          |                    |                   |-- INSERT appt ->|
          |                    |                   |-- COMMIT ------>|
          |                    |                   |<-- appt row ----|
          |                    |<-- AppointmentResponse -------------|
          |<-- 201 Created ----|                   |                 |"""))

    pdf._heading(3, "2.5.2 \u0420\u0430\u0437\u0440\u0435\u0448\u0430\u0432\u0430\u043d\u0435 \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u043a (get_effective_schedule)")
    pdf._code_block(textwrap.dedent("""\
        Vikasht              Service                   DB
          |                    |                         |
          |-- get_effective -->|                         |
          |   (lekar, data)    |                         |
          |                    |-- apply_pending         |
          |                    |   (otdelna sesiya)  --->|
          |                    |<-- committed -----------|
          |                    |                         |
          |                    |-- SELECT temp_override  |
          |                    |   WHERE pokriva data -->|
          |                    |<-- override ili NULL ---|
          |                    |                         |
          |             [ako ima override: vrushtane na negovite slotove]
          |                    |                         |
          |                    |-- SELECT perm_change    |
          |                    |   WHERE eff_date<=data->|
          |                    |<-- promyana ili NULL ---|
          |                    |                         |
          |             [ako ima prom.: vrushtane na slotovete y]
          |                    |                         |
          |                    |-- SELECT working_hours  |
          |                    |   WHERE weekday ------->|
          |                    |<-- bazovi slotove ------|
          |                    |                         |
          |<-- list[TimeSlot] -|                         |"""))

    pdf._heading(3, "2.5.3 \u0410\u043a\u0442\u0443\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u043a \u0441 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0437\u0430 \u043a\u043e\u043d\u0444\u043b\u0438\u043a\u0442\u0438")
    pdf._code_block(textwrap.dedent("""\
        Lekar                Router             Service             DB
          |                    |                   |                 |
          |-- PUT schedule --->|                   |                 |
          |                    |-- update_wh ----->|                 |
          |                    |                   |-- DELETE old -->|
          |                    |                   |-- INSERT new -->|
          |                    |                   |-- FLUSH ------->|
          |                    |                   |                 |
          |                    |                   |-- proverka za   |
          |                    |                   |   konflikti --->|
          |                    |                   |  (za vsyako     |
          |                    |                   |   planirano     |
          |                    |                   |   zapisvane:    |
          |                    |                   |   vpasva li?)   |
          |                    |                   |                 |
          |              [ako konflikt: ROLLBACK, hvurlyane 422]
          |              [ako OK: COMMIT]
          |                    |                   |                 |
          |<-- 200 OK ---------|                   |                 |"""))

    # ═══════════════════════════════════════════════════════════════════
    # 3. SELF-ANALYSIS
    # ═══════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf._heading(1, "3. \u0421\u0430\u043c\u043e\u0430\u043d\u0430\u043b\u0438\u0437")

    pdf._heading(2, "3.1 \u0421\u043f\u0430\u0437\u0432\u0430\u043d\u0435 \u043d\u0430 SOLID \u043f\u0440\u0438\u043d\u0446\u0438\u043f\u0438\u0442\u0435")

    pdf._heading(3, "\u041f\u0440\u0438\u043d\u0446\u0438\u043f \u043d\u0430 \u0435\u0434\u0438\u043d\u0441\u0442\u0432\u0435\u043d\u0430\u0442\u0430 \u043e\u0442\u0433\u043e\u0432\u043e\u0440\u043d\u043e\u0441\u0442 (SRP)")
    pdf._body(
        "\u0412\u0441\u0435\u043a\u0438 \u043c\u043e\u0434\u0443\u043b \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u0432\u0430 \u0442\u043e\u0447\u043d\u043e \u0435\u0434\u043d\u0430 \u0434\u043e\u043c\u0435\u0439\u043d\u043d\u0430 \u043a\u043e\u043d\u0446\u0435\u043f\u0446\u0438\u044f. \u0412 \u0440\u0430\u043c\u043a\u0438\u0442\u0435 \u043d\u0430 \u043c\u043e\u0434\u0443\u043b\u0430 "
        "\u043e\u0442\u0433\u043e\u0432\u043e\u0440\u043d\u043e\u0441\u0442\u0438\u0442\u0435 \u0441\u0430 \u0434\u043e\u043f\u044a\u043b\u043d\u0438\u0442\u0435\u043b\u043d\u043e \u0440\u0430\u0437\u0434\u0435\u043b\u0435\u043d\u0438:"
    )
    pdf._bullet("Router-\u0438\u0442\u0435 \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u0432\u0430\u0442 \u0441\u0430\u043c\u043e HTTP \u043f\u0430\u0440\u0441\u0432\u0430\u043d\u0435 \u0438 \u0444\u043e\u0440\u043c\u0430\u0442\u0438\u0440\u0430\u043d\u0435 \u043d\u0430 \u043e\u0442\u0433\u043e\u0432\u043e\u0440\u0438\u0442\u0435.")
    pdf._bullet("Service-\u0438\u0442\u0435 \u0441\u044a\u0434\u044a\u0440\u0436\u0430\u0442 \u0446\u044f\u043b\u0430\u0442\u0430 \u0431\u0438\u0437\u043d\u0435\u0441 \u043b\u043e\u0433\u0438\u043a\u0430, \u0432\u0430\u043b\u0438\u0434\u0430\u0446\u0438\u0438 \u0438 \u043e\u0440\u043a\u0435\u0441\u0442\u0440\u0430\u0446\u0438\u044f.")
    pdf._bullet("\u041c\u043e\u0434\u0435\u043b\u0438\u0442\u0435 \u0434\u0435\u0444\u0438\u043d\u0438\u0440\u0430\u0442 \u043f\u0435\u0440\u0441\u0438\u0441\u0442\u0435\u043d\u0442\u043d\u0430\u0442\u0430 \u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430 \u0438 \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u044f\u0442\u0430 \u0432 \u0431\u0430\u0437\u0430\u0442\u0430.")
    pdf._bullet("\u0421\u0445\u0435\u043c\u0438\u0442\u0435 \u0434\u0435\u0444\u0438\u043d\u0438\u0440\u0430\u0442 API \u043a\u043e\u043d\u0442\u0440\u0430\u043a\u0442\u0430 (\u0432\u0430\u043b\u0438\u0434\u0430\u0446\u0438\u044f \u043d\u0430 \u0437\u0430\u044f\u0432\u043a\u0438, \u0444\u043e\u0440\u043c\u0430 \u043d\u0430 \u043e\u0442\u0433\u043e\u0432\u043e\u0440\u0438).")
    pdf._bullet(
        "\u041f\u0430\u043a\u0435\u0442\u044a\u0442 common/ \u0446\u0435\u043d\u0442\u0440\u0430\u043b\u0438\u0437\u0438\u0440\u0430 \u043a\u0440\u043e\u0441-\u0441\u0435\u0447\u0435\u043d\u0438\u044f\u0442\u0430: \u043a\u043b\u0430\u0441\u043e\u0432\u0435 \u0437\u0430 \u0438\u0437\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u044f "
        "\u0432 exceptions.py \u0438 \u0433\u043b\u043e\u0431\u0430\u043b\u043d\u0438 \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u0446\u0438 \u043d\u0430 \u0433\u0440\u0435\u0448\u043a\u0438 \u0432 error_handlers.py."
    )
    pdf._body(
        "\u041f\u0440\u0438\u043c\u0435\u0440: appointments/service.py \u043f\u0440\u0438\u0442\u0435\u0436\u0430\u0432\u0430 \u0432\u0441\u0438\u0447\u043a\u0438 \u043f\u0440\u0430\u0432\u0438\u043b\u0430 \u0437\u0430 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f (24\u0447, \u043f\u0440\u0435\u043f\u043e\u043a\u0440\u0438\u0432\u0430\u043d\u0435, \u0440\u0430\u0431. \u0432\u0440\u0435\u043c\u0435). "
        "Router-\u044a\u0442 \u043d\u0438\u043a\u043e\u0433\u0430 \u043d\u0435 \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0432\u0430 \u0431\u0438\u0437\u043d\u0435\u0441 \u043f\u0440\u0430\u0432\u0438\u043b\u0430; \u0434\u0435\u043b\u0435\u0433\u0438\u0440\u0430 \u0438\u0437\u0446\u044f\u043b\u043e \u043d\u0430 service-\u0430."
    )

    pdf._heading(3, "\u041f\u0440\u0438\u043d\u0446\u0438\u043f \u043e\u0442\u0432\u043e\u0440\u0435\u043d\u043e\u0441\u0442/\u0437\u0430\u0442\u0432\u043e\u0440\u0435\u043d\u043e\u0441\u0442 (OCP)")
    pdf._body(
        "\u0421\u0438\u0441\u0442\u0435\u043c\u0430\u0442\u0430 \u0437\u0430 \u0440\u0430\u0437\u0440\u0435\u0448\u0430\u0432\u0430\u043d\u0435 \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u0446\u0438 \u0434\u0435\u043c\u043e\u043d\u0441\u0442\u0440\u0438\u0440\u0430 OCP. get_effective_schedule() \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0432\u0430 "
        "\u0442\u0440\u0438 \u0441\u043b\u043e\u044f \u043f\u043e \u043f\u0440\u0438\u043e\u0440\u0438\u0442\u0435\u0442 (\u0432\u0440\u0435\u043c\u0435\u043d\u043d\u043e \u043f\u0440\u0435\u0434\u0435\u0444\u0438\u043d\u0438\u0440\u0430\u043d\u0435 > \u043f\u043e\u0441\u0442\u043e\u044f\u043d\u043d\u0430 \u043f\u0440\u043e\u043c\u044f\u043d\u0430 > "
        "\u0431\u0430\u0437\u043e\u0432\u043e \u0440\u0430\u0431\u043e\u0442\u043d\u043e \u0432\u0440\u0435\u043c\u0435). \u0414\u043e\u0431\u0430\u0432\u044f\u043d\u0435\u0442\u043e \u043d\u0430 \u043d\u043e\u0432 \u0441\u043b\u043e\u0439 (\u043d\u0430\u043f\u0440. \u043a\u0430\u043b\u0435\u043d\u0434\u0430\u0440 \u0437\u0430 \u043f\u0440\u0430\u0437\u043d\u0438\u0446\u0438) "
        "\u0438\u0437\u0438\u0441\u043a\u0432\u0430 \u0441\u0430\u043c\u043e \u043d\u043e\u0432 \u043c\u043e\u0434\u0435\u043b \u0438 \u043e\u0449\u0435 \u0435\u0434\u043d\u0430 \u0441\u0442\u044a\u043f\u043a\u0430 \u043d\u0430 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430, \u0431\u0435\u0437 \u043f\u0440\u043e\u043c\u044f\u043d\u0430 \u043d\u0430 \u0441\u044a\u0449\u0435\u0441\u0442\u0432\u0443\u0432\u0430\u0449\u0430\u0442\u0430 \u043b\u043e\u0433\u0438\u043a\u0430."
    )
    pdf._body(
        "\u0419\u0435\u0440\u0430\u0440\u0445\u0438\u044f\u0442\u0430 \u043d\u0430 \u0438\u0437\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u044f (AppException -> BusinessRuleException, ConflictException \u0438 \u0434\u0440.) "
        "\u0441\u044a\u0449\u043e \u0435 \u043e\u0442\u0432\u043e\u0440\u0435\u043d\u0430 \u0437\u0430 \u0440\u0430\u0437\u0448\u0438\u0440\u0435\u043d\u0438\u0435. \u041d\u043e\u0432\u0438 \u0442\u0438\u043f\u043e\u0432\u0435 \u0433\u0440\u0435\u0448\u043a\u0438 \u043c\u043e\u0433\u0430\u0442 \u0434\u0430 \u0441\u0435 \u0434\u043e\u0431\u0430\u0432\u044f\u0442 \u0431\u0435\u0437 \u043f\u0440\u043e\u043c\u044f\u043d\u0430 "
        "\u043d\u0430 \u0433\u043b\u043e\u0431\u0430\u043b\u043d\u0438\u044f error handler, \u043a\u043e\u0439\u0442\u043e \u0445\u0432\u0430\u0449\u0430 \u0431\u0430\u0437\u043e\u0432\u0438\u044f AppException \u043a\u043b\u0430\u0441."
    )

    pdf._heading(3, "\u041f\u0440\u0438\u043d\u0446\u0438\u043f \u043d\u0430 \u0437\u0430\u043c\u0435\u0441\u0442\u0432\u0430\u043d\u0435\u0442\u043e \u043d\u0430 \u041b\u0438\u0441\u043a\u043e\u0432 (LSP)")
    pdf._body(
        "Doctor \u0438 Patient \u0441\u0430 \u0441\u0432\u044a\u0440\u0437\u0430\u043d\u0438 \u043a\u044a\u043c User \u0447\u0440\u0435\u0437 1:1 \u0432\u044a\u043d\u0448\u0435\u043d \u043a\u043b\u044e\u0447. \u0412\u0441\u0435\u043a\u0438 \u043a\u043e\u0434, \u043a\u043e\u0439\u0442\u043e \u0440\u0430\u0431\u043e\u0442\u0438 \u0441 "
        "User (\u0430\u0443\u0442\u0435\u043d\u0442\u0438\u043a\u0430\u0446\u0438\u044f, \u0441\u044a\u0437\u0434\u0430\u0432\u0430\u043d\u0435 \u043d\u0430 \u0442\u043e\u043a\u0435\u043d, get_current_user), \u0440\u0430\u0431\u043e\u0442\u0438 \u0435\u0434\u043d\u0430\u043a\u0432\u043e "
        "\u043d\u0435\u0437\u0430\u0432\u0438\u0441\u0438\u043c\u043e \u0434\u0430\u043b\u0438 \u043f\u043e\u0442\u0440\u0435\u0431\u0438\u0442\u0435\u043b\u044f\u0442 \u0435 \u043b\u0435\u043a\u0430\u0440 \u0438\u043b\u0438 \u043f\u0430\u0446\u0438\u0435\u043d\u0442. \u041f\u043e\u043b\u0435\u0442\u043e role \u0441\u0435 \u0438\u0437\u043f\u043e\u043b\u0437\u0432\u0430 \u0441\u0430\u043c\u043e \u0437\u0430 "
        "\u0430\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u043e\u043d\u043d\u0438 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438, \u043d\u043e \u0441\u0430\u043c\u0438\u044f\u0442 \u043f\u043e\u0442\u043e\u043a \u043d\u0430 \u0430\u0443\u0442\u0435\u043d\u0442\u0438\u043a\u0430\u0446\u0438\u044f \u0435 \u043d\u0430\u043f\u044a\u043b\u043d\u043e \u0437\u0430\u043c\u0435\u0441\u0442\u0438\u043c."
    )

    pdf._heading(3, "\u041f\u0440\u0438\u043d\u0446\u0438\u043f \u043d\u0430 \u0440\u0430\u0437\u0434\u0435\u043b\u044f\u043d\u0435 \u043d\u0430 \u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441\u0438\u0442\u0435 (ISP)")
    pdf._body(
        "Pydantic \u0441\u0445\u0435\u043c\u0438\u0442\u0435 \u0441\u0430 \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438 \u043f\u043e \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u044f. DoctorRegisterRequest, PatientRegisterRequest, "
        "LoginRequest \u0438 TokenResponse \u0441\u0430 \u0432\u0441\u0438\u0447\u043a\u0438 \u043e\u0442\u0434\u0435\u043b\u043d\u0438 \u043c\u043e\u0434\u0435\u043b\u0438. \u041c\u043e\u0434\u0443\u043b\u044a\u0442 \u0437\u0430 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f \u0438\u043c\u0430 "
        "\u043e\u0442\u0434\u0435\u043b\u043d\u0438 AppointmentCreateRequest, AppointmentResponse \u0438 AppointmentListFilters. "
        "\u041d\u0438\u043a\u043e\u0439 \u043a\u043b\u0438\u0435\u043d\u0442 \u043d\u0435 \u0435 \u043f\u0440\u0438\u043d\u0443\u0434\u0435\u043d \u0434\u0430 \u0440\u0430\u0431\u043e\u0442\u0438 \u0441 \u043f\u043e\u043b\u0435\u0442\u0430, \u043d\u0435\u0440\u0435\u043b\u0435\u0432\u0430\u043d\u0442\u043d\u0438 \u0437\u0430 \u043d\u0435\u0433\u043e\u0432\u0430\u0442\u0430 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u044f."
    )
    pdf._body(
        "\u0417\u0430\u0432\u0438\u0441\u0438\u043c\u043e\u0441\u0442\u0438\u0442\u0435 \u043d\u0430 FastAPI (get_current_user, require_doctor, require_patient) \u0441\u0430 \u0444\u0438\u043d\u043e "
        "\u0433\u0440\u0430\u043d\u0443\u043b\u0438\u0440\u0430\u043d\u0438. \u041a\u0440\u0430\u0439\u043d\u0438\u0442\u0435 \u0442\u043e\u0447\u043a\u0438 \u0434\u0435\u043a\u043b\u0430\u0440\u0438\u0440\u0430\u0442 \u0442\u043e\u0447\u043d\u043e \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e\u0442\u043e \u043d\u0438\u0432\u043e \u043d\u0430 \u0430\u0443\u0442\u0435\u043d\u0442\u0438\u043a\u0430\u0446\u0438\u044f."
    )

    pdf._heading(3, "\u041f\u0440\u0438\u043d\u0446\u0438\u043f \u043d\u0430 \u0438\u043d\u0432\u0435\u0440\u0441\u0438\u044f \u043d\u0430 \u0437\u0430\u0432\u0438\u0441\u0438\u043c\u043e\u0441\u0442\u0438\u0442\u0435 (DIP)")
    pdf._body(
        "Service-\u0438\u0442\u0435 \u0437\u0430\u0432\u0438\u0441\u044f\u0442 \u043e\u0442 \u0430\u0431\u0441\u0442\u0440\u0430\u043a\u0446\u0438\u044f\u0442\u0430 AsyncSession, \u043d\u0438\u043a\u043e\u0433\u0430 \u043e\u0442 \u043a\u043e\u043d\u043a\u0440\u0435\u0442\u043d\u0438 \u0434\u0435\u0442\u0430\u0439\u043b\u0438 \u043d\u0430 engine. "
        "\u0422\u043e\u0432\u0430 \u0441\u0435 \u0434\u0435\u043c\u043e\u043d\u0441\u0442\u0440\u0438\u0440\u0430 \u043e\u0442 \u0442\u0435\u0441\u0442\u043e\u0432\u0435\u0442\u0435, \u043a\u043e\u0438\u0442\u043e \u0437\u0430\u043c\u0435\u043d\u044f\u0442 \u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u0435\u043d\u0430\u0442\u0430 SQLite \u0431\u0430\u0437\u0430 "
        "\u0441 \u0431\u0430\u0437\u0430 \u0432 \u043f\u0430\u043c\u0435\u0442\u0442\u0430 \u0447\u0440\u0435\u0437 \u043f\u0440\u0435\u0434\u0435\u0444\u0438\u043d\u0438\u0440\u0430\u043d\u0435 \u043d\u0430 get_db \u0437\u0430\u0432\u0438\u0441\u0438\u043c\u043e\u0441\u0442\u0442\u0430. "
        "\u041d\u0435 \u0441\u0430 \u043d\u0443\u0436\u043d\u0438 \u043f\u0440\u043e\u043c\u0435\u043d\u0438 \u0432 \u043a\u043e\u0434\u0430 \u043d\u0430 service-\u0438\u0442\u0435."
    )
    pdf._body(
        "\u041f\u0430\u0442\u044a\u0440\u043d\u044a\u0442 \u0437\u0430 dependency injection \u0447\u0440\u0435\u0437 Depends() \u043c\u0435\u0445\u0430\u043d\u0438\u0437\u043c\u0430 \u043d\u0430 FastAPI "
        "\u0440\u0430\u0437\u0434\u0435\u043b\u044f \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0430\u0442\u0430 \u043d\u0430 \u0437\u0430\u044f\u0432\u043a\u0438 \u043e\u0442 \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435\u0442\u043e \u043d\u0430 DB \u0441\u0435\u0441\u0438\u0438 \u0438 \u0430\u0443\u0442\u0435\u043d\u0442\u0438\u043a\u0430\u0446\u0438\u044f\u0442\u0430."
    )

    # -- 3.2 Design Trade-offs
    pdf._heading(2, "3.2 \u041f\u0440\u043e\u0435\u043a\u0442\u043d\u0438 \u043a\u043e\u043c\u043f\u0440\u043e\u043c\u0438\u0441\u0438")

    pdf._heading(3, "SQLite \u0441\u0440\u0435\u0449\u0443 PostgreSQL")
    pdf._body(
        "SQLite \u0435 \u0438\u0437\u0431\u0440\u0430\u043d \u0437\u0430\u0440\u0430\u0434\u0438 \u043f\u0440\u043e\u0441\u0442\u043e\u0442\u0430\u0442\u0430 (\u043d\u0443\u043b\u0435\u0432\u0430 \u043a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u044f, \u0444\u0430\u0439\u043b\u043e\u0432\u043e \u0431\u0430\u0437\u0438\u0440\u0430\u043d). "
        "\u0422\u043e\u0432\u0430 \u043e\u0442\u0433\u043e\u0432\u0430\u0440\u044f \u043d\u0430 \u043e\u0431\u0445\u0432\u0430\u0442\u0430 \u043d\u0430 \u043f\u0440\u043e\u0435\u043a\u0442\u0430, \u043d\u043e \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0430\u0432\u0430 \u0435\u0434\u043d\u043e\u0432\u0440\u0435\u043c\u0435\u043d\u043d\u0438\u044f \u0437\u0430\u043f\u0438\u0441 \u0438 \u043d\u0430\u043f\u0440\u0435\u0434\u043d\u0430\u043b\u0438\u0442\u0435 "
        "\u0444\u0443\u043d\u043a\u0446\u0438\u0438. \u0410\u0441\u0438\u043d\u0445\u0440\u043e\u043d\u043d\u0438\u044f\u0442 \u0434\u0440\u0430\u0439\u0432\u0435\u0440 (aiosqlite) \u043e\u0431\u0432\u0438\u0432\u0430 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u043d\u0438\u044f SQLite \u0432 thread pool. "
        "\u041c\u0438\u0433\u0440\u0430\u0446\u0438\u044f \u043a\u044a\u043c PostgreSQL \u0438\u0437\u0438\u0441\u043a\u0432\u0430 \u0441\u0430\u043c\u043e \u043f\u0440\u043e\u043c\u044f\u043d\u0430 \u043d\u0430 DATABASE_URL \u0438 \u0438\u043d\u0441\u0442\u0430\u043b\u0438\u0440\u0430\u043d\u0435 \u043d\u0430 asyncpg; "
        "\u0432\u0441\u0438\u0447\u043a\u0438 \u0437\u0430\u044f\u0432\u043a\u0438 \u0438\u0437\u043f\u043e\u043b\u0437\u0432\u0430\u0442 ORM \u0438 \u0441\u0430 \u043d\u0435\u0437\u0430\u0432\u0438\u0441\u0438\u043c\u0438 \u043e\u0442 \u0431\u0430\u0437\u0430\u0442\u0430."
    )

    pdf._heading(3, "\u041d\u0435\u0437\u0430\u0431\u0430\u0432\u043d\u043e \u043f\u0440\u043e\u043c\u043e\u0442\u0438\u0440\u0430\u043d\u0435 \u043d\u0430 \u043f\u043e\u0441\u0442\u043e\u044f\u043d\u043d\u0438 \u043f\u0440\u043e\u043c\u0435\u043d\u0438")
    pdf._body(
        "\u041f\u043e\u0441\u0442\u043e\u044f\u043d\u043d\u0438\u0442\u0435 \u043f\u0440\u043e\u043c\u0435\u043d\u0438 \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u043a\u0430 \u0441\u0435 \u043f\u0440\u043e\u043c\u043e\u0442\u0438\u0440\u0430\u0442 \u043a\u044a\u043c working_hours \u043f\u0440\u0438 \u0441\u0442\u0430\u0440\u0442\u0438\u0440\u0430\u043d\u0435 (lifespan) "
        "\u0438 \u043f\u0440\u0435\u0434\u0438 \u0432\u0441\u044f\u043a\u043e \u0438\u0437\u0432\u0438\u043a\u0432\u0430\u043d\u0435 \u043d\u0430 get_effective_schedule(). \u0422\u043e\u0432\u0430 \u0435 \u043f\u0440\u043e\u0441\u0442\u043e \u0438 \u043a\u043e\u0440\u0435\u043a\u0442\u043d\u043e, "
        "\u043d\u043e \u0438\u0437\u043f\u044a\u043b\u043d\u044f\u0432\u0430 \u0433\u043b\u043e\u0431\u0430\u043b\u043d\u043e \u0441\u043a\u0430\u043d\u0438\u0440\u0430\u043d\u0435 \u043d\u0430 \u0432\u0441\u0438\u0447\u043a\u0438 \u043d\u0435\u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438 \u043f\u0440\u043e\u043c\u0435\u043d\u0438 \u043f\u0440\u0438 \u0432\u0441\u044f\u043a\u043e \u0447\u0435\u0442\u0435\u043d\u0435 \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u043a. "
        "\u0417\u0430 \u043f\u0440\u043e\u0435\u043a\u0442 \u0432 \u0442\u043e\u0437\u0438 \u043c\u0430\u0449\u0430\u0431 \u0442\u043e\u0432\u0430 \u0435 \u043d\u0435\u0437\u043d\u0430\u0447\u0438\u0442\u0435\u043b\u043d\u043e; \u043f\u0440\u0438 \u043c\u0430\u0449\u0430\u0431\u0438\u0440\u0430\u043d\u0435 \u0431\u0438 \u0431\u0438\u043b \u043f\u043e-\u043f\u043e\u0434\u0445\u043e\u0434\u044f\u0449 "
        "\u0444\u043e\u043d\u043e\u0432 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0447\u0438\u043a (Celery beat, APScheduler \u0438\u043b\u0438 cron)."
    )

    pdf._heading(3, "\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0437\u0430 \u043a\u043e\u043d\u0444\u043b\u0438\u043a\u0442\u0438 \u043f\u0440\u0438 \u043f\u0440\u043e\u043c\u044f\u043d\u0430 \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u043a\u0430")
    pdf._body(
        "\u041a\u043e\u0433\u0430\u0442\u043e \u043b\u0435\u043a\u0430\u0440 \u0430\u043a\u0442\u0443\u0430\u043b\u0438\u0437\u0438\u0440\u0430 \u0433\u0440\u0430\u0444\u0438\u043a\u0430 \u0441\u0438, \u0441\u0438\u0441\u0442\u0435\u043c\u0430\u0442\u0430 \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0432\u0430 \u0432\u0441\u0438\u0447\u043a\u0438 \u043f\u043b\u0430\u043d\u0438\u0440\u0430\u043d\u0438 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f "
        "\u0441\u043f\u0440\u044f\u043c\u043e \u043d\u043e\u0432\u0438\u0442\u0435 \u0435\u0444\u0435\u043a\u0442\u0438\u0432\u043d\u0438 \u0447\u0430\u0441\u043e\u0432\u0435 \u0438 \u043e\u0442\u0445\u0432\u044a\u0440\u043b\u044f \u043f\u0440\u043e\u043c\u044f\u043d\u0430\u0442\u0430 \u0430\u043a\u043e \u043d\u044f\u043a\u043e\u0435 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0435 \u0431\u0438 \u043e\u0441\u0442\u0430\u043d\u0430\u043b\u043e \u0431\u0435\u0437 \u043f\u043e\u043a\u0440\u0438\u0442\u0438\u0435. "
        "\u0410\u043b\u0442\u0435\u0440\u043d\u0430\u0442\u0438\u0432\u0435\u043d \u043f\u043e\u0434\u0445\u043e\u0434 \u0431\u0438 \u0431\u0438\u043b \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u043d\u0430 \u043e\u0442\u043c\u044f\u043d\u0430 \u043d\u0430 \u043a\u043e\u043d\u0444\u043b\u0438\u043a\u0442\u0443\u0432\u0430\u0449\u0438\u0442\u0435 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f, "
        "\u043d\u043e \u043f\u043e\u0434\u0445\u043e\u0434\u044a\u0442 \u0441 \u043e\u0442\u0445\u0432\u044a\u0440\u043b\u044f\u043d\u0435 (422) \u0435 \u0438\u0437\u0431\u0440\u0430\u043d \u0437\u0430 \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442: \u043d\u0438\u043a\u043e\u0439 \u043f\u0430\u0446\u0438\u0435\u043d\u0442 \u043d\u0435 \u0433\u0443\u0431\u0438 "
        "\u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0435 \u0431\u0435\u0437 \u044f\u0432\u043d\u043e \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435."
    )

    pdf._heading(3, "JWT \u0431\u0435\u0437 refresh \u0442\u043e\u043a\u0435\u043d\u0438")
    pdf._body(
        "\u0422\u0435\u043a\u0443\u0449\u0430\u0442\u0430 \u0441\u0438\u0441\u0442\u0435\u043c\u0430 \u0437\u0430 \u0430\u0443\u0442\u0435\u043d\u0442\u0438\u043a\u0430\u0446\u0438\u044f \u0438\u0437\u0434\u0430\u0432\u0430 \u0435\u0434\u0438\u043d access token \u0441 60-\u043c\u0438\u043d\u0443\u0442\u0435\u043d \u0441\u0440\u043e\u043a. "
        "\u041d\u044f\u043c\u0430 refresh token \u043f\u043e\u0442\u043e\u043a. \u0422\u043e\u0432\u0430 \u043e\u043f\u0440\u043e\u0441\u0442\u044f\u0432\u0430 \u0438\u043c\u043f\u043b\u0435\u043c\u0435\u043d\u0442\u0430\u0446\u0438\u044f\u0442\u0430, \u043d\u043e \u043e\u0437\u043d\u0430\u0447\u0430\u0432\u0430, \u0447\u0435 "
        "\u043a\u043b\u0438\u0435\u043d\u0442\u0438\u0442\u0435 \u0442\u0440\u044f\u0431\u0432\u0430 \u0434\u0430 \u0441\u0435 \u0430\u0443\u0442\u0435\u043d\u0442\u0438\u043a\u0438\u0440\u0430\u0442 \u043e\u0442\u043d\u043e\u0432\u043e \u0441\u043b\u0435\u0434 \u0438\u0437\u0442\u0438\u0447\u0430\u043d\u0435. \u0414\u043e\u0431\u0430\u0432\u044f\u043d\u0435\u0442\u043e \u043d\u0430 refresh \u0442\u043e\u043a\u0435\u043d\u0438 "
        "\u0431\u0438 \u0431\u0438\u043b\u043e \u0435\u0441\u0442\u0435\u0441\u0442\u0432\u0435\u043d\u043e \u043f\u043e\u0434\u043e\u0431\u0440\u0435\u043d\u0438\u0435 \u0437\u0430 \u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u0435\u043d\u0430 \u0443\u043f\u043e\u0442\u0440\u0435\u0431\u0430."
    )

    # -- 3.3 Areas for Improvement
    pdf._heading(2, "3.3 \u041e\u0431\u043b\u0430\u0441\u0442\u0438 \u0437\u0430 \u043f\u043e\u0434\u043e\u0431\u0440\u0435\u043d\u0438\u0435")

    pdf._bullet(
        "\u041f\u0430\u0433\u0438\u043d\u0430\u0446\u0438\u044f: \u0418\u0437\u043f\u043e\u043b\u0437\u0432\u0430\u043d\u0435 \u043d\u0430 cursor-based \u043f\u0430\u0433\u0438\u043d\u0430\u0446\u0438\u044f \u0432\u043c\u0435\u0441\u0442\u043e offset/limit "
        "\u0437\u0430 \u043f\u043e-\u0434\u043e\u0431\u0440\u0430 \u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u043d\u043e\u0441\u0442 \u043f\u0440\u0438 \u0433\u043e\u043b\u0435\u043c\u0438 \u043d\u0430\u0431\u043e\u0440\u0438 \u043e\u0442 \u0434\u0430\u043d\u043d\u0438."
    )
    pdf._bullet(
        "Rate limiting: \u041d\u044f\u043c\u0430 \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u0435 \u043d\u0430 \u0447\u0435\u0441\u0442\u043e\u0442\u0430\u0442\u0430 \u043d\u0430 \u0437\u0430\u044f\u0432\u043a\u0438\u0442\u0435. \u041f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u0435\u043d\u0438 \u0434\u0435\u043f\u043b\u043e\u0439\u043c\u0435\u043d\u0442\u0438 "
        "\u0442\u0440\u044f\u0431\u0432\u0430 \u0434\u0430 \u0434\u043e\u0431\u0430\u0432\u044f\u0442 middleware \u0438\u043b\u0438 throttling \u043d\u0430 \u043d\u0438\u0432\u043e reverse proxy."
    )
    pdf._bullet(
        "Refresh \u0442\u043e\u043a\u0435\u043d\u0438: \u0418\u043c\u043f\u043b\u0435\u043c\u0435\u043d\u0442\u0438\u0440\u0430\u043d\u0435 \u043d\u0430 \u043f\u043e\u0442\u043e\u043a \u0437\u0430 \u043e\u043f\u0440\u0435\u0441\u043d\u044f\u0432\u0430\u043d\u0435 \u043d\u0430 \u0442\u043e\u043a\u0435\u043d\u0438 "
        "\u0437\u0430 \u043f\u043e-\u0434\u043e\u0431\u0440\u043e \u043f\u043e\u0442\u0440\u0435\u0431\u0438\u0442\u0435\u043b\u0441\u043a\u043e \u0438\u0437\u0436\u0438\u0432\u044f\u0432\u0430\u043d\u0435."
    )
    pdf._bullet(
        "\u0418\u043c\u0435\u0439\u043b \u0438\u0437\u0432\u0435\u0441\u0442\u0438\u044f: \u0423\u0432\u0435\u0434\u043e\u043c\u044f\u0432\u0430\u043d\u0435 \u043d\u0430 \u043f\u0430\u0446\u0438\u0435\u043d\u0442\u0438 \u0438 \u043b\u0435\u043a\u0430\u0440\u0438 \u043f\u0440\u0438 \u0441\u044a\u0437\u0434\u0430\u0432\u0430\u043d\u0435, "
        "\u043e\u0442\u043c\u044f\u043d\u0430 \u0438 \u043f\u0440\u043e\u043c\u044f\u043d\u0430 \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u043a."
    )
    pdf._bullet(
        "\u0410\u0434\u043c\u0438\u043d \u043a\u0440\u0430\u0439\u043d\u0438 \u0442\u043e\u0447\u043a\u0438: \u041d\u044f\u043c\u0430 \u0430\u0434\u043c\u0438\u043d \u0440\u043e\u043b\u044f. \u0414\u043e\u0431\u0430\u0432\u044f\u043d\u0435\u0442\u043e \u0439 \u0431\u0438 \u043f\u043e\u0437\u0432\u043e\u043b\u0438\u043b\u043e "
        "\u0446\u0435\u043d\u0442\u0440\u0430\u043b\u0438\u0437\u0438\u0440\u0430\u043d\u043e \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435."
    )
    pdf._bullet(
        "Soft-delete \u0438 \u043e\u0434\u0438\u0442\u0435\u043d \u0441\u043b\u0435\u0434: \u041e\u0442\u043c\u0435\u043d\u0435\u043d\u0438\u0442\u0435 \u0437\u0430\u043f\u0438\u0441\u0432\u0430\u043d\u0438\u044f \u0438\u0437\u043f\u043e\u043b\u0437\u0432\u0430\u0442 \u0444\u043b\u0430\u0433 \u0437\u0430 \u0441\u0442\u0430\u0442\u0443\u0441, "
        "\u043d\u043e \u0434\u0440\u0443\u0433\u0438\u0442\u0435 \u0435\u043d\u0442\u0438\u0442\u0435\u0442\u0438 \u0441\u0435 \u0438\u0437\u0442\u0440\u0438\u0432\u0430\u0442 \u043d\u0430\u043f\u044a\u043b\u043d\u043e. \u041e\u0434\u0438\u0442\u0435\u043d \u043b\u043e\u0433 \u0431\u0438 \u043f\u043e\u0434\u043e\u0431\u0440\u0438\u043b \u043f\u0440\u043e\u0441\u043b\u0435\u0434\u0438\u043c\u043e\u0441\u0442\u0442\u0430."
    )
    pdf._bullet(
        "\u0427\u0430\u0441\u043e\u0432\u0438 \u0437\u043e\u043d\u0438: \u0412\u0441\u0438\u0447\u043a\u0438 \u0434\u0430\u0442\u0438 \u0441\u0435 \u0441\u044a\u0445\u0440\u0430\u043d\u044f\u0432\u0430\u0442 \u0432 UTC. "
        "\u041a\u043e\u043d\u0432\u0435\u0440\u0442\u0438\u0440\u0430\u043d\u0435\u0442\u043e \u0441\u0435 \u043e\u0441\u0442\u0430\u0432\u044f \u043d\u0430 \u043a\u043b\u0438\u0435\u043d\u0442\u0430. \u042f\u0432\u043d\u043e timezone-aware API "
        "\u0431\u0438 \u043f\u043e\u0434\u043e\u0431\u0440\u0438\u043b\u043e \u0443\u043f\u043e\u0442\u0440\u0435\u0431\u0438\u043c\u043e\u0441\u0442\u0442\u0430."
    )
    pdf._bullet(
        "\u0424\u043e\u043d\u043e\u0432\u0430 \u0437\u0430\u0434\u0430\u0447\u0430 \u0437\u0430 \u043f\u0440\u043e\u043c\u043e\u0446\u0438\u0438: \u0417\u0430\u043c\u044f\u043d\u0430 \u043d\u0430 on-demand "
        "apply_pending_permanent_changes \u0441 \u0444\u043e\u043d\u043e\u0432 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0447\u0438\u043a."
    )
    pdf._bullet(
        "Docker health checks: Dockerfile \u0438 docker-compose.yml \u043d\u044f\u043c\u0430\u0442 "
        "HEALTHCHECK \u0434\u0438\u0440\u0435\u043a\u0442\u0438\u0432\u0430."
    )
    pdf._bullet(
        "API \u0432\u0435\u0440\u0441\u0438\u043e\u043d\u0438\u0440\u0430\u043d\u0435: \u0412\u0441\u0438\u0447\u043a\u0438 \u043c\u0430\u0440\u0448\u0440\u0443\u0442\u0438 \u0441\u0430 \u0431\u0435\u0437 \u0432\u0435\u0440\u0441\u0438\u044f. "
        "\u041f\u0440\u0435\u0444\u0438\u043a\u0441 /v1/ \u0431\u0438 \u043f\u043e\u0437\u0432\u043e\u043b\u0438\u043b \u043e\u0431\u0440\u0430\u0442\u043d\u043e-\u0441\u044a\u0432\u043c\u0435\u0441\u0442\u0438\u043c\u0430 \u0435\u0432\u043e\u043b\u044e\u0446\u0438\u044f."
    )

    # -- Output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    build_pdf("docs/Doctor_Visit_Booking_API_Documentation.pdf")
