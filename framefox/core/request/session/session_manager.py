import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Optional

from framefox.core.config.settings import Settings

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class SessionManager:

    def __init__(self, settings: Settings):
        self.settings = settings

        self.logger = logging.getLogger("SESSION_MANAGER")

        self.session_file_path = self.settings.session_file_path

    def load_sessions(self) -> Dict:
        """Loads the session file"""
        absolute_path = os.path.abspath(self.settings.session_file_path)

        if os.path.exists(absolute_path):
            with open(absolute_path, "r") as f:
                return json.load(f)
        return {}

    def save_sessions(self, session_store: Dict) -> None:
        """Saves the session store"""
        absolute_path = os.path.abspath(self.settings.session_file_path)

        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
        with open(absolute_path, "w") as f:
            json.dump(session_store, f)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieves a session by its ID"""
        sessions = self.load_sessions()

        return sessions.get(session_id)

    def create_session(self, session_id: str, data: Dict, max_age: int) -> None:
        """Creates a new session"""
        sessions = self.load_sessions()
        sessions[session_id] = {
            "data": data,
            "expires_at": (datetime.now(timezone.utc).timestamp() + max_age),
        }
        self.save_sessions(sessions)

    def update_session(self, session_id: str, data: Dict, max_age: int) -> None:
        """Updates an existing session"""
        sessions = self.load_sessions()
        if session_id in sessions:
            sessions[session_id].update(
                {
                    "data": data,
                    "expires_at": (datetime.now(timezone.utc).timestamp() + max_age),
                }
            )
            self.save_sessions(sessions)

    def delete_session(self, session_id: str) -> bool:
        """Deletes a session"""
        sessions = self.load_sessions()
        if session_id in sessions:
            del sessions[session_id]
            self.save_sessions(sessions)
            return True
        return False

    def cleanup_expired_sessions(self) -> None:
        """Cleans up expired sessions"""
        sessions = self.load_sessions()
        current_time = datetime.now(timezone.utc).timestamp()
        expired = [sid for sid, s in sessions.items() if s["expires_at"] < current_time]

        if expired:
            for sid in expired:
                del sessions[sid]
            self.save_sessions(sessions)
            self.logger.info(f"Expired sessions cleaned up: {len(expired)}")
