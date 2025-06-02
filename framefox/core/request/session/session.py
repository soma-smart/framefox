import logging
import uuid
from typing import Any, Dict, Optional

from fastapi import Request

from framefox.core.request.request_stack import RequestStack
from framefox.core.request.session.flash_bag import FlashBag
from framefox.core.request.session.session_interface import SessionInterface

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class Session(SessionInterface):

    def __init__(self):
        self._flash_bag = FlashBag()

    def get_request(self) -> Request:
        """Retrieve the current request via the RequestStack"""
        return RequestStack.get_request()

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the session"""
        request = self.get_request()
        return request.state.session_data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value in the session"""
        request = self.get_request()
        if not hasattr(request.state, "session_data"):
            request.state.session_data = {}

        if not hasattr(request.state, "session_id") or not request.state.session_id:
            request.state.session_id = str(uuid.uuid4())

        request.state.session_data[key] = value

    def has(self, key: str) -> bool:
        """Check if a key exists in the session"""
        request = self.get_request()
        if not hasattr(request.state, "session_data"):
            return False
        return key in request.state.session_data

    def remove(self, key: str) -> None:
        """Remove a value from the session"""
        request = self.get_request()
        if hasattr(request.state, "session_data") and key in request.state.session_data:
            del request.state.session_data[key]

    def clear(self) -> None:
        """Completely clear the session"""
        request = self.get_request()
        if hasattr(request.state, "session_data"):
            request.state.session_data.clear()

    def get_id(self) -> Optional[str]:
        """Retrieve the session ID"""
        request = self.get_request()
        return getattr(request.state, "session_id", None)

    def migrate(self, destroy: bool = False) -> bool:
        """Migrate the session to a new ID"""
        request = self.get_request()
        old_id = getattr(request.state, "session_id", None)

        new_id = str(uuid.uuid4())
        request.state.session_id = new_id

        if destroy and old_id:
            from framefox.core.di.service_container import ServiceContainer
            from framefox.core.request.session.session_manager import SessionManager

            container = ServiceContainer()
            session_manager = container.get(SessionManager)
            if session_manager:
                session_manager.delete_session(old_id)

        return True

    def invalidate(self) -> bool:
        """Invalidate the session and generate a new ID"""
        self.clear()
        return self.migrate(True)

    def get_all(self) -> Dict:
        """Retrieve all session data"""
        request = self.get_request()
        return getattr(request.state, "session_data", {})

    def get_flash_bag(self) -> FlashBag:
        """Retrieve the flash message manager"""
        if not self.has("_flash_initialized"):
            self._flash_bag.initialize_from_session(self)
            self.set("_flash_initialized", True)
        return self._flash_bag

    def save(self) -> None:
        """Save all session data"""
        if self.has("_flash_initialized"):
            self._flash_bag.save_to_session(self)

        request = self.get_request()
        session_id = self.get_id()

        if session_id and hasattr(request.state, "session_data"):
            from framefox.core.config.settings import Settings
            from framefox.core.di.service_container import ServiceContainer
            from framefox.core.request.session.session_manager import SessionManager

            container = ServiceContainer()
            session_manager = container.get(SessionManager)
            settings = container.get(Settings)

            if session_manager:
                session_manager.update_session(
                    session_id, request.state.session_data, settings.cookie_max_age
                )
