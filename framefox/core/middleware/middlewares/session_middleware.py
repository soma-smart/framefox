import logging, uuid
from datetime import datetime, timedelta, timezone
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from framefox.core.di.service_container import ServiceContainer
from framefox.core.request.request_stack import RequestStack
from framefox.core.request.session.session_interface import SessionInterface
from framefox.core.config.settings import Settings
from framefox.core.request.session.session import Session

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(self,app):
        super().__init__(app)   
        self.logger = logging.getLogger("SESSION")
        self.settings = Settings()
        self.container = ServiceContainer()
        self.cookie_name = self.settings.session_name
        self.cookie_manager = self.container.get_by_tag("core.request.cookie_manager")
        self.session_manager = self.container.get_by_tag("core.request.session.session_manager")
        self.session_service = self.container.get_by_tag("core.request.session.session_service")

    async def dispatch(self, request: Request, call_next):
        """
        Processes the session for the current request
        Uses an inactivity-based expiration system rather than a fixed duration
        """
        signed_session_id = request.cookies.get(self.cookie_name)
        session_id = None
        session = None

        if signed_session_id:

            session_id = self.session_manager.verify_and_extract_session_id(
                signed_session_id
            )
            if session_id:
                session = self.session_manager.get_session(session_id)
                if not session:
                    session_id = None

        request.state.session_id = session_id
        request.state.session_data = session["data"] if session else {}

        RequestStack.set_request(request)
        if not self.session_service:
            try:
                session_instance = Session()
            except Exception as e:
                self.logger.error(f"Error while creating a Session instance: {e}")
                session_instance = None
        else:
            session_instance = self.session_service

        if session_instance:
            self.container.set_instance(SessionInterface, session_instance)

        response = await call_next(request)

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

            signed_session_id = self.session_manager.sign_session_id(session_id)

            self.cookie_manager.set_cookie(
                response=response,
                key=self.cookie_name,
                value=signed_session_id,
                max_age=self.settings.cookie_max_age,
                expires=expiration.strftime("%a, %d-%b-%Y %H:%M:%S GMT"),
            )

        self.session_manager.cleanup_expired_sessions()
        RequestStack.set_request(None)

        return response
