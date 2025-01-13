import uuid
<<<<<<< Updated upstream:src/core/request/session/session.py
=======

from framefox.core.request.request_stack import RequestStack
>>>>>>> Stashed changes:framefox/core/request/session/session.py

<<<<<<< Updated upstream:src/core/request/session/session.py
from src.core.request.request_stack import RequestStack
import uuid
=======
from framefox.core.request.request_stack import RequestStack
>>>>>>> Stashed changes:framefox/core/request/session/session.py


class Session:
    """
    Session management utility class.

    This class provides static methods to interact with the session data
    associated with the current request. It allows getting, setting, checking,
    removing, and clearing session data.

    Methods:
        get(key, default=None):
            Retrieve a value from the session using the given key. If the key
            does not exist, return the default value.

        set(key, value):
            Set a value in the session with the given key.

        has(key):
            Check if a given key exists in the session.

        remove(key):
            Remove a value from the session using the given key.

        flush():
            Clear all data from the session.
    """

    @staticmethod
    def get(key, default=None):
        request = RequestStack.get_request()
        return request.state.session_data.get(key, default)

    @staticmethod
    def set(key, value):
        request = RequestStack.get_request()
        if not request.state.session_id:
            request.state.session_data = {}
            request.state.session_id = str(uuid.uuid4())
        request.state.session_data[key] = value

    @staticmethod
    def has(key):
        request = RequestStack.get_request()
        return key in request.state.session_data

    @staticmethod
    def remove(key):
        request = RequestStack.get_request()
        if key in request.state.session_data:
            del request.state.session_data[key]

    @staticmethod
    def flush():
        request = RequestStack.get_request()
        request.state.session_data.clear()

    @staticmethod
    def get_all():
        request = RequestStack.get_request()
        return request.state.session_data
