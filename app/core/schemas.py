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
    access_token: str
    refresh_token: str

    class Config:
        from_attributes = True

