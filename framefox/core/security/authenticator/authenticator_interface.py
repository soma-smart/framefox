from abc import ABC, abstractmethod
from typing import Optional

from fastapi import Request

from framefox.core.security.passport.passport import Passport

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class AuthenticatorInterface(ABC):
    @abstractmethod
    async def authenticate(self, request: Request) -> Optional[Passport]:
        pass

    @abstractmethod
    def on_auth_success(self, token: str):
        pass

    @abstractmethod
    def on_auth_failure(self, request: Request):
        pass
