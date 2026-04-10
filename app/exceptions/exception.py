"""Custom exception logics"""

from uuid import UUID
from fastapi import status, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

def _build_error_entry(error: dict) -> dict:
    """Builds a normalized error description from a raw validation error entry. This helper converts internal validation details into a client-facing error structure.

    The function identifies special cases such as missing or invalid JSON bodies and produces a consistent shape for error reporting.

    Args:
        error: A dictionary containing raw validation error details, including location, type, and message.

    Returns:
        dict: A standardized error dictionary with `field`, `message`, and `type` keys.
    """
    error_type = error.get("type", "")

    raw_locations = error["loc"]
    loc = [str(location) for location in raw_locations if location != "body"]

    is_body_missing_or_invalid = (
        error_type == "json_invalid"
        or (error_type == "missing" and not loc)
    )

    if is_body_missing_or_invalid:
        return {
            "field": "body",
            "message": "Request body is required and must be valid JSON",
            "type": error_type,
        }

    field_name = " -> ".join(loc) if loc else "body"
    error_message = error["msg"]
    return {
        "field": field_name,
        "message": error_message,
        "type": error_type,
    }


def _build_errors_from_exception(exc: Exception) -> list[dict]:
    """Builds a list of normalized error entries from a validation exception. This helper converts FastAPI request validation errors into a consistent error structure.

    The function only processes `RequestValidationError` instances and returns an empty list for all other exception types.

    Args:
        exc: The exception instance that may contain request validation errors.

    Returns:
        list[dict]: A list of standardized error dictionaries derived from the exception, or an empty list if the exception is not a `RequestValidationError`.
    """
    if not isinstance(exc, RequestValidationError):
        return []
    return [_build_error_entry(error) for error in exc.errors()]


async def validation_exception_handler(_request: Request, exc: Exception):
    """Handles validation-related exceptions and formats them into a standardized JSON response. This handler ensures clients receive consistent error details for invalid requests.

    The function extracts structured validation errors when available, or falls back to a simple error message representation of the exception.

    Args:
        _request: The incoming HTTP request that triggered the validation error.
        exc: The exception instance raised during request validation.

    Returns:
        JSONResponse: A response with a 422 status code and a body containing a general detail message and a list of error entries.
    """
    errors = _build_errors_from_exception(exc)

    final_errors = errors or [{"message": str(exc)}]

    response_content = {
        "detail": "Validation failed",
        "errors": final_errors,
    }

    return JSONResponse(
        status_code=422,
        content=response_content,
    )

async def http_exception_handler(request: Request, exc: Exception):
    """Handles HTTP and unexpected exceptions by returning a structured JSON response. This handler ensures clients always receive a consistent error format for both known and internal errors.

    For recognized `HTTPException` instances, the function mirrors the original status code and detail, while unknown exceptions are mapped to a 500 Internal Server Error with a generic message.

    Args:
        request: The incoming HTTP request associated with the exception.
        exc: The exception instance that was raised during request processing.

    Returns:
        JSONResponse: A JSON response containing a detail message and a list of standardized error entries.
    """
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "errors": [
                    {
                        "field": "general",
                        "message": exc.detail,
                        "type": "http_exception"
                    }
                ]
            }
        )
    # Fallback for other exceptions
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "errors": [
                {
                    "field": "general",
                    "message": str(exc),
                    "type": "internal_error"
                }
            ]
        }
    )

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

def google_token_invalid_exception():
    """Creates an HTTP exception representing an invalid Google token. This helper standardizes the error response when Google token verification fails.

    The returned exception uses a 401 Unauthorized status and includes the appropriate WWW-Authenticate header for Bearer tokens.

    Returns:
        HTTPException: An exception configured for invalid Google token responses.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid google token provided.",
        headers={"WWW-Authenticate": "Bearer"},
    )

def google_token_not_provided_exception():
    """Creates an HTTP exception for missing or absent Google tokens. This helper provides a consistent response when a required Google token is not included in the request.

    The returned exception uses a 401 Unauthorized status and includes the appropriate WWW-Authenticate header for Bearer tokens.

    Returns:
        HTTPException: An exception configured for missing Google token errors.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Google token is not provided or not found.",
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
    
def invalid_user_exception():
    """Creates an HTTP exception indicating that the referenced user is invalid or does not exist. This helper standardizes the response when token data does not match any known user.

    The returned exception uses a 401 Unauthorized status and includes the appropriate WWW-Authenticate header for Bearer tokens.

    Returns:
        HTTPException: An exception configured for invalid or non-existent user errors.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User doesn't match or doesn't exist.",
        headers={"WWW-Authenticate": "Bearer"},
    )

def invalid_input_token_submitted():
    """Creates an HTTP exception for cases where a non-refresh token is submitted to a refresh-only endpoint. This helper standardizes the error response when the token type does not meet the required criteria.

    The returned exception uses a 401 Unauthorized status and includes the appropriate WWW-Authenticate header for Bearer tokens.

    Returns:
        HTTPException: An exception configured for invalid token type submissions.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token should be refresh token only.",
        headers={"WWW-Authenticate": "Bearer"},
    )

def black_listed_token_exception():
    """Creates an HTTP exception for attempts to use a blacklisted token. This helper standardizes the response when a token has been revoked and must not be honored.

    The returned exception uses a 401 Unauthorized status and includes the appropriate WWW-Authenticate header for Bearer tokens.

    Returns:
        HTTPException: An exception configured for blacklisted token usage.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token is black listed and can't be used.",
        headers={"WWW-Authenticate": "Bearer"},
    )