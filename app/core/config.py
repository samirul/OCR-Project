"""Pydantic settings for core application."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.deploy_checker import deploy_checker_pydantic_settings

ENV_FILE = deploy_checker_pydantic_settings()

class DatabaseSettings(BaseSettings):
    """Application database configuration settings.

    This class loads database connection settings from environment variables
    and provides them as strongly-typed attributes for the application.

    Attributes:
        database_hostname (str): Hostname of the database server.
        database_port (str): Port on which the database server is listening.
        database_password (str): Password used to authenticate with the database.
        database_name (str): Name of the application database.
        database_username (str): Username used to authenticate with the database.
    """
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), extra='ignore')
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str

database_configs_settings = DatabaseSettings() # type: ignore
