from typing import Optional
from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.security.passport.passport import Passport
from src.core.security.passport.user_badge import UserBadge
from src.entity.user import User
from src.core.security.authenticator.abstract_authenticator import AbstractAuthenticator
from src.core.security.authenticator.authenticator_interface import AuthenticatorInterface
from src.core.request.session.session import Session


class ApiTokenAuthenticator(AbstractAuthenticator, AuthenticatorInterface):
    async def authenticate(self, request: Request) -> Optional[Passport]:
        passport = Passport()
        passport.user = User(
            id=2,
            name="Utilisateur Test",
            email="lol",
            password="",
            roles=["ROLE_USER"],
        )
        return passport

    def on_auth_success(self, token: str) -> JSONResponse:
        session_id = Session.get('session_id')
        return JSONResponse(
            {
                "message": "Authentification réussie",
                "token": token,
                "session_id": session_id,
            },
            status_code=200
        )
