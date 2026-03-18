"""Pydantic schema for authentications"""

from pydantic import BaseModel


class GoogleAuthCode(BaseModel):
    """Represents the payload containing a Google OAuth authorization code. This model is used to validate incoming login requests before processing authentication.

    The code encapsulates the short-lived token returned by Google's OAuth consent screen and is required to exchange for user credentials.

    Attributes:
        code: The authorization code obtained from Google's OAuth flow.
    """
    code: str
    class Config:
        """Pydantic configuration for the GoogleAuthCode model. This configuration controls how data is populated and serialized for this schema.

        The current setup allows instances to be created from ORM objects by reading attributes directly.

        Attributes:
            from_attributes: Enables population of the model from object attributes instead of only from dict-like structures.
        """
        from_attributes = True