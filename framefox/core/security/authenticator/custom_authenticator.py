from typing import Optional
from fastapi import Request
from fastapi.responses import Response

from framefox.core.security.passport.passport import Passport
from framefox.core.security.authenticator.abstract_authenticator import (
    AbstractAuthenticator,
)
from framefox.core.security.authenticator.authenticator_interface import (
    AuthenticatorInterface,
)


class CustomAuthenticator(AbstractAuthenticator, AuthenticatorInterface):
    async def authenticate(self, request: Request) -> Optional[Passport]:
        passport = Passport()

        return passport

    def on_auth_success(self, token: str) -> Response:

        return Response()
