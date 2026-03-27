from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.src.users.models import User
from app.src.users.schemas import UserCreate


def commit_to_db(db: Session, model_instance: User):
    """Persist a model instance to the database within the current session.

    This function adds the instance to the session, commits the transaction, and
    refreshes the instance with any changes made by the database.

    Args:
        db: The active database session used for persistence operations.
        model_instance: The user model instance to be saved and refreshed.
    """
    db.add(model_instance)
    db.commit()
    db.refresh(model_instance)

def check_user_oauth(db: Session, new_user: User):
    """Look up an existing user by email for OAuth-based authentication.

    This helper checks whether a user with the given email already exists and
    returns the matching user instance if found.

    Args:
        db: The active database session used to query user records.
        new_user: The user instance whose email is used for the lookup.

    Returns:
        User | None: The existing user with the same email, or None if no match is found.
    """
    return db.scalars(select(User).where(User.email == new_user.email)).first()

def check_user(db: Session, new_user: User):
    """Ensure that a user's email address is unique before creation.

    This function queries the database for an existing user with the same email
    and blocks the operation if a duplicate is found.

    Args:
        db: The active database session used to perform the lookup.
        new_user: The user instance whose email should be validated for uniqueness.

    Raises:
        HTTPException: Raised with a 403 status code if a user with the same email
            already exists in the database.
    """
    user = db.scalars(select(User).where(User.email == new_user.email)).first()
    if user is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{new_user.email} already exists.")


def check_user_id(db: Session, new_user: User):
    """Validate that a user ID is unique before creating a new user.

    This function checks the database for an existing user with the same ID and
    blocks creation if a conflict is found.

    Args:
        db: The active database session used to perform the lookup.
        new_user: The user instance whose ID should be validated for uniqueness.

    Raises:
        HTTPException: Raised with a 403 status code if a user with the same ID
            already exists in the database.
    """
    user_id = db.scalars(select(User).where(User.id == new_user.id)).first()
    if user_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{new_user.id} already exists.")
    

def get_user_data_from_oauth_google(data: dict) -> UserCreate:
    """Transform raw Google OAuth user data into a UserCreate schema.

    This function extracts the relevant user fields from the OAuth payload and
    maps them into the internal user creation model.

    Args:
        data: The dictionary containing user information returned by Google OAuth.

    Returns:
        UserCreate: A populated user creation schema built from the OAuth data.
    """
    return UserCreate(
        email=data["email"],
        username=data["name"],
        profile_picture=data["picture"]
    )

async def create_user_oauth(db: Session, user: UserCreate):
    """Create or retrieve a user based on Google OAuth data.

    This function ensures that a user backed by Google OAuth exists by
    either returning an existing record or creating a new active user.

    Args:
        user: The user creation schema populated from Google OAuth data.
        db: The active database session used to query and persist user records.

    Returns:
        User: The existing or newly created user associated with the OAuth data.
    """
    new_user = User(**user.model_dump())
    new_user.is_active = True
    user = check_user_oauth(db,new_user)
    if not user:
        commit_to_db(db,new_user)
        return new_user
    return user