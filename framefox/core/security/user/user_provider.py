import logging
from typing import Any, Dict, Optional, Type, TypeVar

from framefox.core.request.session.session_interface import SessionInterface
from framefox.core.security.token_storage import TokenStorage
from framefox.core.security.user.entity_user_provider import EntityUserProvider

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""

T = TypeVar("T")


class UserProvider:
    """
    Provides methods to retrieve the currently authenticated user.
    This class centralizes the logic for retrieving the user from
    the token or session cache.
    """

    def __init__(
        self,
        token_storage: TokenStorage,
        session: SessionInterface,
        entity_user_provider: EntityUserProvider,
    ):
        self.token_storage = token_storage
        self.session = session
        self.entity_user_provider = entity_user_provider
        self.logger = logging.getLogger("USER_PROVIDER")

    def get_current_user(self, user_class: Type[T] = None) -> Optional[T]:
        """
        Retrieves the currently authenticated user.

        Args:
            user_class (Type[T], optional): The expected user class type.
                If None, returns the user as stored in the token.

        Returns:
            Optional[T]: The user object if authenticated, otherwise None.
        """

        user_id_cache = self.session.get("_current_user_id")
        if user_id_cache:

            firewall_name = "main"
            provider_info = self.entity_user_provider.get_repository_and_property(
                firewall_name
            )

            if provider_info:
                repository, _ = provider_info
                user = repository.find(user_id_cache)
                if user:
                    return user

        payload = self.token_storage.get_payload()
        if not payload:
            self.logger.warning("No valid authentication token")
            return None

        user_id = payload.get("sub")

        firewall_name = payload.get("firewallname", "main")
        if firewall_name.startswith("/"):
            self.logger.debug(f"Convert path {firewall_name} to firewall name 'main'")
            firewall_name = "main"

        if not user_id:
            return None

        provider_info = self.entity_user_provider.get_repository_and_property(
            firewall_name
        )

        if not provider_info:
            self.logger.warning(f"No provider found for firewall '{firewall_name}'")
            return None
        repository, _ = provider_info
        user = repository.find(user_id)
        if user:
            self.session.set("_current_user_id", user_id)
            self.session.save()
            self.logger.debug(f"User {user_id} cached")
        else:
            self.logger.warning(f"User with ID {user_id} not found in repository")

        return user
