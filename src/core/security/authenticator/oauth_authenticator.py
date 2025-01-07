import logging
from fastapi import Request
from fastapi.responses import RedirectResponse
from typing import Optional
from src.core.security.passport.passport import Passport
from src.core.security.passport.user_badge import UserBadge
from src.core.security.passport.password_credentials import PasswordCredentials
from src.core.security.passport.csrf_token_badge import CsrfTokenBadge
from src.core.security.authenticator.authenticator_interface import (
    AuthenticatorInterface,
)


class OAuthAuthenticator(AuthenticatorInterface):

    def __init__(self):
        self.logger = logging.getLogger("OAUTH_AUTHENTICATOR")

    async def authenticate(self, request: Request) -> Optional[Passport]:
        # Implémentez la logique OAuth ici
        # Exemple simplifié :
        token = request.query_params.get("oauth_token")
        # Validez le token et récupérez les informations de l'utilisateur
        user_email = self.validate_oauth_token(token)
        if user_email:
            passport = Passport(
                user_badge=UserBadge(user_email),
                password_credentials=PasswordCredentials(),
                csrf_token_badge=None,  # Pas nécessaire pour OAuth
            )
            return passport
        return None

    def on_auth_success(self, login_redirect_route: str) -> RedirectResponse:
        return RedirectResponse(login_redirect_route, status_code=303)

    def validate_oauth_token(self, token: str) -> Optional[str]:
        # Validez le token OAuth et retournez l'email de l'utilisateur
        # Implémentation fictive
        if token == "valid_oauth_token":
            return "oauth_user@example.com"
        return None
