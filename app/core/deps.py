from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import SessionLocal
from app.core.security import verify_token
from app.src.users.models import User


async def get_db():
    """Provide an asynchronous database session for use within a request lifecycle.

    This function yields a database session and ensures that any errors cause a rollback
    before the exception is re-raised.

    Yields:
        AsyncSession: An active asynchronous database session.
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
async def fetch_user(db: AsyncSession, token: str):
    """Fetch a user based on the provided access token. 

    This function validates the token and retrieves the user whose identity matches
    the information encoded in the token.

    Args:
        db: The database session used to query the user.
        token: The access token containing user identification data.

    Returns:
        User | None: The user matching the token data, or None if no user is found.
    """
    token_data = verify_token(token)
    user_query = (
        select(User)
        .where(User.id == token_data.id)
        .where(User.email == token_data.email)
    )
    result = await db.scalars(user_query)
    return result.first()



async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
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
    user = await fetch_user(db, str(token))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    return user