from typing import Optional, List, Dict
import logging

from framefox.core.security.passport.user_badge import UserBadge
from framefox.core.security.passport.password_credentials import PasswordCredentials
from framefox.core.security.passport.csrf_token_badge import CsrfTokenBadge

from src.entity.user import User


class Passport:
    """
    A class to handle user authentication and CSRF token validation.

    Attributes:
        user_badge (UserBadge): An instance of UserBadge to identify the user.
        password_credentials (PasswordCredentials): An instance of PasswordCredentials to verify the user's password.
        csrf_token_badge (Optional[CsrfTokenBadge]): An optional instance of CsrfTokenBadge for CSRF protection.
        user (Optional[User]): The authenticated user, if authentication is successful.
        provider_info (Optional[Dict]): Informations du provider, incluant repository et propriété d'identification.
    """

    def __init__(
        self,
        user_badge: UserBadge = None,
        password_credentials: PasswordCredentials = None,
        csrf_token_badge: Optional[CsrfTokenBadge] = None,
        provider_info: Optional[Dict] = None,
    ):
        self.user_badge = user_badge
        self.password_credentials = password_credentials
        self.csrf_token_badge = csrf_token_badge
        self.user: Optional[User] = None
        self.roles: List[str] = []
        self.provider_info = provider_info
        self.logger = logging.getLogger("PASSPORT")

    async def authenticate_user(self) -> bool:
        if self.user:
            self.logger.debug("User directly set, no database query needed.")
            self.roles = self.user.roles
            return True

        if not self.user_badge:
            self.logger.debug("No user_badge provided and no user set.")
            return False

        if self.provider_info:

            repository = self.provider_info.get("repository")
            property_name = self.provider_info.get("property")
            if repository and property_name:
                self.user_badge.user_identifier_property = property_name
                user = await self.user_badge.get_user(repository)
                if user:
                    self.user = user
        else:

            self.logger.warning(
                "No provider info available, cannot authenticate user.")
            return False

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
        self.logger.debug(f"User authenticated with roles: {self.roles}")
        return True
