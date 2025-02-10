from abc import ABC, abstractmethod
from typing import Optional

from fastapi import Request

from framefox.core.security.passport.passport import Passport


class AuthenticatorInterface(ABC):
    @abstractmethod
    async def authenticate(self, request: Request) -> Optional[Passport]:
        pass

    @abstractmethod
    def on_auth_success(self, token: str):
        pass
