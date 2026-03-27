import uuid
from sqlalchemy import String, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class BlackListedTokens(Base):
    """Represents a record of tokens that have been invalidated and should no longer be accepted. This model is used to persist blacklisted tokens for security and auditing purposes.

    The blacklisted tokens are associated with a specific user and timestamped to track when they were revoked.

    Attributes:
        id: The unique identifier of the blacklisted token record.
        access_token: The access token that has been blacklisted and must be rejected.
        refresh_token: The refresh token that has been blacklisted and must be rejected.
        user_id: The identifier of the user to whom the blacklisted tokens belong.
        created_at: The timestamp indicating when the tokens were blacklisted.
        user: The user relationship associated with the blacklisted tokens.
    """

    __tablename__ = "black_listed_token"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    access_token: Mapped[str] = mapped_column(
        String, nullable=True
    )
    refresh_token: Mapped[str] = mapped_column(
        String, nullable=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("user.id", ondelete="CASCADE"), 
        nullable=False
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
    )
    user: Mapped["User"] = relationship(back_populates="blacklisted_tokens") # type: ignore
