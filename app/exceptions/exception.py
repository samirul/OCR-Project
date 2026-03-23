from uuid import UUID
from fastapi import status, HTTPException

def jwt_validation_error_exception():
    """Creates an HTTP exception representing a failed JWT authentication attempt. This helper standardizes the error response for invalid or missing authentication credentials.

    The returned exception uses a 401 Unauthorized status and includes the appropriate WWW-Authenticate header for Bearer tokens.

    Returns:
        HTTPException: An exception configured for JWT validation failure responses.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication Credentials could not validated.",
        headers={"WWW-Authenticate": "Bearer"},
    )

def check_valid_uuid(ids: str):
    """Validates that a given string is a properly formatted UUID. This helper ensures identifiers conform to UUID standards before they are used in the system.

    If the string is not a valid UUID, the function raises an HTTP 400 Bad Request error to signal invalid input to the client.

    Args:
        ids: The string value expected to represent a UUID.

    Raises:
        HTTPException: If the provided string is not a valid UUID.
    """
    try:
        UUID(ids)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format.",
        ) from e