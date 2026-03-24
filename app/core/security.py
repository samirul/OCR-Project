"""Related to JWT and password logics"""

from typing import Literal
from datetime import datetime, timedelta, timezone
from fastapi import Response
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import jwt_configs_settings
from app.exceptions.exception import jwt_validation_error_exception
from app.core.schemas import TokenData

SECRET_KEY = jwt_configs_settings.secret_key
ALGORITHM = jwt_configs_settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(jwt_configs_settings.jwt_expiration_minutes)
SameSitePolicy = Literal["lax", "strict", "none"]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
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
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
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
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=secure,
        samesite=same_site,
        max_age=max_age,
        path=path, 
    )