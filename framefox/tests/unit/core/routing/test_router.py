from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI

from framefox.core.routing.router import Router
from framefox.core.templates.template_renderer import TemplateRenderer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestRouter:
    @pytest.fixture
    def mock_app(self):
        """Fixture for FastAPI"""
        app = Mock(spec=FastAPI)
        app.routes = []
        app.include_router = Mock()
        app.add_api_route = Mock()
        return app

    @pytest.fixture
    def mock_settings(self):
        """Fixture for Settings"""
        settings = Mock()
        settings.app_env = "dev"
        return settings

    @pytest.fixture
    def mock_template_renderer(self):
        """Fixture for TemplateRenderer"""
        renderer = Mock(spec=TemplateRenderer)
        renderer.render.return_value = "<html>Test</html>"
        return renderer

    @pytest.fixture
    def router(self, mock_app, mock_settings, mock_template_renderer):
        """Fixture for Router"""
        # Patch the ServiceContainer class and its instance
        with patch("framefox.core.routing.router.ServiceContainer") as MockContainer:
            # Create a mock instance that inherits from ServiceContainer
            container = Mock()

            # Configure the necessary methods
            container.get_by_name = Mock(return_value=mock_settings)
            container.get = Mock(return_value=mock_template_renderer)

            # Configure the mock class
            MockContainer.return_value = container

            # Return the Router instance
            return Router(mock_app)

    def test_init(self, router, mock_app):
        """Test Router initialization"""
        assert router.app == mock_app
        assert isinstance(router._routes, dict)



    def test_url_path_for_existing_route(self, router):
        """Test URL generation for an existing route"""
        Router._routes = {"test_route": "/users/{id}/profile"}
        url = router.url_path_for("test_route", id=123)
        assert url == "/users/123/profile"

    def test_url_path_for_missing_route(self, router):
        """Test URL generation for a non-existent route"""
        url = router.url_path_for("nonexistent_route")
        assert url == "#"

    # def test_register_default_route(self, router, mock_app):
    #     """Test default route registration"""
    #     router.register_controller()
    #     mock_app.add_api_route.assert_called_with(
    #         "/",
    #         "",
    #         name="default_route",
    #         methods=["GET"],
    #     )
