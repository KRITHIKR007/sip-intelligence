"""
SIP Intelligence — User, Department and Permission Models
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.documents import Project


# ---- Enums ----------------------------------------------------------------

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    ENGINEER = "ENGINEER"
    VIEWER = "VIEWER"
    MANAGER = "MANAGER"


class PermissionLevel(str, enum.Enum):
    READ = "READ"
    WRITE = "WRITE"
    ADMIN = "ADMIN"


# ---- Models ---------------------------------------------------------------

class Department(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "departments"
    __table_args__ = {"schema": "sip"}

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    users: Mapped[list["User"]] = relationship(back_populates="department")


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = {"schema": "sip"}

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, schema="sip"), default=UserRole.VIEWER)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.departments.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    department: Mapped[Optional["Department"]] = relationship(back_populates="users")
    permissions: Mapped[list["ProjectPermission"]] = relationship(back_populates="user")


class ProjectPermission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "project_permissions"
    __table_args__ = {"schema": "sip"}

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.users.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.projects.id", ondelete="CASCADE"), nullable=False
    )
    permission_level: Mapped[PermissionLevel] = mapped_column(
        Enum(PermissionLevel, schema="sip"), default=PermissionLevel.READ
    )

    user: Mapped["User"] = relationship(back_populates="permissions")
    project: Mapped["Project"] = relationship(back_populates="permissions")

