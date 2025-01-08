from typing import Optional, List
import logging
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
        self.roles: List[str] = []
        self.logger = logging.getLogger("PASSPORT")

    async def authenticate_user(self) -> bool:
        if self.user:
            self.logger.debug(
                "User directly set, no database query needed.")
            self.roles = self.user.roles
            return True

        if not self.user_badge:
            self.logger.debug(
                "No user_badge provided and no user set.")
            return False

        user_repository = UserRepository()
        self.user = await self.user_badge.get_user(user_repository)
        if not self.user:
            self.logger.warning("User not found in the database.")
            return False

        if self.password_credentials:
            authenticated = self.password_credentials.verify(
                self.user.password)
            if not authenticated:
                self.logger.warning("Password verification failed.")
                return False

        self.roles = self.user.roles
        self.logger.debug(
            f"User authenticated with roles: {self.roles}")
        return True
