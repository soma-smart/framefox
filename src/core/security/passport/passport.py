from typing import Optional

from src.core.security.passport.user_badge import UserBadge
from src.core.security.passport.password_credentials import PasswordCredentials
from src.core.security.passport.csrf_token_badge import CsrfTokenBadge

from src.entity.user import User
from src.repository.user_repository import UserRepository


class Passport:
    """
    A class to handle user authentication and CSRF token validation.

    Attributes:
        user_badge (UserBadge): An instance of UserBadge to identify the user.
        password_credentials (PasswordCredentials): An instance of PasswordCredentials to verify the user's password.
        csrf_token_badge (Optional[CsrfTokenBadge]): An optional instance of CsrfTokenBadge for CSRF protection.
        user (Optional[User]): The authenticated user, if authentication is successful.

    Methods:
        authenticate_user(user_repository: UserRepository) -> bool:
            Asynchronously authenticates the user using the provided user repository.
    """

    def __init__(
        self,
        user_badge: UserBadge,
        password_credentials: PasswordCredentials,
        csrf_token_badge: Optional[CsrfTokenBadge] = None,
    ):
        self.user_badge = user_badge
        self.password_credentials = password_credentials
        self.csrf_token_badge = csrf_token_badge
        self.user: Optional[User] = None

    async def authenticate_user(self, user_repository: UserRepository) -> bool:
        self.user = await self.user_badge.get_user(user_repository)
        if not self.user:
            return False
        return self.password_credentials.verify(self.user.password)
