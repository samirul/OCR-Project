"""Configuration for Database, Engine & SessionLocal"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import database_configs_settings

# Database URL.
DATABASE_URL = f"postgresql://{
    database_configs_settings.database_username
    }:{database_configs_settings.database_password
    }@{database_configs_settings.database_hostname
    }:{database_configs_settings.database_port
    }/{database_configs_settings.database_name}"

# Create engine.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create the Session maker.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for inherit by all models.
Base = declarative_base()