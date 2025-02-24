from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse

from framefox.core.request.session.session import Session

# from src.entity.user import User
from framefox.core.security.authenticator.abstract_authenticator import (
    AbstractAuthenticator,
)
from framefox.core.security.authenticator.authenticator_interface import (
    AuthenticatorInterface,
)
from framefox.core.security.passport.passport import Passport
from framefox.core.security.passport.user_badge import UserBadge

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class ApiTokenAuthenticator(AbstractAuthenticator, AuthenticatorInterface):
    async def authenticate(self) -> Optional[Passport]:
        passport = Passport()
        # passport.user = User(
        #     id=2,
        #     name="Test User",
        #     email="test@example.com",
        #     password="",
        #     roles=["ROLE_USER"],
        # )
        return passport

    def on_auth_success(self, token: str) -> JSONResponse:
        session_id = Session.get("session_id")
        return JSONResponse(
            {
                "message": "Authentication successful",
                "token": token,
                "session_id": session_id,
            },
            status_code=200,
        )
