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

class UserPayload(BaseModel):
    """Represents the minimal user identity information carried in authentication payloads. This model captures the core fields needed to identify and contact a user.

    The payload is typically embedded in tokens or response objects to propagate user identity across the system.

    Attributes:
        id: The unique identifier of the user.
        email: The email address associated with the user account.
    """
    id: str
    email: str

class GoogleLoginResponseOut(BaseModel):
    """Defines the response structure returned after a successful Google login. This model bundles issued tokens with the authenticated user's core identity payload.

    The response is designed to be sent to clients so they can store the access token and understand which user it represents.

    Attributes:
        access_token: The JWT or token string granting access to protected resources.
        refresh_token: A token string that can be used to obtain a new access token, if implemented.
        payload: The minimal user identity information associated with the authenticated session.
    """
    access_token: str
    refresh_token: str
    payload: UserPayload
    class Config:
        """Pydantic configuration for the GoogleLoginResponseOut model. This configuration defines how the response model can be populated from underlying data objects.

        The current setup enables constructing the response from ORM-like objects by reading their attributes directly.

        Attributes:
            from_attributes: Allows population of the model from object attributes instead of only dictionaries.
        """
        from_attributes = True