import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from framefox.core.di.service_container import ServiceContainer
from framefox.core.request.cookie_manager import CookieManager
from framefox.core.request.request_stack import RequestStack
from framefox.core.request.session.session_manager import SessionManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        settings,
    ):
        super().__init__(app)
        self.settings = settings

        self.cookie_name = settings.session_cookie_name
        container = ServiceContainer()
        self.cookie_manager = container.get(CookieManager)
        self.session_manager = container.get(SessionManager)

    async def dispatch(self, request: Request, call_next):
        session_id = request.cookies.get(self.cookie_name)
        session = self.session_manager.get_session(
            session_id) if session_id else None

        RequestStack.set_request(request)

        if session:
            self.logger.info(f"Session expired for session_id: {session_id}")
            self.session_manager.delete_session(session_id)
            request.state.session_id = None
            request.state.session_data = {}
            response = Response(
                content="Session expired. Please log in again.",
                status_code=440,
            )
            self.cookie_manager.delete_cookie(response, self.cookie_name)
            RequestStack.set_request(None)
            return response
        else:
            session_id = None
            request.state.session_data = {}

        request.state.session_id = session_id
        request.state.session_data = session["data"] if session else {}

        response: Response = await call_next(request)

        if request.state.session_data:
            if not session_id:
                session_id = str(uuid.uuid4())
                request.state.session_id = session_id
                self.session_manager.create_session(
                    session_id, request.state.session_data, self.settings.cookie_max_age
                )
            else:
                self.session_manager.update_session(
                    session_id, request.state.session_data, self.settings.cookie_max_age
                )

            expiration = datetime.now(timezone.utc) + timedelta(
                seconds=self.settings.cookie_max_age
            )
            self.cookie_manager.set_cookie(
                response=response,
                key=self.cookie_name,
                value=session_id,
                max_age=self.settings.cookie_max_age,
                expires=expiration.strftime("%a, %d-%b-%Y %H:%M:%S GMT"),
            )

        self.session_manager.cleanup_expired_sessions()
        RequestStack.set_request(None)

        return response
