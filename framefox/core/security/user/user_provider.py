import logging
from typing import Optional, Type, TypeVar

from framefox.core.di.service_container import ServiceContainer

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

    def __init__(self):
        self.container = ServiceContainer()
        self.token_storage = self.container.get_by_name("TokenStorage")
        self.session = self.container.get_by_name("Session")
        self.entity_user_provider = self.container.get_by_name("EntityUserProvider")
        self.logger = logging.getLogger("USER_PROVIDER")

    def get_current_user(self, user_class: Type[T] = None) -> Optional[T]:
        """
        Retrieves the currently authenticated user.
        """
        # SUPPRIMÉ : Tentative d'accès au request scope qui ne fonctionne pas
        # L'utilisateur JWT sera géré directement par l'authorization dans le firewall
        
        # Logique existante pour les autres types d'auth (avec session)
        user_id_cache = self.session.get("user_id")
        if user_id_cache:
            # Vérifier si c'est un utilisateur virtuel OAuth
            if str(user_id_cache).startswith("oauth_"):
                self.logger.debug(f"Virtual OAuth user found in session: {user_id_cache}")
                # Reconstruire l'utilisateur virtuel depuis le token
                payload = self.token_storage.get_payload()
                if payload:
                    return self._create_virtual_user_from_payload(payload)
            
            # Essayer avec le firewall principal d'abord
            firewall_name = "main"
            provider_info = self.entity_user_provider.get_repository_and_property(firewall_name)

            if provider_info:
                repository, _ = provider_info
                user = repository.find(user_id_cache)
                if user:
                    self.logger.debug(f"User found in session cache: {user_id_cache}")
                    return user
            
            # Si pas trouvé, essayer avec d'autres firewalls (comme oauth)
            settings = self.entity_user_provider.settings
            for fw_name in settings.firewalls.keys():
                if fw_name != firewall_name:
                    provider_info = self.entity_user_provider.get_repository_and_property(fw_name)
                    if provider_info:
                        repository, _ = provider_info
                        user = repository.find(user_id_cache)
                        if user:
                            self.logger.debug(f"User found in session cache with firewall '{fw_name}': {user_id_cache}")
                            return user

        payload = self.token_storage.get_payload()
        if not payload:
            self.logger.debug("No token payload found")
            return None

        user_id = payload.get("sub")

        firewall_name = payload.get("firewallname", "main")
        if firewall_name.startswith("/"):
            self.logger.debug(f"Convert path {firewall_name} to firewall name 'main'")
            firewall_name = "main"

        if not user_id:
            self.logger.debug("No user_id in token payload")
            return None

        # Vérifier si c'est un utilisateur virtuel OAuth
        if str(user_id).startswith("oauth_"):
            self.logger.debug(f"Virtual OAuth user detected: {user_id}")
            virtual_user = self._create_virtual_user_from_payload(payload)
            if virtual_user:
                self.session.set("user_id", user_id)
                self.session.save()
                self.logger.debug(f"Virtual user {user_id} cached from token")
            return virtual_user

        provider_info = self.entity_user_provider.get_repository_and_property(firewall_name)

        if not provider_info:
            self.logger.warning(f"No provider found for firewall '{firewall_name}'")
            return None
        repository, _ = provider_info
        user = repository.find(user_id)
        if user:
            self.session.set("user_id", user_id)
            self.session.save()
            self.logger.debug(f"User {user_id} cached from token")
        else:
            self.logger.warning(f"User with ID {user_id} not found in repository")

        return user

    def _create_virtual_user_from_payload(self, payload: dict):
        """
        Recrée un utilisateur virtuel depuis le payload du token
        """
        from types import SimpleNamespace
        
        virtual_user = SimpleNamespace()
        virtual_user.id = payload.get("sub")
        virtual_user.email = payload.get("email")
        virtual_user.name = virtual_user.email.split('@')[0] if virtual_user.email else "OAuth User"
        virtual_user.roles = payload.get("roles", ["ROLE_USER"])
        virtual_user.provider = "oauth"
        virtual_user.is_virtual = True
        
        return virtual_user