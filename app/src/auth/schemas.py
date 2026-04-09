"""Pydantic schema for authentications"""

import string
from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator, model_validator

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

class GithubAuthCode(BaseModel):
    """Represents the payload containing a GitHub OAuth authorization code. This model is used to validate incoming GitHub login requests before starting authentication.

    The code encapsulates the short-lived token returned by GitHub's OAuth flow and is required to exchange for an access token.

    Attributes:
        code: The authorization code obtained from GitHub's OAuth process.
    """
    code: str
    class Config:
        """Pydantic configuration for the GithubAuthCode model. This configuration controls how data is populated and serialized for this schema.

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
    user: UserPayload
    class Config:
        """Pydantic configuration for the GoogleLoginResponseOut model. This configuration defines how the response model can be populated from underlying data objects.

        The current setup enables constructing the response from ORM-like objects by reading their attributes directly.

        Attributes:
            from_attributes: Allows population of the model from object attributes instead of only dictionaries.
        """
        from_attributes = True

class GithubLoginResponseOut(BaseModel):
    """Defines the response structure returned after a successful GitHub login. This model bundles issued tokens with the authenticated user's core identity payload.

    The response is designed to be sent to clients so they can store the access token and understand which user it represents.

    Attributes:
        access_token: The JWT or token string granting access to protected resources.
        refresh_token: A token string that can be used to obtain a new access token, if implemented.
        user: The minimal user identity information associated with the authenticated session.
    """
    access_token: str
    refresh_token: str
    user: UserPayload
    class Config:
        """Pydantic configuration for the GithubLoginResponseOut model. This configuration defines how the response model can be populated from underlying data objects.

        The current setup enables constructing the response from ORM-like objects by reading their attributes directly.

        Attributes:
            from_attributes: Allows population of the model from object attributes instead of only dictionaries.
        """
        from_attributes = True

class RegisterUser(BaseModel):
    """Defines the payload required to register a new user account. This model enforces basic email and password rules before user creation.

    The schema ensures that passwords meet minimum complexity requirements and that the confirmation password matches the original.

    Attributes:
        email: The email address that will be associated with the new user account.
        username: The display name or handle chosen by the user.
        password: The primary password used for authentication, subject to complexity validation.
        confirm_password: A repeated password value that must match the primary password.
    """
    email: EmailStr
    username: str
    password: SecretStr = Field(min_length=8, max_length=30)
    confirm_password: SecretStr = Field(min_length=8, max_length=30)

    @classmethod
    def password_type_checker(cls, password: str) -> None:
        """Validates that a password string meets basic complexity requirements. This helper checks for the presence of digits, letter casing, and special characters.

        The method raises a ValueError with a descriptive message when the supplied password does not satisfy any of the enforced rules.

        Args:
            password: The plain-text password string submitted by the user.

        Raises:
            ValueError: If the password lacks digits, lowercase letters, uppercase letters, or special characters.
        """
        if not any(pw.isdigit() for pw in password):
            raise ValueError('Password must contain at least one digit')
        if not any(pw.islower() for pw in password):
            raise ValueError('Password must contain at least one lower case')
        if not any(pw.isupper() for pw in password):
            raise ValueError('Password must contain at least one uppercase')
        if all(pw not in string.punctuation for pw in password):
            raise ValueError('Password must contain at least one special character')

    @field_validator("password")
    @classmethod
    def password_validation(cls, password: SecretStr) -> SecretStr:
        """Applies server-side validation rules to a submitted password field. This validator ensures that any password assigned to the model satisfies the configured complexity checks.

        The method delegates to the shared password_type_checker helper and returns the original SecretStr value if validation succeeds.

        Args:
            password: The secret password value provided in the registration payload.

        Returns:
            SecretStr: The same password value, returned after successful validation.

        Raises:
            ValueError: If the password does not meet the required complexity constraints.
        """
        get_password = password.get_secret_value()
        RegisterUser.password_type_checker(get_password)
        return password
    
    @model_validator(mode='after')
    def check_passwords_match(self) -> 'RegisterUser':
        """Ensures that the password and confirmation password fields contain the same value. This validator runs after field-level validation to enforce consistency between related fields.

        If the two password fields disagree, the method raises a validation error to prevent creation of an inconsistent registration payload.

        Returns:
            RegisterUser: The validated model instance when both passwords match successfully.

        Raises:
            ValueError: If the password and confirm_password values are not identical.
        """
        password_value: str = self.password.get_secret_value()
        confirm_password_value: str = self.confirm_password.get_secret_value()
        if password_value != confirm_password_value:
            raise ValueError('The password and confirm password did not match')
        return self
    class Config:
        """Pydantic configuration for the RegisterUser model. This configuration defines how registration payloads can be populated from underlying data objects.

        The current setup enables constructing the registration schema from ORM-like objects by reading their attributes directly.

        Attributes:
            from_attributes: Allows population of the model from object attributes instead of only dictionaries.
        """
        from_attributes = True

class ShowStatus(BaseModel):
    """Represents a simple status message payload used in authentication responses. This model provides a lightweight way to convey human-readable outcome messages to clients.

    The schema is typically wrapped inside higher-level response objects to indicate success or failure of an operation.

    Attributes:
        msg: The human-readable status or informational message to be returned to the client.
    """
    msg: str
class RegisterUserResponseOut(BaseModel):
    """Defines the response structure returned after a successful user registration. This model wraps a simple status payload to communicate the outcome of the registration process.

    The response is intended to provide clients with a clear, human-readable confirmation message rather than exposing full user details.

    Attributes:
        data: The status payload containing a message about the registration result.
    """
    data: ShowStatus
    class Config:
        """Pydantic configuration for the RegisterUserResponseOut model. This configuration specifies how response objects are created from underlying data sources.

        The current setup enables constructing the response from ORM-like objects by reading their attributes directly.

        Attributes:
            from_attributes: Allows population of the model from object attributes instead of only dictionaries.
        """
        from_attributes = True

class ResponseTokenOut(BaseModel):
    """Represents the token pair returned when refreshing or issuing authentication tokens. This model provides a consistent structure for delivering new access tokens and optional refresh tokens to clients.

    The schema is typically used in responses from token refresh endpoints or other authentication flows.

    Attributes:
        access_token: The JWT or token string granting access to protected resources.
        refresh_token: The token string that can be used to obtain a new access token, if provided.
    """
    access_token: str
    refresh_token: str

    class Config:
        """Pydantic configuration for the ResponseTokenOut model. This configuration determines how token response objects are built from underlying data sources.

        The current setup enables constructing the response from ORM-like objects by reading their attributes directly.

        Attributes:
            from_attributes: Allows population of the model from object attributes instead of only dictionaries.
        """
        from_attributes = True