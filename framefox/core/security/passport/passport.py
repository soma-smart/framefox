import logging
from typing import Dict, List, Optional

from framefox.core.security.passport.csrf_token_badge import CsrfTokenBadge
from framefox.core.security.passport.password_credentials import PasswordCredentials
from framefox.core.security.passport.user_badge import UserBadge
from framefox.core.security.password.password_hasher import PasswordHasher

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


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
        user_badge: UserBadge,
        password_credentials: Optional[PasswordCredentials] = None,
        csrf_token_badge: Optional[CsrfTokenBadge] = None,
        provider_info=None,
    ):
        self.user_badge = user_badge
        self.password_credentials = password_credentials
        self.csrf_token_badge = (csrf_token_badge,) if csrf_token_badge else None
        self.user = None
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
                    # NOUVEAU: Essayer de créer l'utilisateur via la méthode personnalisable de l'authenticator
                    if not self.password_credentials and hasattr(self, '_oauth_authenticator'):  # C'est un utilisateur OAuth
                        self.logger.info(f"User not found, attempting OAuth user creation: {self.user_badge.user_identifier}")
                        # Récupérer les données utilisateur depuis l'authenticator
                        user_data = getattr(self, '_oauth_user_data', {})
                        user = await self._oauth_authenticator.create_oauth_user(user_data, repository)
                        if user:
                            self.user = user
                            self.logger.info(f"OAuth user created successfully: {self.user_badge.user_identifier}")
                        else:
                            self.logger.debug(f"No OAuth user creation implemented for: {self.user_badge.user_identifier}")
        else:
            # NOUVEAU: Pas de provider configuré - créer un utilisateur virtuel OAuth
            if not self.password_credentials:  # C'est une authentification OAuth sans provider
                self.logger.info(f"Creating virtual OAuth user (no provider configured): {self.user_badge.user_identifier}")
                # Récupérer les rôles par défaut depuis l'authenticator OAuth
                default_roles = ["ROLE_USER"]
                if hasattr(self, '_oauth_authenticator'):
                    default_roles = getattr(self._oauth_authenticator, 'default_roles', default_roles)
                
                self.user = self._create_virtual_oauth_user(default_roles)
            else:
                self.logger.warning("No provider info available, cannot authenticate user.")
                return False

        if not self.user:
            self.logger.warning("User not found in the database.")
            return False

        # Vérification du mot de passe seulement s'il y a des credentials (pas pour OAuth)
        if self.password_credentials:
            password_hasher = PasswordHasher()
            authenticated = password_hasher.verify(self.password_credentials.raw_password, self.user.password)
            if not authenticated:
                self.logger.warning("Password verification failed.")
                return False

        self.roles = self.user.roles
        self.logger.debug(f"User authenticated with roles: {self.roles}")
        return True

    def _create_virtual_oauth_user(self, default_roles: list = None):
        """
        Crée un utilisateur virtuel pour OAuth quand aucun provider n'est configuré
        """
        from types import SimpleNamespace
        
        if default_roles is None:
            default_roles = ["ROLE_USER"]
        
        # Créer un objet utilisateur simple sans base de données
        virtual_user = SimpleNamespace()
        virtual_user.id = f"oauth_{hash(self.user_badge.user_identifier)}"  # ID unique basé sur l'email
        virtual_user.email = self.user_badge.user_identifier
        virtual_user.name = self.user_badge.user_identifier.split('@')[0]  # Nom par défaut
        virtual_user.roles = default_roles  # Utiliser les rôles configurés
        virtual_user.provider = "oauth"
        virtual_user.is_virtual = True  # Marquer comme utilisateur virtuel
        
        self.logger.info(f"Virtual OAuth user created: {virtual_user.email} with roles {virtual_user.roles}")
        return virtual_user

    # Supprimer l'ancienne méthode _create_oauth_user car elle sera dans l'authenticator
