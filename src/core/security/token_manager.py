import logging
from datetime import datetime, timedelta
import jwt
from injectable import Autowired, autowired
from src.core.config.settings import Settings
from typing import Annotated


class TokenManager:
    @autowired
    def __init__(self, settings: Annotated[Settings, Autowired]):
        self.logger = logging.getLogger("TOKENMANAGER")
        self.settings = settings
        self.algorithm = "HS256"

    def create_token(self, user, firewallname: str, roles: list) -> str:

        payload = {
            "email": user.email,
            "firewallname": firewallname,
            "roles": roles,
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token = jwt.encode(
            payload, self.settings.cookie_secret_key, algorithm=self.algorithm
        )
        return token

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token, self.settings.cookie_secret_key, algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired.")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid token.")
            return None
