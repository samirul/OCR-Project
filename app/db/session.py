"""Configuration for Database, Engine & SessionLocal"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import database_configs_settings

# Database URL.
DATABASE_URL = f"postgresql+asyncpg://{
    database_configs_settings.database_username
    }:{database_configs_settings.database_password
    }@{database_configs_settings.database_hostname
    }:{database_configs_settings.database_port
    }/{database_configs_settings.database_name}"

# Create engine.
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create the Session maker.
SessionLocal = async_sessionmaker(
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for inherit by all models.
Base = declarative_base()