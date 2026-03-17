"""Created User model"""
import uuid
from typing import Optional
from sqlalchemy import String, text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class User(Base):
    """Represent an application user and their core account attributes.
    This model defines how user data is stored and managed in the database.

    The user record includes identity, authentication, and status information.
    It also tracks profile metadata and timestamps for auditing user lifecycle.
    """
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String, nullable=False, unique=True
    )

    username: Mapped[str] = mapped_column(
        String, nullable=False, unique=True
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    profile_picture: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        default=None
    )

    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
    )

    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        onupdate=text('now()'),
        nullable=False
    )
