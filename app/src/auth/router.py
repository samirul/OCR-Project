"""Router for social authentication and authentication"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.src.auth.service import validate_google_token_and_extract_user_info, return_tokens_and_credentials
from app.src.auth.schemas import GoogleAuthCode, GoogleLoginResponseOut
from app.core.deploy_checker import deploy_checker_auth_services
from app.src.users.service import get_user_data_from_oauth_google, create_user_oauth
from app.db.session import get_db

config = deploy_checker_auth_services()
logger = logging.getLogger(__name__)
router_auth = APIRouter()


@router_auth.post('login/google', response_model=GoogleLoginResponseOut)
async def google_login(body: GoogleAuthCode, db: Session = Depends(get_db)):
    """Handle user login via Google OAuth and create or update the user in the system.

    This endpoint validates the provided Google authorization code, extracts user data,
    and persists the user information in the database if authentication is successful.

    Args:
        body: The payload containing the Google authorization code to be validated.
        db: The database session dependency used for persisting user data.

    Raises:
        HTTPException: Raised with a 401 status code if token verification fails, or
            with a 500 status code if an unexpected authentication error occurs.
    """
    try:
        user = validate_google_token_and_extract_user_info(body)
        serialized_data = get_user_data_from_oauth_google(user)
        data = await create_user_oauth(serialized_data, db)
        return await return_tokens_and_credentials({"id": str(data.id), "email": str(data.email)})
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}") from e