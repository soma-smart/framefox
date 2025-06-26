from unittest.mock import Mock, patch

import pytest
from fastapi import Request

from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.di.service_container import ServiceContainer
from framefox.core.request.request_stack import RequestStack
from framefox.core.request.session.session import Session

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestController(AbstractController):
    pass


class TestAbstractController:
    @pytest.fixture(autouse=True)
    def setup_request_context(self):
        """Fixture to set up the request context"""
        request = Mock(spec=Request)
        RequestStack.set_request(request)
        yield
        RequestStack.set_request(None)

    @pytest.fixture
    def mock_session(self):
        """Fixture for the session"""
        session = Mock(spec=Session)
        session.get.return_value = []
        session.has.return_value = False
        return session

    @pytest.fixture
    def mock_template_renderer(self):
        """Fixture for the template renderer"""
        renderer = Mock()
        renderer.render.return_value = "<html>Test</html>"
        return renderer

    @pytest.fixture
    def mock_container(self, mock_session, mock_template_renderer):
        """Fixture for the container with dependencies"""
        container = Mock(spec=ServiceContainer)

        def get_by_name_side_effect(name):
            if name == "Session":
                return mock_session
            elif name == "TemplateRenderer":
                return mock_template_renderer
            return None

        container.get_by_name.side_effect = get_by_name_side_effect
        ServiceContainer._instance = container
        return container

    @pytest.fixture
    def controller(self, mock_container):
        """Fixture for the controller"""
        with patch(
            "framefox.core.controller.abstract_controller.ServiceContainer",
            return_value=mock_container,
        ):
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

    def test_json(self, controller):
        data = {"status": "success"}
        response = controller.json(data)
        assert response.status_code == 200
        assert response.body == b'{"status":"success"}'

        response = controller.json(data, 201)
        assert response.status_code == 201
