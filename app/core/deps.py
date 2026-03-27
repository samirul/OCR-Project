from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
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

def fetch_user(db: Session, token: str):
    """Fetch a user from the database using data extracted from an access token.

    This function validates the provided token, derives identifying user information,
    and retrieves the corresponding user record if it exists.

    Args:
        db: The database session used to execute the user lookup.
        token: The encoded access token containing user identification data.

    Returns:
        User | None: The matching user instance if found, otherwise None.
    """
    token_data = verify_token(token)
    user_query = (
        select(User)
        .where(User.id == token_data.id)
        .where(User.email == token_data.email)
    )
    return db.scalars(user_query).first()



def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Retrieve the currently authenticated user based on the access token cookie.

    This function extracts the access token from the incoming request cookies, validates
    it, and loads the corresponding user from the database or raises an authorization error.

    Args:
        request: The incoming HTTP request containing the access token cookie.
        db: The database session used to query the user.

    Returns:
        User: The authenticated user associated with the provided access token.

    Raises:
        HTTPException: If the token is missing, invalid, or the user cannot be found.
    """
    token = request.cookies.get("access_token")
    user = fetch_user(db, str(token))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    return user