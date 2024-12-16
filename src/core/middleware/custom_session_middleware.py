from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging


class CustomSessionMiddleware(SessionMiddleware):
    def __init__(self, app, settings):
        super().__init__(
            app,
            secret_key=settings.session_secret_key,
            session_cookie="session_id",
            max_age=settings.session_max_age,
            same_site=settings.session_same_site,
            https_only=settings.session_https_only,
        )
        self.logger = logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next):
        # Journaliser l'accès à la session
        self.logger.info(f"Session accessed for path: {request.url.path}")

        # Vérifier l'expiration de la session
        session = request.session
        if "last_activity" in session:
            if (request.state.time - session["last_activity"]).total_seconds() > self.max_age:
                session.clear()
                self.logger.info("Session expired and cleared.")
        session["last_activity"] = request.state.time

        response = await call_next(request)

        # Ajouter des en-têtes de sécurité pour les cookies
        response.set_cookie(
            key=self.session_cookie,
            value=request.cookies.get(self.session_cookie),
            max_age=self.max_age,
            httponly=True,
            secure=self.https_only,
            samesite=self.same_site,
        )

        return response
