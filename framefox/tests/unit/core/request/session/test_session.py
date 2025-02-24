import pytest
from unittest.mock import Mock, patch
from fastapi import Request
from framefox.core.request.session.session import Session
from framefox.core.request.request_stack import RequestStack

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TestSession:
    @pytest.fixture
    def mock_request(self):
        """Fixture to simulate a request"""
        request = Mock(spec=Request)
        request.state.session_data = {}
        request.state.session_id = None
        return request

    @pytest.fixture(autouse=True)
    def setup_request_stack(self, mock_request):
        """Fixture to configure the RequestStack"""
        with patch.object(RequestStack, 'get_request', return_value=mock_request):
            yield

    def test_set_and_get(self, mock_request):
        """Test setting and getting values in the session"""
        # Test set
        Session.set("test_key", "test_value")
        assert mock_request.state.session_id is not None
        assert "test_key" in mock_request.state.session_data

        # Test get
        value = Session.get("test_key")
        assert value == "test_value"

        # Test get with default value
        default_value = Session.get("non_existent", "default")
        assert default_value == "default"

    def test_has(self, mock_request):
        """Test checking the existence of a key"""
        # Non-existent key
        assert not Session.has("test_key")

        # Add a key
        Session.set("test_key", "test_value")
        assert Session.has("test_key")

    def test_remove(self, mock_request):
        """Test removing a value"""
        # Add then remove a value
        Session.set("test_key", "test_value")
        assert Session.has("test_key")

        Session.remove("test_key")
        assert not Session.has("test_key")

        # Attempting to remove a non-existent key should not raise an error
        Session.remove("non_existent")

    def test_flush(self, mock_request):
        """Test completely clearing the session"""
        # Add multiple values
        Session.set("key1", "value1")
        Session.set("key2", "value2")
        assert len(mock_request.state.session_data) == 2

        # Clear the session
        Session.flush()
        assert len(mock_request.state.session_data) == 0

    def test_get_all(self, mock_request):
        """Test retrieving all session data"""
        # Initially empty session
        assert len(Session.get_all()) == 0

        # Add data
        test_data = {"key1": "value1", "key2": "value2"}
        for key, value in test_data.items():
            Session.set(key, value)

        # Verify data
        all_data = Session.get_all()
        assert all_data == mock_request.state.session_data
        assert len(all_data) == len(test_data)
        for key, value in test_data.items():
            assert key in all_data
            assert all_data[key] == value

    def test_session_id_generation(self, mock_request):
        """Test automatic session ID generation"""
        assert mock_request.state.session_id is None

        # The first use of set() should generate an ID
        Session.set("test_key", "test_value")
        generated_id = mock_request.state.session_id

        assert generated_id is not None
        assert isinstance(generated_id, str)
        # Subsequent uses should retain the same ID
        Session.set("another_key", "another_value")
        assert mock_request.state.session_id == generated_id
