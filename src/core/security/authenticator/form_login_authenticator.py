import logging
from typing import Optional, Annotated
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from src.core.security.passport.passport import Passport
from src.core.security.passport.user_badge import UserBadge
from src.core.security.passport.password_credentials import PasswordCredentials
from src.core.security.passport.csrf_token_badge import CsrfTokenBadge
from src.core.request.csrf_token_manager import CsrfTokenManager
from src.core.request.cookie_manager import CookieManager
from src.core.templates.template_renderer import TemplateRenderer
from src.core.security.token_manager import TokenManager
from src.core.security.exceptions.invalid_csrf_token_exception import (
    InvalidCsrfTokenException,
)
from injectable import Autowired, autowired
from src.core.config.settings import Settings


class FormLoginAuthenticator:
    @autowired
    def __init__(
        self,
        settings: Annotated[Settings, Autowired],
        template_renderer: Annotated[TemplateRenderer, Autowired],
    ):
        self.logger = logging.getLogger("FORM_AUTHENTICATOR")
        self.settings = settings
        self.template_renderer = template_renderer
        self.cookie_manager = CookieManager()
        self.csrf_manager = CsrfTokenManager(prefix="csrf_")
        self.token_manager = TokenManager()

    async def authenticate(self, request: Request) -> Optional[Passport]:
        form = await request.form()
        email = form.get("email")
        passport = Passport(
            user_badge=UserBadge(email),
            password_credentials=PasswordCredentials(form.get("password")),
            csrf_token_badge=CsrfTokenBadge(form.get("csrf_token")),
        )
        return passport

    def on_auth_success(self, passport: Passport) -> RedirectResponse:
        token = self.token_manager.create_token(
            user=passport.user,
            firewallname="main_firewall",
            roles=(passport.user.roles if passport.user.roles else []),
        )

        response = RedirectResponse(self.settings.login_redirect_route, status_code=303)
        self.cookie_manager.set_response_cookie(
            response=response, key="access_token", token=token
        )
        self.logger.info("Authentication successful and token added to the cookie.")
        return response

    async def handle_login_get(self) -> HTMLResponse:
        """
        Gère les requêtes GET pour la page de login en générant un token CSRF.
        """
        self.logger.debug("Handling a GET request to the login page.")
        csrf_token_value = self.csrf_manager.get_token()
        content = self.template_renderer.render(
            "login.html", {"csrf_token": csrf_token_value}
        )
        response = HTMLResponse(content=content, status_code=200)
        self.cookie_manager.set_response_cookie(
            response=response, key="csrf_token", token=csrf_token_value
        )
        self.logger.debug("CSRF token set in the cookie.")
        return response

    async def handle_login_post(self, request: Request) -> Response:
        """
        Gère les requêtes POST pour la page de login en authentifiant l'utilisateur.
        """
        self.logger.debug("Handling a POST request to the login page.")
        form = await request.form()
        csrf_token_cookie = request.cookies.get("csrf_token")
        csrf_token_form = form.get("csrf_token")

        if not self.csrf_manager.validate_token(csrf_token_cookie, csrf_token_form):
            self.logger.error("CSRF validation failed.")
            return Response(content="Invalid CSRF token", status_code=400)
        try:
            passport: Optional[Passport] = await self.authenticate(request)
            if passport:
                authenticated = await passport.authenticate_user()
                if not authenticated:
                    self.logger.warning("Invalid credentials.")
                    return RedirectResponse(url="/login", status_code=302)

                return self.on_auth_success(passport)

            return Response(content="Authentication failed", status_code=400)
        except HTTPException as e:
            self.logger.error(f"HTTP error during authentication: {e.detail}")
            return RedirectResponse(url="/login", status_code=302)
        except InvalidCsrfTokenException:
            self.logger.error("CSRF validation failed.")
            return Response(content="Invalid CSRF token", status_code=400)
