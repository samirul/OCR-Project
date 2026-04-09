"""Related to JWT and password logics"""

from typing import Literal
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from itsdangerous import URLSafeTimedSerializer
from app.core.config import jwt_configs_settings
from app.exceptions.exception import black_listed_token_exception, invalid_input_token_submitted, invalid_user_exception, jwt_validation_error_exception
from app.core.schemas import BlackListData, TokenData
from app.src.users.models import User
from app.src.auth.models import BlackListedTokens

SECRET_KEY = jwt_configs_settings.secret_key
ALGORITHM = jwt_configs_settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(jwt_configs_settings.jwt_expiration_minutes)
SameSitePolicy = Literal["lax", "strict", "none"]
url_safe_serializer = URLSafeTimedSerializer(SECRET_KEY)

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


async def check_validity_of_refresh_token_and_return_token_data(db: AsyncSession, token: str):
    """Validate a refresh token and return the associated user record. This function ensures the token is a refresh token, belongs to a real user, and is structurally valid.

    The function decodes the token, verifies its type, looks up the corresponding user in the database, and raises a standardized error if no matching user is found.

    Args:
        db: The database AsyncSession used to query the user table.
        token: The encoded JWT refresh token submitted by the client.

    Returns:
        User: The user associated with the provided refresh token.

    Raises:
        HTTPException: If the token is invalid, not a refresh token, or the user does not exist.
    """
    token_data = verify_token(token)
    check_token_type_refresh_token(token)
    user_query = (
        select(User)
        .where(User.id == token_data.id)
        .where(User.email == token_data.email)
    )
    user = (await db.scalars(user_query)).first()
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


async def blacklisting_existing_tokens(db: AsyncSession, tokens: BlackListData):
    """Persist a token pair in the blacklist to prevent its future use. This function records revoked access and refresh tokens along with the associated user.

    The function creates a blacklist entry from the provided token data, stores it in the database, and finalizes the transaction so the revocation is durable.

    Args:
        db: The database AsyncSession used to store the blacklist entry.
        tokens: The token data containing access, refresh, and user identifier fields to blacklist.

    Returns:
        None: This function commits the blacklist entry and does not return a value.
    """
    new_tokens_blacklist = BlackListedTokens(**tokens.model_dump())
    db.add(new_tokens_blacklist)
    await db.commit()
    await db.refresh(new_tokens_blacklist)

async def reject_blacklisted_tokens(db: AsyncSession,  token: BlackListData):
    """Reject the use of tokens that have already been blacklisted. This function prevents revoked access and refresh tokens from being reused for authentication or refresh flows.

    The function checks the blacklist for a matching token pair and raises a standardized error if a revoked entry is found.

    Args:
        db: The database AsyncSession used to query the blacklist table.
        token: The token data containing access, refresh, and user identifier fields to validate.

    Returns:
        None: This function raises an exception when a match is found instead of returning a value.

    Raises:
        HTTPException: If the provided token pair has already been blacklisted.
    """
    blacklisted_query = (
        select(BlackListedTokens)
        .where(BlackListedTokens.access_token == token.access_token)
        .where(BlackListedTokens.refresh_token == token.refresh_token)
        .where(BlackListedTokens.user_id == token.user_id)
    )
    blacklisted_tokens = (await db.scalars(blacklisted_query)).first()
    if blacklisted_tokens is not None:
        raise black_listed_token_exception()


async def fetch_new_tokens(db: AsyncSession, response: Response, refresh_token: str, access_token: str):
    """Issue a fresh pair of access and refresh tokens using a valid refresh token. This endpoint enforces token revocation rules by blacklisting the previous tokens before returning new ones.

    The function validates the submitted refresh token, ensures the existing tokens are not already revoked, blacklists them, generates new tokens, and stores the new pair in secure cookies.

    Args:
        db: The database AsyncSession used to validate and blacklist tokens.
        response: The HTTP response object that will receive the new token cookies.
        refresh_token: The current JWT refresh token presented by the client.
        access_token: The current JWT access token associated with the session.

    Returns:
        str: The newly generated access token that replaces the previous one.

    Raises:
        HTTPException: If the refresh token is invalid, the user does not exist, or the tokens have already been blacklisted.
    """
    data = await check_validity_of_refresh_token_and_return_token_data(db, refresh_token)
    await reject_blacklisted_tokens(db, BlackListData(access_token=access_token, refresh_token=refresh_token, user_id=str(data.id)))
    await blacklisting_existing_tokens(db, BlackListData(access_token=access_token, refresh_token=refresh_token, user_id=str(data.id)))
    new_access_token, new_refresh_token = new_tokens_are_generated({"id": str(data.id), "email": str(data.email)})
    new_tokens_save_in_http_only_cookie(response, new_access_token, new_refresh_token)
    return new_access_token

def generate_csrf_token(response: Response):
    """Generate a CSRF token and attach it to the response as a cookie. This token helps protect state-changing requests against cross-site request forgery attacks.

    The function creates a signed, URL-safe token using the application secret key and stores it in a non-HTTP-only cookie with a strict SameSite policy.

    Args:
        response: The HTTP response object on which the CSRF cookie will be set.

    Returns:
        None: This function modifies the response in-place and does not return a value.
    """
    new_csrf_token = url_safe_serializer.dumps(SECRET_KEY)
    response.set_cookie(
        key="csrf_token",
        value=new_csrf_token,
        httponly=False,
        samesite="strict",
        secure=True
    )

def verify_csrf_token(request: Request):
    """Validate that the CSRF token in the request headers matches the token stored in cookies. This function enforces CSRF protection by ensuring both tokens are present and identical.

    When the tokens are missing or do not match, the function raises a 403 Forbidden error to block the potentially unsafe request.

    Args:
        request: The incoming HTTP request containing cookies and headers to validate.

    Raises:
        HTTPException: If the CSRF token is missing from either location or if the two tokens do not match.
    """
    cookie_token = request.cookies.get("csrf_token")
    header_token = request.headers.get("X-CSRF-Token")
    if not cookie_token or not header_token:
        raise HTTPException(status_code=403, detail="CSRF token is missing")
    if cookie_token != header_token:
        raise HTTPException(status_code=403, detail="CSRF token is mismatch")
