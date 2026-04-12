from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.doctors.models import Doctor
    from app.patients.models import Patient


class User(Base, TimestampMixin):
    """Login identity shared by doctors and patients."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('doctor', 'patient')",
            name="ck_users_role",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)

    doctor: Mapped[Optional[Doctor]] = relationship(
        "Doctor",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    patient: Mapped[Optional[Patient]] = relationship(
        "Patient",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
