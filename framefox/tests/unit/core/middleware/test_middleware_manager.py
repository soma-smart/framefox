from unittest.mock import Mock

import pytest
from fastapi import FastAPI

from framefox.core.config.settings import Settings
from framefox.core.middleware.middleware_manager import MiddlewareManager
from framefox.core.middleware.middlewares.entity_manager_middleware import \
    EntityManagerMiddleware
from framefox.core.middleware.middlewares.custom_cors_middleware import \
    CustomCORSMiddleware
from framefox.core.middleware.middlewares.firewall_middleware import \
    FirewallMiddleware
from framefox.core.middleware.middlewares.request_middleware import \
    RequestMiddleware
from framefox.core.middleware.middlewares.session_middleware import \
    SessionMiddleware
EntityManagerMiddleware
"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestMiddlewareManager:
    @pytest.fixture
    def mock_app(self):
        app = Mock(spec=FastAPI)
        app.add_middleware = Mock()
        return app

    @pytest.fixture
    def mock_settings(self):
        return Mock(spec=Settings)

    @pytest.fixture
    def middleware_manager(self, mock_app, mock_settings):
        return MiddlewareManager(mock_app, mock_settings)

    def test_initialization(self, middleware_manager, mock_app, mock_settings):
        """Test the initialization of MiddlewareManager"""
        assert middleware_manager.app == mock_app
        assert middleware_manager.settings == mock_settings

    def test_setup_middlewares(self, middleware_manager, mock_app):
        """Test that all middlewares are correctly configured"""
        middleware_manager.setup_middlewares()

        # Verify that add_middleware was called for each middleware
        expected_calls = [
            ((RequestMiddleware,), {}),
            ((EntityManagerMiddleware,), {}),
            ((FirewallMiddleware,), {"settings": middleware_manager.settings}),
            ((SessionMiddleware,), {"settings": middleware_manager.settings}),
            ((CustomCORSMiddleware,), {"settings": middleware_manager.settings}),
        ]

        # Verify that the number of calls is correct
        assert mock_app.add_middleware.call_count == len(expected_calls)

        # Verify that each middleware was added with the correct parameters
        actual_calls = mock_app.add_middleware.call_args_list
        for expected, actual in zip(expected_calls, actual_calls):
            # Verify the middleware class
            assert actual[0][0] == expected[0][0]
            assert actual[1] == expected[1]  # Verify the parameters

    def test_middleware_order(self, middleware_manager, mock_app):
        """Test that the order of middlewares is correct"""
        middleware_manager.setup_middlewares()

        calls = mock_app.add_middleware.call_args_list

        # Verify the order of middlewares
        assert calls[0][0][0] == RequestMiddleware
        assert calls[1][0][0] == EntityManagerMiddleware
        assert calls[2][0][0] == FirewallMiddleware
        assert calls[3][0][0] == SessionMiddleware
        assert calls[4][0][0] == CustomCORSMiddleware

    @pytest.mark.parametrize(
        "middleware_class",
        [
            RequestMiddleware,
            EntityManagerMiddleware,
            FirewallMiddleware,
            SessionMiddleware,
            CustomCORSMiddleware,
        ],
    )
    def test_individual_middleware_addition(
        self, middleware_manager, mock_app, middleware_class
    ):
        """Test the addition of each middleware individually"""
        middleware_manager.setup_middlewares()

        # Verify that each middleware was added
        middleware_calls = [
            call[0][0] for call in mock_app.add_middleware.call_args_list
        ]
        assert middleware_class in middleware_calls
