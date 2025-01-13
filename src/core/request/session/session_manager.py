from datetime import datetime, timezone
import json
import os
from typing import Dict, Optional, Annotated
import logging
from injectable import autowired, Autowired
<<<<<<< Updated upstream:src/core/request/session/session_manager.py
<<<<<<< Updated upstream:src/core/request/session/session_manager.py
from src.core.config.settings import Settings
=======
=======
>>>>>>> Stashed changes:framefox/core/request/session/session_manager.py

from framefox.core.config.settings import Settings
>>>>>>> Stashed changes:framefox/core/request/session/session_manager.py


class SessionManager:

    @autowired
    def __init__(self, settings: Annotated[Settings, Autowired]):
        self.logger = logging.getLogger("SESSION_MANAGER")
        self.settings = settings
        self.session_file_path = settings.session_file_path

    def load_sessions(self) -> Dict:
        """Loads the session file"""
        absolute_path = os.path.abspath(self.settings.session_file_path)
        self.logger.info(f"Loading session file from: {absolute_path}")
        if os.path.exists(absolute_path):
            with open(absolute_path, "r") as f:
                return json.load(f)
        return {}

    def save_sessions(self, session_store: Dict) -> None:
        """Saves the session store"""
        absolute_path = os.path.abspath(self.settings.session_file_path)

        self.logger.info(f"Saving session file to: {absolute_path}")
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
        with open(absolute_path, "w") as f:
            json.dump(session_store, f)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieves a session by its ID"""
        sessions = self.load_sessions()
        self.logger.info(f"Retrieving session: {session_id}")
        return sessions.get(session_id)

    def create_session(self, session_id: str, data: Dict, max_age: int) -> None:
        """Creates a new session"""
        sessions = self.load_sessions()
        sessions[session_id] = {
            "data": data,
            "expires_at": (datetime.now(timezone.utc).timestamp() + max_age),
        }
        self.save_sessions(sessions)
        self.logger.info(f"Session created: {session_id}")

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
            self.logger.info(f"Session updated: {session_id}")

    def delete_session(self, session_id: str) -> bool:
        """Deletes a session"""
        sessions = self.load_sessions()
        if session_id in sessions:
            del sessions[session_id]
            self.save_sessions(sessions)
            self.logger.info(f"Session deleted: {session_id}")
            return True
        return False

    def cleanup_expired_sessions(self) -> None:
        """Cleans up expired sessions"""
        sessions = self.load_sessions()
        current_time = datetime.now(timezone.utc).timestamp()
        expired = [sid for sid, s in sessions.items() if s["expires_at"]
                   < current_time]

        if expired:
            for sid in expired:
                del sessions[sid]
            self.save_sessions(sessions)
            self.logger.info(f"Expired sessions cleaned up: {len(expired)}")
