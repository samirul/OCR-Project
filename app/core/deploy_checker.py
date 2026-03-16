"""Check deployment current types from environment variables."""
import os
from starlette.config import Config

# Configs for production or local dev env.
DEPLOYMENT_TYPE = str(os.environ.get("DEPLOYMENT_ENV")).lower()

# Check for deployment type(Either production or local dev)
def deploy_checker_auth_services():
    """Select and load the appropriate environment configuration.

    This function checks the current deployment type and returns a configuration
    object pointing to either the production or local environment file.

    Returns:
        Config: A Starlette Config instance loaded from the selected environment file.
    """
    return (
        Config(env_file='.env.prod')
        if DEPLOYMENT_TYPE in {'prod', 'production'}
        else Config(env_file='.env.local')
    )

def deploy_checker_pydantic_settings():
    """Get the environment file path for Pydantic settings.

    This function checks the current deployment type and returns the name of
    the environment file that should be used for loading Pydantic settings.

    Returns:
        str: The filename of the environment file for the current deployment.
    """
    return ('.env.prod'
            if DEPLOYMENT_TYPE in {'prod', 'production'}
            else '.env.local'
    )