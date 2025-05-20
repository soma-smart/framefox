import logging
from datetime import datetime, timedelta

import jwt

from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TokenManager:

    def __init__(self):
        self.settings = ServiceContainer().get(Settings)
        self.logger = logging.getLogger("TOKENMANAGER")
        self.algorithm = "HS256"

    def create_token(self, user, firewallname: str, roles: list) -> str:

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "firewallname": firewallname,
            "roles": roles,
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token = jwt.encode(
            payload, self.settings.session_secret_key, algorithm=self.algorithm
        )
        return token

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token, self.settings.session_secret_key, algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired.")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid token.")
            return None
