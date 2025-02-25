import logging
import re
from typing import List

from framefox.core.config.settings import Settings

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
        self.logger.debug(f"Evaluating required roles for path: {path}")
        for rule in self.settings.access_control:
            pattern = rule.get("path")
            roles = rule.get("roles", [])
            if isinstance(roles, str):
                roles = [roles]

            if re.match(pattern, path):
                self.logger.debug(
                    f"Path {path} matches pattern {
                        pattern} with roles {roles}"
                )
                return roles
        return []

    def is_allowed(self, user_roles: List[str], required_roles: List[str]) -> bool:
        """
        Checks if the user has at least one of the required roles.
        """
        has_role = any(role in user_roles for role in required_roles)
        self.logger.debug(
            f"The user {
                'has' if has_role else 'does not have'} the required roles."
        )
        return has_role
