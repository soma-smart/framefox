import logging

from fastapi import Request
from starlette.middleware.sessions import SessionMiddleware


class CustomSessionMiddleware(SessionMiddleware):
    """
    CustomSessionMiddleware is a middleware class that extends the SessionMiddleware to provide custom session handling.

    Attributes:
        logger (logging.Logger): Logger instance for logging session activities.

    Methods:
        __init__(app, settings):
            Initializes the middleware with the given application and settings.

        dispatch(request: Request, call_next):
            Handles the incoming request, manages session expiration, and sets the session cookie in the response.

            Args:
                request (Request): The incoming request object.
                call_next: The next middleware or route handler to call.

            Returns:
                Response: The response object after processing the request.
    """

    def __init__(self, app, settings):
        super().__init__(
            app,
            secret_key=settings.cookie_secret_key,
            session_cookie="session_id",
            max_age=settings.cookie_max_age,
            same_site=settings.cookie_same_site,
            https_only=settings.cookie_http_only,
        )
        self.logger = logging.getLogger("SESSION")

    async def dispatch(self, request: Request, call_next):

        self.logger.info(f"Session accessed for path: {request.url.path}")

        session = request.session
        if "last_activity" in session:
            if (
                request.state.time - session["last_activity"]
            ).total_seconds() > self.max_age:
                session.clear()
                self.logger.info("Session expired and cleared.")
        session["last_activity"] = request.state.time

        response = await call_next(request)

        response.set_cookie(
            key=self.session_cookie,
            value=request.cookies.get(self.session_cookie),
            max_age=self.max_age,
            httponly=True,
            secure=self.https_only,
            samesite=self.same_site,
        )

        return response
