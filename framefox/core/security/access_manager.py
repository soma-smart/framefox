import logging
import re
from typing import List

from framefox.core.config.settings import Settings
from framefox.core.request.static_resource_detector import StaticResourceDetector

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class AccessManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger("FIREWALL")

    def get_required_roles(self, path: str) -> List[str]:
        """
        Retrieves the required roles for a specific path from the settings.
        """
        is_static_resource = StaticResourceDetector.is_static_resource(path)
        if not is_static_resource:
            self.logger.debug(f"Evaluating required roles for path: {path}")

        if not self.settings.access_control:
            if not is_static_resource:
                self.logger.debug("No access control rules defined.")
            return []

        for rule in self.settings.access_control:
            pattern = rule.get("path")
            roles = rule.get("roles", [])
            if isinstance(roles, str):
                roles = [roles]

            if re.match(pattern, path):
                if not is_static_resource:
                    self.logger.debug(f"Path {path} matches pattern {pattern} with roles {roles}")
                return roles
        
        # NOUVEAU: Vérifier la politique par défaut depuis la configuration
        default_policy = self.settings.config.get("security", {}).get("default_access_policy", "allow")
        
        if not is_static_resource:
            self.logger.debug(f"No access control rule matched for path: {path} - applying default policy: {default_policy}")
        
        if default_policy == "deny":
            return ["ROLE_ADMIN"]  # Deny by default
        else:
            return []  # Allow by default

    def is_allowed(self, user_roles: List[str], required_roles: List[str]) -> bool:
        """
        Checks if the user has at least one of the required roles.
        Special handling for IS_AUTHENTICATED_ANONYMOUSLY.
        """
        # NOUVEAU: Gestion spéciale pour IS_AUTHENTICATED_ANONYMOUSLY
        if "IS_AUTHENTICATED_ANONYMOUSLY" in required_roles:
            self.logger.debug("Route accessible anonymously - access granted")
            return True
        
        # Si pas de rôles requis, autoriser (pour compatibilité)
        if not required_roles:
            self.logger.debug("No roles required - access granted")
            return True
        
        # Vérification classique des rôles utilisateur
        if not user_roles:
            self.logger.debug("User has no roles - access denied")
            return False
        
        has_role = any(role in user_roles for role in required_roles)
        self.logger.debug(
            f"User roles: {user_roles}, Required roles: {required_roles}"
        )
        self.logger.debug(
            f"The user {'has' if has_role else 'does not have'} the required roles."
        )
        return has_role