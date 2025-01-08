import logging
from typing import Optional, Annotated
from fastapi import Request, HTTPException
from injectable import Autowired, autowired
from src.core.config.settings import Settings
from src.core.security.passport.passport import Passport
from src.core.security.token_manager import TokenManager


class AbstractAuthenticator:
    @autowired
    def __init__(
        self,
        settings: Annotated[Settings, Autowired],
    ):
        self.logger = logging.getLogger("AUTHENTICATOR")
        self.settings = settings
        self.token_manager = TokenManager()

    async def authenticate_request(self, request: Request) -> Optional[Passport]:
        try:
            passport: Optional[Passport] = await self.authenticate(request)
            if passport:
                authenticated = await passport.authenticate_user()
                if not authenticated:
                    self.logger.warning("Authentification échouée.")
                    return None
                return passport
            return None
        except HTTPException as e:
            self.logger.error(
                f"Erreur HTTP lors de l'authentification : {e.detail}")
            return None
