"""Created User model"""
import uuid
from typing import Optional, List
from sqlalchemy import String, text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class User(Base):
    """Represents an application user and their core account information. This model defines the primary identity, status, and profile fields used throughout the system.

    The user record also tracks creation and update timestamps, along with relationships to security-related data such as blacklisted tokens.

    Attributes:
        id: The unique identifier for the user.
        email: The user's email address, which must be unique.
        username: The user's chosen username, which must be unique.
        is_admin: Indicates whether the user has administrative privileges.
        is_active: Indicates whether the user's account is currently active.
        profile_picture: An optional URL or path to the user's profile image.
        created_at: The timestamp when the user account was created.
        updated_at: The timestamp when the user account was last updated.
        blacklisted_tokens: A collection of blacklisted tokens associated with the user.
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
    blacklisted_tokens: Mapped[List["BlackListedTokens"]] = relationship(back_populates="user") # type: ignore
