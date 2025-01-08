from typing import Annotated
from fastapi.responses import Response
from injectable import Autowired, autowired
from src.core.config.settings import Settings


@autowired
class CookieManager:
    def __init__(self, settings: Annotated[Settings, Autowired]):
        self.settings = settings

    def set_cookie(self, response: Response, key: str, value: str):
        """
        Définit le cookie d'accès JWT.

        Args:
            response (Response): La réponse HTTP.
            token (str): Le token JWT à définir.
            secure (bool, optional): Indique si le cookie doit être sécurisé. Par défaut à False.
        """
        return response.set_cookie(
            key=key,
            value=value,
            expires=10,
            # max_age=self.settings.cookie_max_age,
            httponly=self.settings.cookie_http_only,
            secure=self.settings.cookie_secure,
            samesite=self.settings.cookie_same_site,
            path=self.settings.cookie_path,
        )
