import base64
import hashlib
import hmac
import json
import logging
import os
import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional

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
        db_dir = os.path.dirname(os.path.abspath(self.settings.session_file_path))
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, "sessions.db")
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    expires_at REAL NOT NULL
                )
            """
            )

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON sessions(expires_at)")

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error(f"Error initializing session database: {e}")

    def load_sessions(self) -> Dict:
        """Load all sessions (API compatibility)"""
        sessions = {}
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT session_id, data, expires_at FROM sessions")
            rows = cursor.fetchall()

            for row in rows:
                session_id = row["session_id"]
                data = json.loads(row["data"])
                expires_at = row["expires_at"]
                sessions[session_id] = {"data": data, "expires_at": expires_at}

            conn.close()
        except sqlite3.Error as e:
            self.logger.error(f"Error loading sessions: {e}")

        return sessions

    def save_sessions(self, session_store: Dict) -> None:
        """
        Compatibility method for bulk saving sessions
        This method is less efficient with SQLite but maintained for the API
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions")

            for session_id, session_data in session_store.items():
                serialized_data = json.dumps(session_data.get("data", {}))
                expires_at = session_data.get("expires_at", 0)

                cursor.execute(
                    "INSERT INTO sessions (session_id, data, expires_at) VALUES (?, ?, ?)",
                    (session_id, serialized_data, expires_at),
                )

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error(f"Error saving sessions: {e}")

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve a session by its ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT data, expires_at FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    "data": json.loads(row["data"]),
                    "expires_at": row["expires_at"],
                }
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving session {session_id}: {e}")

        return None

    def create_session(self, session_id: str, data: Dict, max_age: int) -> None:
        """Create a new session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            expires_at = datetime.now(timezone.utc).timestamp() + max_age
            serialized_data = json.dumps(data)

            cursor.execute(
                "INSERT OR REPLACE INTO sessions (session_id, data, expires_at) VALUES (?, ?, ?)",
                (session_id, serialized_data, expires_at),
            )

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error(f"Error creating session {session_id}: {e}")

    def update_session(self, session_id: str, data: Dict, max_age: int) -> None:
        """Update an existing session and reset its expiration time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            expires_at = datetime.now(timezone.utc).timestamp() + max_age
            serialized_data = json.dumps(data)

            cursor.execute(
                "UPDATE sessions SET data = ?, expires_at = ? WHERE session_id = ?",
                (serialized_data, expires_at, session_id),
            )

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error(f"Error updating session {session_id}: {e}")

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            deleted = cursor.rowcount > 0

            conn.commit()
            conn.close()

            return deleted
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting session {session_id}: {e}")
            return False

    def cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            current_time = datetime.now(timezone.utc).timestamp()
            cursor.execute("DELETE FROM sessions WHERE expires_at < ?", (current_time,))
            deleted_count = cursor.rowcount

            if deleted_count > 0:
                self.logger.info(f"Expired sessions cleaned up: {deleted_count}")

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error(f"Error cleaning up expired sessions: {e}")

    def sign_session_id(self, session_id: str) -> str:
        """
        Signs the session ID with HMAC-SHA256 to prevent tampering
        """
        if not session_id:
            return ""

        secret_key = self.settings.session_secret_key.encode("utf-8")

        signature = hmac.new(secret_key, session_id.encode("utf-8"), digestmod=hashlib.sha256).digest()

        encoded_sig = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")

        return f"{session_id}.{encoded_sig}"

    def verify_and_extract_session_id(self, signed_id: str) -> Optional[str]:
        """
        Verifies the signature of a signed ID and extracts the original ID
        Returns None if the ID is invalid or improperly signed
        """

        if not signed_id or "." not in signed_id:
            return None

        raw_id, received_sig = signed_id.split(".", 1)

        expected_signed_id = self.sign_session_id(raw_id)
        expected_id, expected_sig = expected_signed_id.split(".", 1)

        if hmac.compare_digest(received_sig, expected_sig):
            return raw_id

        self.logger.warning(f"Invalid session signature detected")
        return None
