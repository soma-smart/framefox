from typing import Annotated, Optional
from fastapi.responses import Response
from injectable import Autowired, autowired
<<<<<<< Updated upstream:src/core/request/cookie_manager.py
<<<<<<< Updated upstream:src/core/request/cookie_manager.py
from src.core.config.settings import Settings
=======
=======
>>>>>>> Stashed changes:framefox/core/request/cookie_manager.py

from framefox.core.config.settings import Settings
>>>>>>> Stashed changes:framefox/core/request/cookie_manager.py


@autowired
class CookieManager:
    def __init__(self, settings: Annotated[Settings, Autowired]):
        self.settings = settings

    def set_cookie(
        self,
        response: Response,
        key: str,
        value: str,
        max_age: Optional[int] = None,
        expires: Optional[str] = None,
        secure: Optional[bool] = None,
    ):
        """
        Définit un cookie de manière sécurisée avec possibilité de surcharger `max_age`.

        Args:
            response (Response): La réponse HTTP.
            key (str): La clé du cookie.
            value (str): La valeur du cookie.
            max_age (int, optional): Durée de vie du cookie en secondes. Par défaut, utilise `settings.cookie_max_age`.
            expires (str, optional): Date d'expiration du cookie au format HTTP. Facultatif.
            secure (bool, optional): Indique si le cookie doit être sécurisé. Par défaut, utilise `settings.cookie_secure`.
        """
        response.set_cookie(
            key=key,
            value=value,
            max_age=max_age if max_age is not None else self.settings.cookie_max_age,
            expires=expires,
            httponly=self.settings.cookie_http_only,
            secure=secure if secure is not None else self.settings.cookie_secure,
            samesite=self.settings.cookie_same_site,
            path=self.settings.cookie_path,
        )

    def delete_cookie(self, response: Response, key: str):
        """
        Supprime un cookie de manière sécurisée.

        Args:
            response (Response): La réponse HTTP.
            key (str): La clé du cookie à supprimer.
        """
        response.delete_cookie(
            key=key,
            path=self.settings.cookie_path,
        )
