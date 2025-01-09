# python

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from src.core.request.request_stack import RequestStack
from src.core.request.cookie_manager import CookieManager
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from src.core.request.session.session_manager import SessionManager


# SESSION_FILE_PATH = "var/session_store.json"


class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        settings,
        cookie_name: str = "session_id",
    ):
        super().__init__(app)
        self.settings = settings
        self.cookie_manager = CookieManager()
        self.cookie_name = cookie_name
        self.session_manager = SessionManager()

    async def dispatch(self, request: Request, call_next):
        session_id = request.cookies.get(self.cookie_name)
        session = self.session_manager.get_session(
            session_id) if session_id else None

        RequestStack.set_request(request)

        if session:
            if session["expires_at"] < datetime.now(timezone.utc).timestamp():
                self.session_manager.delete_session(session_id)
                request.state.session_id = None
                request.state.session_data = {}
                response = Response(content="Session expired", status_code=440)
                self.cookie_manager.delete_cookie(response, self.cookie_name)
                RequestStack.set_request(None)
                return response

        request.state.session_id = session_id
        request.state.session_data = session["data"] if session else {}

        response = await call_next(request)

        if request.state.session_data:
            if not session_id:
                session_id = str(uuid.uuid4())
                request.state.session_id = session_id
                self.session_manager.create_session(
                    session_id,
                    request.state.session_data,
                    self.settings.cookie_max_age
                )
            else:
                self.session_manager.update_session(
                    session_id,
                    request.state.session_data,
                    self.settings.cookie_max_age
                )

        expiration = datetime.now(
            timezone.utc) + timedelta(seconds=self.settings.cookie_max_age)
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

    # async def dispatch(self, request: Request, call_next):

    #     if os.path.exists(SESSION_FILE_PATH):
    #         with open(SESSION_FILE_PATH, "r") as f:
    #             session_store = json.load(f)
    #     else:
    #         session_store = {}

    #     RequestStack.set_request(request)

    #     session_id = request.cookies.get(self.cookie_name)
    #     session = session_store.get(session_id)

    #     if session:
    #         if session["expires_at"] < datetime.now(timezone.utc).timestamp():
    #             self.logger.info(
    #                 f"Session expired for session_id: {session_id}")
    #             del session_store[session_id]
    #             with open(SESSION_FILE_PATH, "w") as f:
    #                 json.dump(session_store, f)
    #             request.state.session_id = None
    #             request.state.session_data = {}
    #             response = Response(
    #                 content="Session expired. Please log in again.", status_code=440)
    #             self.cookie_manager.delete_cookie(response, self.cookie_name)
    #             RequestStack.set_request(None)
    #             return response
    #     else:
    #         session_id = None
    #         request.state.session_data = {}

    #     request.state.session_id = session_id
    #     request.state.session_data = session_store.get(
    #         session_id, {}).get("data", {}) if session_id else {}

    #     response: Response = await call_next(request)

    #     if request.state.session_data:
    #         if not session_id:
    #             session_id = str(uuid.uuid4())
    #             request.state.session_id = session_id

    #         session_store[session_id] = {
    #             "data": request.state.session_data,
    #             "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=self.settings.cookie_max_age)).timestamp()
    #         }

    #         expiration = datetime.now(
    #             timezone.utc) + timedelta(seconds=self.settings.cookie_max_age)
    #         self.cookie_manager.set_cookie(
    #             response=response,
    #             key=self.cookie_name,
    #             value=session_id,
    #             max_age=self.settings.cookie_max_age,
    #             expires=expiration.strftime("%a, %d-%b-%Y %H:%M:%S GMT"),
    #         )

    #     with open(SESSION_FILE_PATH, "w") as f:
    #         json.dump(session_store, f)

    #     await self.gc_sessions(session_store)

    #     RequestStack.set_request(None)

    #     return response

    # async def gc_sessions(self, session_store):
    #     current_time = datetime.now(timezone.utc).timestamp()
    #     expired_sessions = [
    #         sid for sid, s in session_store.items() if s["expires_at"] < current_time
    #     ]
    #     for sid in expired_sessions:
    #         del session_store[sid]
    #     if expired_sessions:
    #         with open(SESSION_FILE_PATH, "w") as f:
    #             json.dump(session_store, f)
