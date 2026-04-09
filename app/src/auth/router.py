"""Router for social authentication and authentication"""

import logging
from fastapi import APIRouter, Depends, Response, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db
from app.core.security import fetch_new_tokens, generate_csrf_token, verify_csrf_token
from app.src.auth.service import github_login_user, validate_google_token_and_extract_user_info, return_tokens_and_credentials
from app.src.auth.schemas import GoogleAuthCode, GithubAuthCode ,GoogleLoginResponseOut, GithubLoginResponseOut, RegisterUserResponseOut, ResponseTokenOut, RegisterUser, ShowStatus
from app.core.deploy_checker import deploy_checker_auth_services
from app.src.users.service import create_user, get_user_data, get_user_data_from_oauth, create_user_oauth

config = deploy_checker_auth_services()
logger = logging.getLogger(__name__)
router_auth = APIRouter()


@router_auth.post('/login/google', response_model=GoogleLoginResponseOut)
async def google_login(response: Response, body: GoogleAuthCode, db: AsyncSession = Depends(get_db)):
    """Authenticate a user via Google OAuth and start their application session. This endpoint exchanges a Google authorization artifact for user details and issues tokens for subsequent API calls.

    The function validates the provided Google credentials, normalizes and persists the user record, sets CSRF protection, and returns access and refresh tokens along with core user identifiers.

    Args:
        response: The HTTP response object used to attach authentication and CSRF cookies.
        body: The payload containing the Google authorization code or credential data.
        db: The database session used to retrieve or create the authenticated user.

    Returns:
        GoogleLoginResponseOut: The issued access and refresh tokens, plus user identification data.
    """
    user = validate_google_token_and_extract_user_info(body)
    serialized_data = get_user_data_from_oauth(user)
    data = await create_user_oauth(db, serialized_data)
    generate_csrf_token(response)
    return await return_tokens_and_credentials(
        response= response, data={"id": str(data.id), "email": str(data.email)}
    )
@router_auth.post('/login/github', response_model=GithubLoginResponseOut)
async def github_login(response: Response, body: GithubAuthCode, db: AsyncSession = Depends(get_db)):
    """Authenticate a user via GitHub OAuth and initiate their application session. This endpoint exchanges a GitHub authorization code for user details and issues tokens for subsequent API access.

    The function validates the submitted GitHub code, normalizes and persists the user record, sets CSRF protection, and returns access and refresh tokens along with core user identifiers.

    Args:
        response: The HTTP response object used to attach authentication and CSRF cookies.
        body: The payload containing the GitHub authorization code from the OAuth flow.
        db: The database session used to retrieve or create the authenticated user.

    Returns:
        GithubLoginResponseOut: The issued access and refresh tokens, plus user identification data.
    """
    generate_csrf_token(response)
    user = await github_login_user(body.code)
    serialized_data = get_user_data_from_oauth(user)
    data = await create_user_oauth(db, serialized_data)
    return await return_tokens_and_credentials(
        response= response, data={"id": str(data.id), "email": str(data.email)}
    )

@router_auth.post('/register', status_code=status.HTTP_201_CREATED, response_model=RegisterUserResponseOut, dependencies=[Depends(verify_csrf_token)])
async def register_user(body: RegisterUser, db: AsyncSession = Depends(get_db)):
    """Register a new user account using the provided credentials. This endpoint validates the registration payload, creates the user, and returns a human-readable status message.

    The function hashes the submitted password, persists the new user record after uniqueness checks, and relies on CSRF protection to secure the registration request.

    Args:
        body: The validated registration payload containing email, username, and password fields.
        db: The database session used to create and persist the new user.

    Returns:
        RegisterUserResponseOut: A response object containing a status message about the registration outcome.
    """
    serialized_data = await get_user_data({"email": body.email,
    "username": body.username, "password": body.password.get_secret_value()})
    await create_user(db, serialized_data)
    return RegisterUserResponseOut(
        data=ShowStatus(msg="Registration is successful, please verify in your email."))

@router_auth.post('/refresh', response_model=ResponseTokenOut)
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """Refresh an expired or soon-to-expire access token using the stored refresh token. This endpoint maintains a user's authenticated session without requiring them to log in again.

    The function reads the existing token cookies from the request, delegates validation and rotation logic to the security layer, and returns a response model containing the new access token.

    Args:
        request: The incoming HTTP request containing the current token cookies.
        response: The HTTP response object that will be updated with new token cookies.
        db: The database session used for token and user validation.

    Returns:
        ResponseTokenOut: The new access token and an empty placeholder for the refresh token.
    """
    refresh_token_ = request.cookies.get("refresh_token")
    access_token = request.cookies.get("access_token")
    new_token = await fetch_new_tokens(db, response, str(refresh_token_), str(access_token))
    return ResponseTokenOut(access_token=new_token, refresh_token="")
