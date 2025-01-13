from abc import ABC, abstractmethod
from fastapi import Request
from typing import Optional
<<<<<<< Updated upstream:src/core/security/authenticator/authenticator_interface.py
<<<<<<< Updated upstream:src/core/security/authenticator/authenticator_interface.py
from src.core.security.passport.passport import Passport
=======
=======
>>>>>>> Stashed changes:framefox/core/security/authenticator/authenticator_interface.py

from framefox.core.security.passport.passport import Passport
>>>>>>> Stashed changes:framefox/core/security/authenticator/authenticator_interface.py


class AuthenticatorInterface(ABC):
    @abstractmethod
    async def authenticate(self, request: Request) -> Optional[Passport]:
        pass

    @abstractmethod
    def on_auth_success(self, token: str):
        pass
