import logging
from typing import Optional, Annotated
from fastapi import Request, HTTPException
from injectable import Autowired, autowired

from framefox.core.config.settings import Settings
from framefox.core.security.passport.passport import Passport
from framefox.core.security.token_manager import TokenManager
from framefox.core.security.user.entity_user_provider import EntityUserProvider


class AbstractAuthenticator:
    @autowired
    def __init__(
        self,
        settings: Annotated[Settings, Autowired],
        entity_user_provider: Annotated[EntityUserProvider, Autowired],
    ):
        self.logger = logging.getLogger("AUTHENTICATOR")
        self.settings = settings
        self.token_manager = TokenManager()
        self.entity_user_provider = entity_user_provider

    async def authenticate_request(
        self, request: Request, firewall_name: str
    ) -> Optional[Passport]:
        try:
            passport: Optional[Passport] = await self.authenticate(request)
            if passport:

                provider_info = self.entity_user_provider.get_repository_and_property(
                    firewall_name
                )

                passport.provider_info = (
                    {"repository": provider_info[0],
                        "property": provider_info[1]}
                    if provider_info
                    else None
                )

                authenticated = await passport.authenticate_user()
                if not authenticated:
                    self.logger.warning("Authentication failed.")
                    return None
                return passport
            return None
        except HTTPException as e:
            self.logger.error(f"HTTP error while authentication : {e.detail}")
            return None
