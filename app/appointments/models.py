from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.doctors.models import Doctor
    from app.patients.models import Patient


class Appointment(Base, TimestampMixin):
    """Scheduled visit between a patient and their doctor."""

    __tablename__ = "appointments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'cancelled')",
            name="ck_appointments_status",
        ),
        CheckConstraint(
            "cancelled_by IS NULL OR cancelled_by IN ('doctor', 'patient')",
            name="ck_appointments_cancelled_by",
        ),
        Index(
            "ix_appointments_doctor_time",
            "doctor_id",
            "start_datetime",
            "end_datetime",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
    )
    start_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=text("'scheduled'"),
    )
    cancelled_by: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    doctor: Mapped[Doctor] = relationship(
        "Doctor",
        back_populates="appointments",
        foreign_keys=[doctor_id],
    )
    patient: Mapped[Patient] = relationship(
        "Patient",
        back_populates="appointments",
        foreign_keys=[patient_id],
    )
