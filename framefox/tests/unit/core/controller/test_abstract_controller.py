import pytest
from unittest.mock import Mock, patch
from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.request.session.session import Session
from framefox.core.di.service_container import ServiceContainer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TestController(AbstractController):
    pass


class TestAbstractController:
    @pytest.fixture
    def mock_container(self):

        container = ServiceContainer()
        template_renderer = Mock()
        template_renderer.render.return_value = "<html>Test</html>"

        container.get_by_name = Mock(return_value=template_renderer)

        with patch('framefox.core.di.service_container.ServiceContainer') as mock_class:
            mock_class._instance = container
            mock_class.return_value = container
            yield container

    @pytest.fixture
    def controller(self):
        return TestController()

    def test_get_container(self, controller, mock_container):
        container = controller._get_container()
        assert container is mock_container

    def test_redirect(self, controller):
        response = controller.redirect("/home")
        assert response.status_code == 302
        assert response.headers["location"] == "/home"

        response = controller.redirect("/login", 301)
        assert response.status_code == 301
        assert response.headers["location"] == "/login"

    def test_flash(self, controller):
        with patch.object(Session, 'get') as mock_get, \
                patch.object(Session, 'set') as mock_set:

            mock_get.return_value = []
            controller.flash("success", "Operation successful")

            mock_get.assert_called_once_with("flash_messages", [])
            mock_set.assert_called_once_with("flash_messages", [
                {"message": "Operation successful", "category": "success"}
            ])

    def test_json(self, controller):
        data = {"status": "success"}
        response = controller.json(data)
        assert response.status_code == 200
        assert response.body == b'{"status":"success"}'

        response = controller.json(data, 201)
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_render(self, controller, mock_container):
        with patch.object(Session, 'has') as mock_has, \
                patch.object(Session, 'get') as mock_get, \
                patch.object(Session, 'remove') as mock_remove:

            mock_has.return_value = True
            mock_get.return_value = [{"message": "Test", "category": "info"}]

            context = {"title": "Test Page"}
            response = controller.render("test.html", context)

            assert response.status_code == 200
            assert response.body == b"<html>Test</html>"
            assert response.media_type == "text/html"

            mock_container.get_by_name.assert_called_with("TemplateRenderer")
            mock_remove.assert_called_once_with("flash_messages")
