import logging
import time

import jwt

from framefox.core.config.settings import Settings

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TokenManager:

    def __init__(self):
        self.settings = Settings()
        self.logger = logging.getLogger("TOKENMANAGER")
        self.algorithm = "HS256"
        self.expiration = 3600  # Token expiration time in seconds
        self.secret_key = self.settings.session_secret_key
        if not self.secret_key:
            raise ValueError("Session secret key is not set in settings.")

    def create_token(self, user, firewallname: str, roles: list = None) -> str:
        """
        Create a JWT token for the authenticated user.

        Args:
            user: The authenticated user object
            firewallname: The name of the firewall
            roles: List of user roles

        Returns:
            str: The JWT token
        """
        # Gestion des utilisateurs virtuels OAuth
        if hasattr(user, "is_virtual") and user.is_virtual:
            user_id = user.id  # ID virtuel déjà généré
            self.logger.debug(f"Creating token for virtual OAuth user: {user.email}")
        else:
            user_id = user.id
            self.logger.debug(f"Creating token for database user: {user.email}")

        payload = {
            "sub": str(user_id),
            "email": user.email,
            "roles": roles or [],
            "firewallname": firewallname,
            "iat": int(time.time()),
            "exp": int(time.time()) + self.expiration,
        }

        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.settings.session_secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired.")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid token.")
            return None
