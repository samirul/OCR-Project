import uuid
from sqlalchemy import String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class BlackListedTokens(Base):

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
