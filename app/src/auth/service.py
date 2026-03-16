"""Business logics for all type authentications"""

import json
from authlib.integrations.starlette_client import OAuth
from app.core.deploy_checker import deploy_checker_auth_services

config = deploy_checker_auth_services()
oauth = OAuth(config=config)

def google_auth_configs():
    """Configure and register the Google OAuth client.

    This function initializes a Google OAuth client using environment-based configuration
    and registers it with the shared OAuth instance.

    Returns:
        OAuth: The registered Google OAuth client instance.
    """
    return oauth.register(
        name="google",
        client_id=config("GOOGLE_CLIENT_ID"),
        client_secret=config("GOOGLE_CLIENT_SECRET"),
        access_token_url=config("GOOGLE_ACCESS_TOKEN_URL"),
        authorization_url=config("GOOGLE_AUTHORIZATION_URL"),
        api_base_url=config("GOOGLE_API_BASE_URL"),
        user_info_endpoint=config("GOOGLE_USER_INFO_ENDPOINT"),
        client_kwargs={'scope': 'openid email profile'}
    )

def auth_provider_func(provider: str = "google"):
    """Create and return an OAuth client for the requested authentication provider.

    This function validates the requested provider and either returns an error response
    or creates an OAuth client for initiating the authentication flow.

    Args:
        provider (str): The OAuth provider name, expected to be "google" or "github".

    Returns:
        OAuth | str: An OAuth client instance when the provider is valid,
            otherwise a JSON-encoded error message.
    """
    if provider.lower() not in {"google", "github"}:
        return json.dumps({"error": "Provider must be google or github."})
    return oauth.create_client(provider)

