import logging
from fastapi import APIRouter, Response, status
from app.core.security import generate_csrf_token

logger = logging.getLogger(__name__)
router_csrf = APIRouter()

@router_csrf.get('/csrf_token', status_code=status.HTTP_200_OK)
async def csrf_token_get(response: Response):
    """Retrieve and attach a CSRF token to the response headers.

    This endpoint generates a new CSRF token and includes it in the response so that subsequent requests can be protected.

    Args:
        response: The outgoing HTTP response object to which the CSRF token will be attached.

    Returns:
        str: The generated CSRF token value.
    """
    return generate_csrf_token(response)