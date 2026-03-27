from pydantic import BaseModel

class TokenData(BaseModel):
    """Represents the identity information extracted from an authentication token. This model captures the essential fields needed to identify a user from token payloads.

    The token data is typically derived from decoded JWTs and is used to authorize user actions throughout the system.

    Attributes:
        id: The unique identifier associated with the authenticated user.
        email: The email address linked to the authenticated user.
    """
    id: str
    email: str

    class Config:
        """Pydantic configuration for the TokenData model. This configuration controls how token data objects are instantiated from underlying sources.

        The current setup enables populating the model directly from ORM-like objects that expose attributes.

        Attributes:
            from_attributes: Allows the model to be created from attribute-based objects instead of only dictionaries.
        """
        from_attributes = True

class BlackListData(BaseModel):
    """Represents tokens and user information associated with a blacklisted session. This model is used to track tokens that should no longer be accepted for authentication.

    The blacklist data helps enforce security policies by invalidating compromised or expired tokens.

    Attributes:
        access_token: The access token that has been blacklisted and should be rejected.
        refresh_token: The refresh token tied to the blacklisted session, also considered invalid.
        user_id: The unique identifier of the user whose tokens have been blacklisted.
    """
    access_token: str
    refresh_token: str
    user_id: str

    class Config:
        """Pydantic configuration for the BlackListData model. This configuration defines how blacklist entries can be instantiated from different data sources.

        The current setup allows creating blacklist entries from objects that expose attributes instead of plain dictionaries.

        Attributes:
            from_attributes: Enables model population from attribute-based sources such as ORM instances.
        """
        from_attributes = True

