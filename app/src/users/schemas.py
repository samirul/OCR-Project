from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    """Represent a user within the application domain.

    This model defines the core user attributes used for identification and profile
    representation across the system.

    Attributes:
        email: The user's email address used for identification and communication.
        username: The display name chosen by the user.
        profile_picture: An optional URL or path to the user's profile image.
    """
    email: str
    username: str
    profile_picture: Optional[str] = None

    class Config:
        """Pydantic configuration for the User model.

        This configuration enables population of the model from ORM objects by
        reading attributes directly from database model instances.
        """
        from_attributes = True

class UserCreate(User):
    """Represent the data required to create a new user.

    This model extends the base User schema and is used specifically for user
    creation operations within the system.
    """
