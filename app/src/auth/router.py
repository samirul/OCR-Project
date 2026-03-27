"""Router for social authentication and authentication"""

import logging
from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.security import fetch_new_tokens, generate_csrf_token
from app.src.auth.service import validate_google_token_and_extract_user_info, return_tokens_and_credentials
from app.src.auth.schemas import GoogleAuthCode, GoogleLoginResponseOut, ResponseTokenOut
from app.core.deploy_checker import deploy_checker_auth_services
from app.src.users.service import get_user_data_from_oauth_google, create_user_oauth

config = deploy_checker_auth_services()
logger = logging.getLogger(__name__)
router_auth = APIRouter()


@router_auth.post('/login/google', response_model=GoogleLoginResponseOut)
async def google_login(response: Response, body: GoogleAuthCode, db: Session = Depends(get_db)):
    """Authenticate a user via Google OAuth and initialize their session. This endpoint exchanges a Google authorization code for user information and issues application tokens for subsequent requests.

    The function validates the provided Google auth code, ensures the user exists or is created in the database, sets CSRF protection, and returns access and refresh tokens along with basic user identifiers.

    Args:
        response: The HTTP response object used to set authentication and CSRF cookies.
        body: The payload containing the Google authorization code and related data.
        db: The database session used to retrieve or create the authenticated user.

    Returns:
        GoogleLoginResponseOut: The issued access and refresh tokens, plus user identification data.
    """
    user = validate_google_token_and_extract_user_info(body)
    serialized_data = get_user_data_from_oauth_google(user)
    data = await create_user_oauth(db, serialized_data)
    generate_csrf_token(response)
    return await return_tokens_and_credentials(
        response= response, data={"id": str(data.id), "email": str(data.email)}
    )

@router_auth.post('/refresh', response_model=ResponseTokenOut)
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """Refreshes the user's access token using a valid refresh token stored in cookies. This endpoint validates the refresh token and issues a new short-lived access token for continued authentication.

    The function reads the refresh token from the incoming request cookies, delegates token validation and rotation to the security layer, and returns an updated access token in the response body.

    Args:
        request: The incoming HTTP request containing the refresh token cookie.
        response: The HTTP response object used to update cookies with any new tokens.
        db: The database session used to validate the user associated with the refresh token.

    Returns:
        ResponseTokenOut: The refreshed access token, with an empty refresh token field.
    """
    refresh_token_ = request.cookies.get("refresh_token")
    access_token = request.cookies.get("access_token")
    new_token = fetch_new_tokens(db, response, str(refresh_token_), str(access_token))
    return ResponseTokenOut(access_token=new_token, refresh_token="")
