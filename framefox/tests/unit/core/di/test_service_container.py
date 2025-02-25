from unittest.mock import Mock, patch

import pytest

from framefox.core.di.service_container import ServiceContainer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TestService:
    pass


class DependentService:
    def __init__(self, test_service: TestService):
        self.test_service = test_service


class CircularService1:
    def __init__(self, service2: "CircularService2"):
        self.service2 = service2


class CircularService2:
    def __init__(self, service1: CircularService1):
        self.service1 = service1


class TestServiceContainer:
    @pytest.fixture
    def container(self):
        # Reset the singleton for each test
        ServiceContainer._instance = None
        with patch(
            "framefox.core.di.service_container.ServiceContainer.scan_and_register_services"
        ):
            return ServiceContainer()

    def test_singleton_pattern(self):
        container1 = ServiceContainer()
        container2 = ServiceContainer()
        assert container1 is container2

    def test_register_simple_service(self, container):
        service = container.register(TestService)
        assert isinstance(service, TestService)
        assert TestService in container.services

    def test_register_service_with_dependencies(self, container):
        # First register the service that DependentService depends on
        container.register(TestService)
        dependent_service = container.register(DependentService)

        assert isinstance(dependent_service, DependentService)
        assert isinstance(dependent_service.test_service, TestService)

    def test_get_existing_service(self, container):
        original_service = container.register(TestService)
        retrieved_service = container.get(TestService)
        assert original_service is retrieved_service

    def test_get_by_name(self, container):
        service = container.register(TestService)
        retrieved_service = container.get_by_name("TestService")
        assert service is retrieved_service

    def test_get_by_name_not_found(self, container):
        result = container.get_by_name("NonExistentService")
        assert result is None

    def test_get_by_tag(self, container):
        service = container.register(TestService, tags=["test.tag"])
        retrieved_service = container.get_by_tag("test.tag")
        assert service is retrieved_service

    def test_get_by_tag_multiple_services(self, container):
        container.register(TestService, tags=["shared.tag"])
        container.register(DependentService, tags=["shared.tag"])

        with pytest.raises(Exception) as exc_info:
            container.get_by_tag("shared.tag")
        assert "Multiple services found for tag" in str(exc_info.value)

    def test_get_all_by_tag(self, container):
        service1 = container.register(TestService, tags=["shared.tag"])
        service2 = container.register(DependentService, tags=["shared.tag"])

        services = container.get_all_by_tag("shared.tag")
        assert len(services) == 2
        assert service1 in services
        assert service2 in services

    def test_default_tag_generation(self, container):
        test_service = container.register(TestService)
        default_tag = container._get_default_tag(TestService)
        assert container.get_by_tag(default_tag) is test_service

    @patch("os.walk")
    @patch("importlib.import_module")
    def test_scan_and_register_services(self, mock_import, mock_walk, container):
        # Restore the original method
        container.scan_and_register_services = (
            ServiceContainer.scan_and_register_services.__get__(container)
        )

        mock_walk.return_value = [("/test/path", [], ["test_service.py"])]

        mock_module = Mock()
        mock_module.TestService = TestService
        mock_import.return_value = mock_module

        container.scan_and_register_services()

        assert mock_import.called
        assert TestService in container.services

    def test_print_container_stats(self, container, capsys):
        container.register(TestService)
        container.print_container_stats()

        captured = capsys.readouterr()
        assert "ServiceContainer Statistics:" in captured.out
        assert "TestService" in captured.out
