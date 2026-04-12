from __future__ import annotations

from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Time,
    UniqueConstraint,
    false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.doctors.models import Doctor


class WorkingHours(Base):
    """One time interval (work or break) for a doctor on a weekday."""

    __tablename__ = "working_hours"
    __table_args__ = (
        CheckConstraint(
            "day_of_week >= 0 AND day_of_week <= 6",
            name="ck_working_hours_dow",
        ),
        UniqueConstraint(
            "doctor_id",
            "day_of_week",
            "start_time",
            name="uq_working_hours_doctor_day_start",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_break: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
    )

    doctor: Mapped[Doctor] = relationship("Doctor", back_populates="working_hours")


class TemporaryOverride(Base, TimestampMixin):
    """At most one active temporary schedule window per doctor (enforced by UNIQUE)."""

    __tablename__ = "temporary_overrides"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    start_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    doctor: Mapped[Doctor] = relationship("Doctor", back_populates="temporary_override")
    hours: Mapped[list[TemporaryOverrideHours]] = relationship(
        "TemporaryOverrideHours",
        back_populates="override",
        cascade="all, delete-orphan",
    )


class TemporaryOverrideHours(Base):
    """Intervals for a temporary override schedule."""

    __tablename__ = "temporary_override_hours"
    __table_args__ = (
        CheckConstraint(
            "day_of_week >= 0 AND day_of_week <= 6",
            name="ck_temp_override_hours_dow",
        ),
        UniqueConstraint(
            "override_id",
            "day_of_week",
            "start_time",
            name="uq_temp_override_hours_override_day_start",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    override_id: Mapped[int] = mapped_column(
        ForeignKey("temporary_overrides.id", ondelete="CASCADE"),
        nullable=False,
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_break: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
    )

    override: Mapped[TemporaryOverride] = relationship(
        "TemporaryOverride",
        back_populates="hours",
    )


class PermanentChange(Base):
    """Future-dated permanent schedule replacement (promoted in a later phase)."""

    __tablename__ = "permanent_changes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
    )
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    applied: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    doctor: Mapped[Doctor] = relationship("Doctor", back_populates="permanent_changes")
    hours: Mapped[list[PermanentChangeHours]] = relationship(
        "PermanentChangeHours",
        back_populates="change",
        cascade="all, delete-orphan",
    )


class PermanentChangeHours(Base):
    """Intervals attached to a pending permanent change."""

    __tablename__ = "permanent_change_hours"
    __table_args__ = (
        CheckConstraint(
            "day_of_week >= 0 AND day_of_week <= 6",
            name="ck_perm_change_hours_dow",
        ),
        UniqueConstraint(
            "change_id",
            "day_of_week",
            "start_time",
            name="uq_perm_change_hours_change_day_start",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    change_id: Mapped[int] = mapped_column(
        ForeignKey("permanent_changes.id", ondelete="CASCADE"),
        nullable=False,
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_break: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
    )

    change: Mapped[PermanentChange] = relationship(
        "PermanentChange",
        back_populates="hours",
    )
