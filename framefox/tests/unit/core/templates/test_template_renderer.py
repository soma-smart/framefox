from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from jinja2 import Environment

from framefox.core.di.service_container import ServiceContainer
from framefox.core.templates.template_renderer import TemplateRenderer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TestTemplateRenderer:
    @pytest.fixture
    def mock_settings(self):
        """Fixture for settings"""
        settings = Mock()
        settings.template_dir = "/path/to/templates"
        return settings

    @pytest.fixture
    def mock_router(self):
        """Fixture for the router"""
        router = Mock()
        router.url_path_for.return_value = "/test-route"
        return router

    @pytest.fixture
    def mock_container(self, mock_settings, mock_router):
        """Fixture for the service container"""
        container = Mock(spec=ServiceContainer)

        def get_by_name_side_effect(name):
            if name == "Settings":
                return mock_settings
            elif name == "Router":
                return mock_router
            return None

        container.get_by_name.side_effect = get_by_name_side_effect
        ServiceContainer._instance = container
        return container

    @pytest.fixture
    def template_renderer(self, mock_container):
        """Fixture for the TemplateRenderer instance"""
        with patch("pathlib.Path") as mock_path:
            mock_path_instance = Mock()
            mock_path_instance.parent = Mock()
            framework_templates = Path("/path/to/framework/templates")

            # Correct configuration of the mock for the division operation
            mock_div = Mock()
            mock_div.return_value = framework_templates
            mock_path_instance.parent.__truediv__ = mock_div
            mock_path.return_value = mock_path_instance

            # Configuration of user_template_dir via mock_settings
            mock_container.get_by_name("Settings").template_dir = "/path/to/templates"

            renderer = TemplateRenderer()
            renderer.framework_template_dir = framework_templates
            renderer.user_template_dir = "/path/to/templates"

            return renderer

    def test_init_environment(self, template_renderer):
        """Test the initialization of the Jinja2 environment"""
        assert isinstance(template_renderer.env, Environment)
        assert "url_for" in template_renderer.env.globals

    def test_url_for_success(self, template_renderer, mock_router):
        """Test successful URL generation"""
        url = template_renderer._url_for("test-route", param="value")
        assert url == "/test-route"
        mock_router.url_path_for.assert_called_once_with("test-route", param="value")

    def test_url_for_error(self, template_renderer, mock_router):
        """Test error handling in url_for"""
        mock_router.url_path_for.side_effect = Exception("Route not found")
        url = template_renderer._url_for("invalid-route")
        assert url == "#"

    def test_render_template(self, template_renderer):
        """Test template rendering"""
        with patch.object(template_renderer.env, "get_template") as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "<html>Test Content</html>"
            mock_get_template.return_value = mock_template

            context = {"title": "Test Page"}
            result = template_renderer.render("test.html", context)

            assert result == "<html>Test Content</html>"
            mock_get_template.assert_called_once_with("test.html")
            mock_template.render.assert_called_once_with(**context)

    def test_render_template_with_empty_context(self, template_renderer):
        """Test template rendering without context"""
        with patch.object(template_renderer.env, "get_template") as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "<html>Empty Context</html>"
            mock_get_template.return_value = mock_template

            result = template_renderer.render("empty.html")

            assert result == "<html>Empty Context</html>"
            mock_get_template.assert_called_once_with("empty.html")
            mock_template.render.assert_called_once_with()
