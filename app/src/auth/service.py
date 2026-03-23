"""Business logics for all type authentications"""

from typing import Mapping
from fastapi import HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from app.core.deploy_checker import deploy_checker_auth_services
from app.src.auth.schemas import GoogleAuthCode, GoogleLoginResponseOut, UserPayload
from app.core.security import create_access_token, verify_token
from app.exceptions.exception import google_token_invalid_exception, google_token_not_provided_exception

config = deploy_checker_auth_services()

def google_auth_configs()-> dict[str, str]:
    """Builds and returns Google OAuth configuration values. This helper centralizes access to deployment-specific Google authentication settings.

    The configuration includes client credentials, OAuth endpoints, redirect URI, and commonly used OAuth scopes for email, profile, and OpenID.

    Returns:
        dict[str, str]: A mapping of Google OAuth configuration keys to their corresponding values.
    """
    return {
        "client_id": config("GOOGLE_CLIENT_ID"),
        "client_secret": config("GOOGLE_CLIENT_SECRET"),
        "auth_uri": config("GOOGLE_AUTHORIZATION_URL"),
        "token_uri": config("GOOGLE_ACCESS_TOKEN_URL"),
        "redirect_uri": config("GOOGLE_REDIRECT_URI"),
        "scopes_email": config("GOOGLE_SCOPES_EMAIL"),
        "scopes_profile": config("GOOGLE_SCOPES_PROFILE"),
        "scopes_open_id": config("GOOGLE_SCOPES_OPENID"),

    }

def get_google_credentials(data: dict[str, str]) -> dict[str, dict[str, object]]:
    """Constructs a Google OAuth client configuration mapping from raw configuration values. This prepares the structure required by the Google OAuth flow initializer.

    The configuration is grouped under the 'web' key and ensures redirect URIs are provided as a list.

    Args:
        data: A dictionary containing Google OAuth configuration values such as client ID, client secret, endpoints, and redirect URI.

    Returns:
        dict[str, dict[str, object]]: A nested mapping in the format expected by Google OAuth client libraries.
    """
    return {
        "web": {
            "client_id": str(data.get("client_id")),
            "client_secret": str(data.get("client_secret")),
            "auth_uri": str(data.get("auth_uri")),
            "token_uri": str(data.get("token_uri")),
            "redirect_uris": [str(data.get("redirect_uri"))],
        }
    }

    
def google_flow() -> Flow:
    """Creates and returns a configured Google OAuth Flow instance. This flow manages the authorization URL generation and callback handling for Google sign-in.

    The flow is configured using deployment-specific OAuth credentials and scopes loaded from the environment.

    Returns:
        Flow: A Google OAuth flow object ready to initiate the authorization process.
    """
    data = google_auth_configs()
    return Flow.from_client_config(
        get_google_credentials(data=data),
        scopes=[str(data.get("scopes_open_id")), str(data.get("scopes_email")), str(data.get("scopes_profile"))],
        redirect_uri=str(data.get("redirect_uri")),
    )

def verify_google_token(token: str) -> Mapping[str, object]:
    """Validates a Google OAuth ID token against the configured client. This ensures the token is authentic and was issued for this application.

    The verification returns the decoded token payload if the token is valid and raises an error if validation fails.

    Args:
        token: The Google OAuth ID token to validate.

    Returns:
        dict: The decoded token payload containing user and token metadata.
    """
    data = google_auth_configs()
    return id_token.verify_oauth2_token(
        token,
        requests.Request(),
        str(data.get("client_id")),
        clock_skew_in_seconds=10,
)

def exchange_auth_code_for_token(code: str):
    """Exchanges a Google authorization code for OAuth credentials. This function performs the token retrieval step in the Google OAuth flow using the provided code.

    When the exchange fails due to grant issues or configuration errors, it raises standardized Google token exceptions for consistent error handling.

    Args:
        code: The short-lived authorization code received from Google's OAuth redirect.

    Returns:
        Credentials: The Google OAuth credentials obtained from the authorization code.

    Raises:
        HTTPException: If the authorization code is invalid, expired, reused, or the client configuration is incorrect.
    """
    try:
        flow = google_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials
        return credentials
    except InvalidGrantError as e:
        # Auth code expired, already used
        raise google_token_invalid_exception() from e
    except ValueError as e:
        # Invalid client configuration or other issues
        raise google_token_not_provided_exception() from e

def validate_google_audience_and_email(id_info: Mapping[str, object], data: dict[str, str]):
    """Validates that a Google ID token is intended for this client and that the user's email is verified. This ensures only trusted and verified Google accounts can proceed.

    The function checks the token audience against the configured client ID and enforces that Google has marked the email as verified.

    Args:
        id_info: The decoded Google ID token payload containing token and user information.
        data: The Google OAuth configuration values, including the expected client ID.

    Raises:
        HTTPException: If the audience does not match or the email is not verified.
    """
    if id_info.get("aud") != str(data.get("client_id")):
        raise HTTPException(status_code=401, detail="Invalid google audience.")
    if not id_info.get("email_verified"):
        raise HTTPException(status_code=401, detail="Email not verified by Google.")

def extract_user_info_from_id_token(id_info: Mapping[str, object]) -> dict[str, object]:
    """Extracts core user profile information from a verified Google ID token payload. This presents the token data in a simplified structure suitable for downstream authentication logic.

    The returned dictionary includes the user's unique Google identifier, email, display name, and profile picture URL when available.

    Args:
        id_info: The decoded and verified Google ID token payload.

    Returns:
        dict[str, object]: A mapping of user attributes derived from the ID token.
    """
    return {
        # "sub": id_info["sub"],  # Google's unique id for user.
        "email": id_info["email"],
        "name": id_info.get("name"),
        "picture": id_info.get("picture"),
    }

def validate_google_token_and_extract_user_info(body: GoogleAuthCode) -> dict[str, object]:
    """Validates a Google authorization code and extracts user profile information. This function orchestrates the full Google OAuth verification flow for a single sign-in request.

    The process exchanges the code for tokens, verifies the ID token, enforces audience and email checks, and returns a simplified user representation.

    Args:
        body: The request body containing the Google authorization code.

    Returns:
        dict[str, object]: A mapping of validated user attributes derived from the Google ID token.
    """
    credentials = exchange_auth_code_for_token(body.code)
    data = google_auth_configs()
    id_info = verify_google_token(credentials.id_token) # type: ignore
    validate_google_audience_and_email(id_info=id_info, data=data)
    return extract_user_info_from_id_token(id_info=id_info)

async def return_tokens_and_credentials(data: dict) -> GoogleLoginResponseOut:
    """Generates an access token for a Google-authenticated user and returns it with basic user payload. This helper wraps token creation and verification into a single response builder.

    The function signs the provided data into a JWT, validates the resulting token, and embeds the derived user identifier and email in the response payload.

    Args:
        data: A dictionary containing user-related data to be encoded into the access token.

    Returns:
        GoogleLoginResponseOut: An object containing the access token, an empty refresh token, and a user payload with ID and email.
    """
    access_token = create_access_token(data)
    payload_data = verify_token(access_token)
    return GoogleLoginResponseOut(
        access_token=access_token,
        refresh_token="",
        user=UserPayload(id=payload_data.id, email=payload_data.email)
    )
