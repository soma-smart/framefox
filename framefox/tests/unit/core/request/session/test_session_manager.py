import os
from unittest.mock import Mock

import pytest

from framefox.core.config.settings import Settings
from framefox.core.request.session.session_manager import SessionManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestSessionManager:
    @pytest.fixture
    def mock_settings(self, tmp_path):
        """Fixture for settings"""
        settings = Mock(spec=Settings)
        settings.session_file_path = str(tmp_path / "sessions.json")
        return settings

    @pytest.fixture
    def session_manager(self, mock_settings):
        """Fixture for SessionManager"""
        return SessionManager(mock_settings)

    @pytest.fixture
    def sample_session_data(self):
        """Fixture for sample session data"""
        return {"user_id": "123", "username": "test_user"}

    @pytest.fixture(autouse=True)
    def cleanup(self, tmp_path):
        yield
        if os.path.exists(str(tmp_path / "sessions.json")):
            os.remove(str(tmp_path / "sessions.json"))

    def test_create_session(self, session_manager, sample_session_data):
        """Test creating a new session"""
        session_id = "test_session"
        max_age = 3600  # 1 hour

        # Create the session
        session_manager.create_session(session_id, sample_session_data, max_age)

        # Verify that the session was created
        session = session_manager.get_session(session_id)
        assert session is not None
        assert session["data"] == sample_session_data
        assert "expires_at" in session

    def test_update_session(self, session_manager, sample_session_data):
        """Test updating a session"""
        session_id = "test_session"
        max_age = 3600

        # First create a session
        session_manager.create_session(session_id, sample_session_data, max_age)

        # Update the session
        updated_data = {**sample_session_data, "username": "updated_user"}
        session_manager.update_session(session_id, updated_data, max_age)

        # Verify the update
        session = session_manager.get_session(session_id)
        assert session["data"]["username"] == "updated_user"

    def test_delete_session(self, session_manager, sample_session_data):
        """Test deleting a session"""
        session_id = "test_session"
        max_age = 3600

        # Create a session
        session_manager.create_session(session_id, sample_session_data, max_age)

        # Delete the session
        result = session_manager.delete_session(session_id)
        assert result is True

        # Verify that the session no longer exists
        assert session_manager.get_session(session_id) is None

    # def test_cleanup_expired_sessions(self, session_manager, tmp_path):
    #     """Test cleaning up expired sessions"""
    #     # Create sessions with different expiration dates
    #     sessions = {
    #         "active": {
    #             "data": {"user": "active"},
    #             "expires_at": (
    #                 datetime.now(timezone.utc) + timedelta(hours=1)
    #             ).timestamp(),
    #         },
    #         "expired1": {
    #             "data": {"user": "expired1"},
    #             "expires_at": (
    #                 datetime.now(timezone.utc) - timedelta(hours=1)
    #             ).timestamp(),
    #         },
    #         "expired2": {
    #             "data": {"user": "expired2"},
    #             "expires_at": (
    #                 datetime.now(timezone.utc) - timedelta(minutes=30)
    #             ).timestamp(),
    #         },
    #     }

    #     # Save the sessions directly
    #     with open(str(tmp_path / "sessions.json"), "w") as f:
    #         json.dump(sessions, f)

    #     # Clean up expired sessions
    #     session_manager.cleanup_expired_sessions()

    #     # Verify that only the active session remains
    #     remaining_sessions = session_manager.load_sessions()
    #     assert len(remaining_sessions) == 1
    #     assert "active" in remaining_sessions
    #     assert "expired1" not in remaining_sessions
    #     assert "expired2" not in remaining_sessions

    # def test_session_file_creation(self, session_manager, tmp_path):
    #     """Test session file creation"""
    #     # Verify that the file does not initially exist
    #     assert not os.path.exists(tmp_path / "sessions.json")

    #     # Create a session
    #     session_manager.create_session("test", {"data": "test"}, 3600)

    #     # Verify that the file was created
    #     assert os.path.exists(tmp_path / "sessions.json")
