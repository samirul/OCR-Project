"""Related to JWT and password logics"""

from typing import Literal
from datetime import datetime, timedelta, timezone
from fastapi import Depends, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.core.config import jwt_configs_settings
from app.core.deps import get_db
from app.exceptions.exception import black_listed_token_exception, invalid_input_token_submitted, invalid_user_exception, jwt_validation_error_exception
from app.core.schemas import BlackListData, TokenData
from app.src.users.models import User
from app.src.auth.models import BlackListedTokens

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
    """Validates a refresh token and returns the associated user record. This helper confirms both token integrity and that the referenced user still exists.

    The function verifies that the token is a refresh token, looks up the corresponding user in the database, and raises a standardized error if validation fails.

    Args:
        db: The database session used to look up the user referenced in the token.
        token: The encoded JWT string that should represent a refresh token.

    Returns:
        User: The user model instance associated with the valid refresh token.

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
    return user
    

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


def blacklisting_existing_tokens(tokens: BlackListData, db: Session = Depends(get_db)):
    """Persists a pair of tokens to the blacklist store. This function ensures that specified access and refresh tokens can no longer be used for authentication.

    The function creates a blacklist entry from the provided token data, saves it to the database, and refreshes the instance with any persisted metadata.

    Args:
        db: The database session used to store the blacklisted tokens.
        tokens: The data object containing the access and refresh tokens to blacklist.

    Returns:
        None: This function performs a database side effect and does not return a value.
    """
    new_tokens_blacklist = BlackListedTokens(**tokens.model_dump())
    db.add(new_tokens_blacklist)
    db.commit()
    db.refresh(new_tokens_blacklist)

def reject_blacklisted_tokens(token: BlackListData, db: Session = Depends(get_db)):
    """Checks whether a given token pair has already been blacklisted. This function prevents reuse of revoked tokens by raising an error when a match is found.

    The function queries the blacklist store using the access token, refresh token, and user identifier, and blocks further processing if a corresponding entry exists.

    Args:
        db: The database session used to query the blacklist table.
        token: The token data containing access, refresh, and user identifier fields to check.

    Returns:
        None: This function raises an exception when a blacklisted token is detected instead of returning a value.

    Raises:
        HTTPException: If the provided token pair is found in the blacklist.
    """
    blacklisted_query = (
        select(BlackListedTokens)
        .where(BlackListedTokens.access_token == token.access_token)
        .where(BlackListedTokens.refresh_token == token.refresh_token)
        .where(BlackListedTokens.user_id == token.user_id)
    )
    blacklisted_tokens = db.scalars(blacklisted_query).first()
    if blacklisted_tokens is not None:
        raise black_listed_token_exception()


def fetch_new_tokens(response: Response, refresh_token: str, access_token: str, db: Session = Depends(get_db)):
    """Refreshes a user's access credentials by rotating both access and refresh tokens. This function validates the provided refresh token, revokes the old token pair, and issues new tokens.

    The function blacklists the existing tokens, generates a new token pair based on the user's identity, stores the new tokens in HTTP-only cookies, and returns the new access token.

    Args:
        response: The HTTP response object that will be updated with new token cookies.
        db: The database session used to validate the refresh token and store blacklisted tokens.
        refresh_token: The existing refresh token submitted by the client for rotation.
        access_token: The existing access token that will be blacklisted alongside the refresh token.

    Returns:
        str: The newly generated access token.
    """
    data = check_validity_of_refresh_token_and_return_token_data(db, refresh_token)
    reject_blacklisted_tokens(BlackListData(access_token=access_token, refresh_token=refresh_token, user_id=str(data.id)))
    blacklisting_existing_tokens(BlackListData(access_token=access_token, refresh_token=refresh_token, user_id=str(data.id)))
    new_access_token, new_refresh_token = new_tokens_are_generated({"id": str(data.id), "email": str(data.email)})
    new_tokens_save_in_http_only_cookie(response, new_access_token, new_refresh_token)
    return new_access_token