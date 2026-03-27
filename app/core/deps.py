from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import verify_token
from app.src.users.models import User


def get_db():
    """Provide a transactional database session for request handling.

    This function creates a new SQLAlchemy SessionLocal instance, yields it for use, and
    ensures that the session is properly closed after the calling context is finished.

    Yields:
        Session: A SQLAlchemy session bound to the configured database engine.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Retrieves the currently authenticated user based on the access token cookie. This dependency ensures that only valid, known users can access protected endpoints.

    The function reads the access token from the request cookies, validates it, looks up the corresponding user in the database, and raises an unauthorized error if validation fails.

    Args:
        request: The incoming HTTP request containing the access token cookie.
        db: The database session used to query the user table.

    Returns:
        User: The authenticated user associated with the provided access token.

    Raises:
        HTTPException: If the token is invalid or no matching user is found.
    """
    token = request.cookies.get("access_token")
    token_data = verify_token(str(token))
    user = db.query(User).filter(User.id == token_data.id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    return user