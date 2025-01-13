from typing import Optional
from fastapi import Request
from fastapi.responses import Response

<<<<<<< Updated upstream:src/core/security/authenticator/custom_authenticator.py
<<<<<<< Updated upstream:src/core/security/authenticator/custom_authenticator.py
from src.core.security.passport.passport import Passport
from src.core.security.passport.user_badge import UserBadge
from src.entity.user import User
from src.core.security.authenticator.abstract_authenticator import AbstractAuthenticator
from src.core.security.authenticator.authenticator_interface import (
    AuthenticatorInterface,
)
from src.core.request.session.session import Session
=======
=======
>>>>>>> Stashed changes:framefox/core/security/authenticator/custom_authenticator.py
from framefox.core.security.passport.passport import Passport
from framefox.core.security.authenticator.abstract_authenticator import (
    AbstractAuthenticator,
)
from framefox.core.security.authenticator.authenticator_interface import (
    AuthenticatorInterface,
)
<<<<<<< Updated upstream:src/core/security/authenticator/custom_authenticator.py
>>>>>>> Stashed changes:framefox/core/security/authenticator/custom_authenticator.py
=======
>>>>>>> Stashed changes:framefox/core/security/authenticator/custom_authenticator.py


class CustomAuthenticator(AbstractAuthenticator, AuthenticatorInterface):
    async def authenticate(self, request: Request) -> Optional[Passport]:
        passport = Passport()

        return passport

    def on_auth_success(self, token: str) -> Response:

        return Response()
