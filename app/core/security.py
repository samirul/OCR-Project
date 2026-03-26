"""Related to JWT and password logics"""

from typing import Literal
from datetime import datetime, timedelta, timezone
from fastapi import Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.core.config import jwt_configs_settings
from app.exceptions.exception import invalid_input_token_submitted, invalid_user_exception, jwt_validation_error_exception
from app.core.schemas import TokenData
from app.src.users.models import User

SECRET_KEY = jwt_configs_settings.secret_key
ALGORITHM = jwt_configs_settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(jwt_configs_settings.jwt_expiration_minutes)
SameSitePolicy = Literal["lax", "strict", "none"]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, token_type: str):
    """Creates a short-lived JWT access token from the provided payload data. This token is used to authenticate and authorize subsequent client requests.

    The function copies the input data, adds an expiration claim, and signs the token using the configured secret and algorithm.

    Args:
        data: A dictionary containing the claims to embed in the access token payload.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    to_encode["token_type"] = token_type
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, token_type: "str"):
    """Creates a long-lived JWT refresh token from the provided payload data. This token allows clients to obtain new access tokens without reauthenticating.

    The function augments the payload with a refresh-specific expiration time and signs it using the configured secret and algorithm.

    Args:
        data: A dictionary containing the claims to embed in the refresh token payload.

    Returns:
        str: The encoded JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode["exp"] = expire
    to_encode["token_type"] = token_type
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> TokenData:
    """Verifies a JWT token and extracts the core user identity information. This function ensures the token is valid and returns a structured representation of the embedded user data.

    If the token cannot be decoded or required claims are missing, a standardized authentication error is raised.

    Args:
        token: The encoded JWT string received from the client.

    Returns:
        TokenData: The parsed token payload containing the user's ID and email.

    Raises:
        HTTPException: If the token is invalid, expired, or missing required claims.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        ids: str = payload["id"]
        email: str = payload["email"]
        if ids is None and email is None:
            raise jwt_validation_error_exception()
        return TokenData(id=ids, email=email)
    except JWTError as exc:
        raise jwt_validation_error_exception() from exc
    
def save_tokens_in_http_only_cookie(
        response: Response,
        key: str,
        value: str,
        secure: bool = True,
        same_site: SameSitePolicy = "lax",
        max_age: int = 900,
        path: str = "/"):
    """Saves a token into an HTTP-only cookie on the response. This helper ensures tokens are stored securely with appropriate cookie attributes.

    The function wraps FastAPI's cookie-setting mechanism to consistently apply security-related flags and expiration settings for authentication cookies.

    Args:
        response: The HTTP response object on which the cookie will be set.
        key: The name of the cookie used to store the token.
        value: The token value to be stored in the cookie.
        secure: Whether the cookie should only be sent over HTTPS connections.
        same_site: The SameSite policy controlling cross-site cookie behavior.
        max_age: The maximum age of the cookie in seconds before it expires.
        path: The URL path for which the cookie is valid.

    Returns:
        None: This function modifies the response in-place and does not return a value.
    """
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=secure,
        samesite=same_site,
        max_age=max_age,
        path=path,
    )

def check_token_type_refresh_token(token: str):
    """Ensures that a given JWT is explicitly marked as a refresh token. This guard protects refresh-only flows from being used with other token types.

    The function decodes the token payload, inspects the `token_type` claim, and raises a standardized error if it does not match the expected refresh token value.

    Args:
        token: The encoded JWT string that should represent a refresh token.

    Returns:
        None: This function raises an exception if validation fails instead of returning a value.

    Raises:
        HTTPException: If the token's `token_type` claim is missing or not equal to ``"refresh_token"``.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("token_type") != "refresh_token":
        raise invalid_input_token_submitted()


def check_validity_of_refresh_token_and_return_token_data(db: Session, token: str):
    """Validates a refresh token and returns its associated user identity data. This helper ensures both the token and its linked user account are still valid before issuing new tokens.

    The function verifies the JWT, checks that it is a refresh token, confirms the referenced user exists in the database, and then returns the parsed token payload.

    Args:
        db: The database session used to look up the user referenced in the token.
        token: The encoded JWT string that should represent a refresh token.

    Returns:
        TokenData: The structured token data containing the user's ID and email.

    Raises:
        HTTPException: If the token is invalid, not a refresh token, or the user no longer exists.
    """
    token_data = verify_token(token)
    check_token_type_refresh_token(token)
    user_query = (
        select(User)
        .where(User.id == token_data.id)
        .where(User.email == token_data.email)
    )
    user = db.scalars(user_query).first()
    if user is None:
        raise invalid_user_exception()
    return token_data
    

def new_tokens_are_generated(data: dict):
    """Generates a new pair of access and refresh JWT tokens for a user. This helper encapsulates the token creation logic for refresh workflows.

    The function takes core user identity data, creates a short-lived access token and a longer-lived refresh token, and returns both for further handling by the caller.

    Args:
        data: A dictionary containing user identity claims to embed in the tokens.

    Returns:
        tuple[str, str]: A tuple containing the new access token followed by the new refresh token.
    """
    new_access_token = create_access_token(data, "access_token")
    new_refresh_token = create_refresh_token(data, "refresh_token")
    return new_access_token, new_refresh_token

def new_tokens_save_in_http_only_cookie(response: Response, new_access_token, new_refresh_token):
    """Stores a newly generated access and refresh token pair in HTTP-only cookies. This helper centralizes how authentication tokens are written to the client response.

    The function delegates to the cookie-saving utility for each token, ensuring consistent cookie names and security-related attributes across the application.

    Args:
        response: The HTTP response object on which the cookies will be set.
        new_access_token: The freshly issued JWT access token to store in a cookie.
        new_refresh_token: The freshly issued JWT refresh token to store in a cookie.

    Returns:
        None: This function updates the response in-place and does not return a value.
    """
    save_tokens_in_http_only_cookie(response, "access_token", new_access_token)
    save_tokens_in_http_only_cookie(response, "refresh_token", new_refresh_token)


def fetch_new_tokens(response: Response, db: Session, token: str):
    """Exchanges a valid refresh token for a new access token and updates client cookies. This function coordinates refresh token validation, token rotation, and cookie management.

    The function verifies the submitted refresh token, generates a fresh token pair based on the embedded user identity, stores the new tokens in HTTP-only cookies, and returns the new access token.

    Args:
        response: The HTTP response object that will be updated with new token cookies.
        db: The database session used to validate the user associated with the refresh token.
        token: The encoded JWT refresh token submitted by the client.

    Returns:
        str: The newly generated access token.
    """
    data = check_validity_of_refresh_token_and_return_token_data(db, token)
    data={"id": str(data.id), "email": str(data.email)}
    new_access_token, new_refresh_token = new_tokens_are_generated(data)
    new_tokens_save_in_http_only_cookie(response, new_access_token, new_refresh_token)
    return new_access_token

