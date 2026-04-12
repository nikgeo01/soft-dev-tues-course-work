from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.appointments.models import Appointment
    from app.auth.models import User
    from app.patients.models import Patient
    from app.schedules.models import PermanentChange, TemporaryOverride, WorkingHours


class Doctor(Base, TimestampMixin):
    """Doctor profile; primary key is the same as the linked user id."""

    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(512), nullable=False)

    user: Mapped[User] = relationship(
        "User",
        back_populates="doctor",
        foreign_keys=[id],
    )
    patients: Mapped[list[Patient]] = relationship(
        "Patient",
        back_populates="doctor",
        foreign_keys="Patient.doctor_id",
    )
    working_hours: Mapped[list[WorkingHours]] = relationship(
        "WorkingHours",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )
    temporary_override: Mapped[Optional[TemporaryOverride]] = relationship(
        "TemporaryOverride",
        back_populates="doctor",
        uselist=False,
        cascade="all, delete-orphan",
    )
    permanent_changes: Mapped[list[PermanentChange]] = relationship(
        "PermanentChange",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )
    appointments: Mapped[list[Appointment]] = relationship(
        "Appointment",
        back_populates="doctor",
        foreign_keys="Appointment.doctor_id",
    )
