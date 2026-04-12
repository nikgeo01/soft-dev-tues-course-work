from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.appointments.models import Appointment
    from app.auth.models import User
    from app.doctors.models import Doctor


class Patient(Base, TimestampMixin):
    """Patient profile; primary key matches linked user id."""

    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(64), nullable=False)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="RESTRICT"),
        nullable=False,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="patient",
        foreign_keys=[id],
    )
    doctor: Mapped[Doctor] = relationship(
        "Doctor",
        back_populates="patients",
        foreign_keys=[doctor_id],
    )
    appointments: Mapped[list[Appointment]] = relationship(
        "Appointment",
        back_populates="patient",
        foreign_keys="Appointment.patient_id",
    )
