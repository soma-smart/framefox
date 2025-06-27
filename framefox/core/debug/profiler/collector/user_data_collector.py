import logging

from framefox.core.debug.profiler.collector.data_collector import DataCollector

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class UserDataCollector(DataCollector):
    """
    User profiling data collector.

    This collector gathers information about the currently authenticated user,
    including email, roles, authentication status, and user session data.
    It provides comprehensive user context for debugging and profiling purposes.

    Attributes:
        name (str): Collector identifier
        data (dict): User authentication and session data
    """

    name = "user"

    def __init__(self):
        super().__init__("user", "fa-user")
        self.data = {
            "is_authenticated": False,
            "email": None,
            "roles": [],
            "user_id": None,
            "user_class": None,
            "session_data": {},
            "authentication_method": None,
            "firewall": None,
            "error": None,
        }

    def collect(self, request, response):
        try:
            from framefox.core.di.service_container import ServiceContainer

            container = ServiceContainer()
            user_provider = container.get_by_name("UserProvider")

            if not user_provider:
                self.data["error"] = "UserProvider not available"
                return

            current_user = user_provider.get_current_user()

            if current_user:
                self.data["is_authenticated"] = True
                self.data["user_id"] = getattr(current_user, "id", None)
                self.data["email"] = getattr(current_user, "email", None)
                self.data["user_class"] = current_user.__class__.__name__

                if hasattr(current_user, "roles"):
                    roles = getattr(current_user, "roles", [])
                    if isinstance(roles, (list, tuple)):
                        self.data["roles"] = list(roles)
                    elif isinstance(roles, str):
                        self.data["roles"] = [roles]
                    else:
                        self.data["roles"] = [str(roles)]
                elif hasattr(current_user, "role"):
                    role = getattr(current_user, "role", None)
                    self.data["roles"] = [role] if role else []
                else:
                    self.data["roles"] = []

                self._collect_session_data(container)
                self._collect_authentication_method(container)

            else:
                self.data["is_authenticated"] = False
                self.data["email"] = None
                self.data["roles"] = []
                self.data["user_id"] = None
                self.data["user_class"] = None

        except Exception as e:
            logging.getLogger("USER_DATA_COLLECTOR").error(f"Error collecting user data: {e}")
            self.data["error"] = str(e)
            self.data["is_authenticated"] = False

    def _collect_session_data(self, container):
        try:
            session = container.get_by_name("Session")
            if session:
                session_data = {}

                if hasattr(session, "get"):
                    session_data["session_id"] = session.get("session_id", "N/A")
                    session_data["user_cached"] = session.get("_current_user_id") is not None

                self.data["session_data"] = session_data
        except Exception as e:
            self.data["session_data"] = {"error": str(e)}

    def _collect_authentication_method(self, container):
        """Determine authentication method used - prioritize session over JWT."""
        try:
            session = container.get_by_name("Session")
            token_storage = container.get_by_name("TokenStorage")
            if session and session.get("_current_user_id"):
                self.data["authentication_method"] = "Session"
                self.data["firewall"] = "main"
            elif token_storage and token_storage.get_payload():
                self.data["authentication_method"] = "JWT Token"
                payload = token_storage.get_payload()
                self.data["firewall"] = payload.get("firewallname", "main")
            else:
                self.data["authentication_method"] = "Anonymous"
                self.data["firewall"] = None

        except Exception as e:
            self.data["authentication_method"] = f"Error: {e}"

    def reset(self):
        self.data = {
            "is_authenticated": False,
            "email": None,
            "roles": [],
            "user_id": None,
            "user_class": None,
            "session_data": {},
            "authentication_method": None,
            "firewall": None,
            "error": None,
        }
