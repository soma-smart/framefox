from unittest.mock import Mock

import pytest
from fastapi import Request

from framefox.core.request.request_stack import RequestStack

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestRequestStack:
    @pytest.fixture
    def mock_request(self):
        """Fixture to simulate a request"""
        return Mock(spec=Request)

    def test_set_and_get_request(self, mock_request):
        """Test setting and getting a request"""
        try:
            # Set the request
            RequestStack.set_request(mock_request)

            # Retrieve and verify the request
            retrieved_request = RequestStack.get_request()
            assert retrieved_request == mock_request
        finally:
            # Clean up the context
            RequestStack.set_request(None)

    def test_set_multiple_requests(self, mock_request):
        """Test setting multiple successive requests"""
        try:
            # Create two different mock requests
            first_request = Mock(spec=Request)
            second_request = Mock(spec=Request)

            # Set the first request
            RequestStack.set_request(first_request)
            assert RequestStack.get_request() == first_request

            # Set the second request
            RequestStack.set_request(second_request)
            assert RequestStack.get_request() == second_request
        finally:
            # Clean up the context
            RequestStack.set_request(None)
