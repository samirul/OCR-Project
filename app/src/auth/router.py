"""Router for social authentication and authentication"""

import logging
from fastapi import APIRouter, HTTPException
from app.src.auth.service import validate_google_token_and_extract_user_info
from app.src.auth.schemas import GoogleAuthCode
from app.core.deploy_checker import deploy_checker_auth_services

config = deploy_checker_auth_services()
logger = logging.getLogger(__name__)
router_v1 = APIRouter()


@router_v1.post('login/google')
async def google_login(body: GoogleAuthCode):
    """Handles Google OAuth login requests and processes user authentication. This endpoint receives an authorization code, validates it, and surfaces authentication errors to the client.

    The function delegates token validation and user extraction to the authentication service layer and returns appropriate HTTP errors when verification fails.

    Args:
        body: The request payload containing the Google authorization code.
    """
    try:
        user = validate_google_token_and_extract_user_info(body)
        print(user)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}") from e