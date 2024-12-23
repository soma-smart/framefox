import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Response, Request
from src.core.config.settings import Settings
from typing import Annotated
from injectable import autowired, Autowired
import logging


class TokenManager:
    def __init__(self, settings: Annotated[Settings, Autowired]):
        self.logger = logging.getLogger("AUTH")
        self.secret_key = settings.session_secret_key
        self.algorithm = "HS256"
        self.expiration_minutes = 60  # Durée de validité du token

    def create_token(self, user_id: int, roles: list) -> str:
        payload = {
            "user_id": user_id,
            "roles": roles,
            "exp": datetime.utcnow() + timedelta(minutes=self.expiration_minutes),
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def add_token_to_response(self, response: Response, token: str):
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=True,  # Assurez-vous d'utiliser HTTPS
            samesite="strict",
            max_age=self.expiration_minutes * 60,
        )

    def decode_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
