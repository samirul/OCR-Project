import uuid
from sqlalchemy import String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class BlackListedTokens(Base):
    """Represents a record of access and refresh tokens that have been invalidated. This model is used to prevent the reuse of tokens that should no longer grant access.

    Each entry captures the token pair along with the time they were blacklisted, enabling checks against compromised or revoked credentials.

    Attributes:
        id: The unique identifier for the blacklist entry.
        access_token: The access token string that has been blacklisted.
        refresh_token: The refresh token string that has been blacklisted.
        created_at: The timestamp when the tokens were added to the blacklist.
    """

    __tablename__ = "black_listed_token"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    access_token: Mapped[str] = mapped_column(
        String, nullable=False
    )
    refresh_token: Mapped[str] = mapped_column(
        String, nullable=False
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
    )
