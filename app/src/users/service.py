"""User related business logics"""

import secrets
import string
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.security import hash_password
from app.src.users.models import User
from app.src.users.schemas import UserCreate

RANDOM_PASSWORD_LENGTH=12

async def commit_to_db(db: AsyncSession, model_instance: User):
    """Persist a user model instance to the database and synchronize its state. This helper encapsulates the common pattern of adding, committing, and refreshing a user record.

    The function attaches the given model instance to the session, commits the transaction, and refreshes the instance so it reflects any database-generated values.

    Args:
        db: The active database AsyncSession used to persist the model instance.
        model_instance: The user model instance that should be saved and refreshed.

    Returns:
        None: This function performs database side effects and does not return a value.
    """
    db.add(model_instance)
    await db.commit()
    await db.refresh(model_instance)

async def check_user_oauth(db: AsyncSession, new_user: User):
    """Look up an existing user created via OAuth by their email address.

    This function searches the database for a user whose email matches the
    provided user instance and returns the first match if found.

    Args:
        db: The active database AsyncSession used to perform the lookup.
        new_user: The user instance whose email will be used for the search.

    Returns:
        User | None: The matching user if one exists, otherwise ``None``.
    """
    return (await db.scalars(select(User).where(User.email == new_user.email))).first()

async def check_user_email(db: AsyncSession, new_user: User):
    """Ensure that a user's email address is unique before creating or updating a record.

    This function checks for an existing user with the same email and prevents
    duplicates by raising an HTTP 403 error if a conflict is found.

    Args:
        db: The active database AsyncSession used to perform the lookup.
        new_user: The user instance whose email should be validated for uniqueness.

    Raises:
        HTTPException: Raised with a 403 status code if a user with the same email
            already exists in the database.
    """
    user_email = (await db.scalars(select(User).where(User.email == new_user.email))).first()
    if user_email is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{new_user.email} already exists.")
    
async def check_user_name(db: AsyncSession, new_user: User):
    """Ensure that a user's username is unique before creating or updating a record. This function prevents duplicate usernames by validating against existing records.

    The function queries the database for a user with the same username and raises an HTTP 403 error if a conflict is detected.

    Args:
        db: The active database AsyncSession used to perform the lookup.
        new_user: The user instance whose username should be validated for uniqueness.

    Raises:
        HTTPException: Raised with a 403 status code if a user with the same username
            already exists in the database.
    """
    user_name = (await db.scalars(select(User).where(User.username == new_user.username))).first()
    if user_name is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{new_user.username} already exists.")
    


async def check_user_id(db: AsyncSession, new_user: User):
    """Verify that a user's ID is unique before persisting or updating their record.

    This function checks for an existing user with the same ID and prevents
    duplicates by raising an HTTP 403 error if a conflict is found.

    Args:
        db: The active database AsyncSession used to perform the lookup.
        new_user: The user instance whose ID should be validated for uniqueness.

    Raises:
        HTTPException: Raised with a 403 status code if a user with the same ID
            already exists in the database.
    """
    user_id = (await db.scalars(select(User).where(User.id == new_user.id))).first()
    if user_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{new_user.id} already exists.")
    
def generate_random_passwords(password_range: int) -> str:
    """Generate a random password string of the requested length. This helper uses a mix of letters, digits, and punctuation to create high-entropy passwords.

    The function randomly selects characters from the combined alphabet until the specified length is reached.

    Args:
        password_range: The desired length of the generated password.

    Returns:
        str: A randomly generated password string of the requested length.
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(password_range))

def get_user_data_from_oauth(data: dict) -> UserCreate:
    """Build a user creation payload from OAuth provider profile data. This function normalizes external OAuth fields into the internal UserCreate schema.

    The function extracts core identity attributes such as email, display name, and profile image, while generating a secure random password for the new user.

    Args:
        data: The raw profile data dictionary returned by an OAuth provider.

    Returns:
        UserCreate: A populated user creation schema derived from the OAuth profile.
    """
    return UserCreate(
        email=data["email"],
        username=data["name"] or data["login"],
        password=hash_password(generate_random_passwords(int(RANDOM_PASSWORD_LENGTH))),
        profile_picture=data.get("picture") or data.get("avatar_url")
    )

async def create_user_oauth(db: AsyncSession, user: UserCreate):
    """Create or retrieve a user based on OAuth-derived profile data. This function ensures that OAuth logins map to a single, active user record per email address.

    The function builds a User model from the provided data, checks for an existing user with the same email, and either returns the existing user or persists a new active user.

    Args:
        db: The active database AsyncSession used to query and persist user records.
        user: The validated user creation payload constructed from OAuth profile data.

    Returns:
        User: The existing user if one was found, otherwise the newly created active user.
    """
    new_user = User(**user.model_dump())
    new_user.is_active = True
    user = await check_user_oauth(db,new_user)
    if not user:
        await commit_to_db(db,new_user)
        return new_user
    return user

async def get_user_data(data: dict) -> UserCreate:
    """Build a user creation payload from raw registration data. This helper normalizes input fields into the internal UserCreate schema used for persistence.

    The function extracts the core identity attributes and hashes the provided plain-text password before constructing the schema.

    Args:
        data: The raw registration data dictionary containing email, username, and password keys.

    Returns:
        UserCreate: A populated user creation schema ready to be stored in the database.
    """
    return UserCreate(
        email=data["email"],
        username=data["username"],
        password=hash_password(data["password"])
    )


async def create_user(db: AsyncSession, user: UserCreate):
    """Create a new user from validated registration data. This function enforces uniqueness checks and persists the user to the database.

    The function constructs a User model instance, verifies that both email and ID are not already in use, and then commits the new record.

    Args:
        db: The active database AsyncSession used to query and persist user records.
        user: The validated user creation payload containing registration details.

    Returns:
        None: This function performs database side effects and does not return a value.

    Raises:
        HTTPException: If a user with the same email or ID already exists.
    """
    new_user = User(**user.model_dump())
    await check_user_email(db,new_user)
    await check_user_id(db,new_user)
    await check_user_name(db, new_user)
    await commit_to_db(db,new_user)
